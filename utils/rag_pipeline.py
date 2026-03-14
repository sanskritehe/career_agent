"""
rag_pipeline.py
---------------
RAG pipeline for Career AI Assistant.

Dataset fields (NxtGenIntern/job_titles_and_descriptions):
  'Job Title', 'Skills', 'Job Description'   ← capital letters + spaces
"""

import chromadb
from sentence_transformers import SentenceTransformer

_chroma_client = chromadb.PersistentClient(path="./chroma_db")
_jd_collection = _chroma_client.get_or_create_collection(
    name="job_descriptions",
    metadata={"hnsw:space": "cosine"},
)

_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# ── Indexing ──────────────────────────────────────────────────────────────────

def index_job_descriptions(force_reindex: bool = False) -> int:
    global _jd_collection
    existing = _jd_collection.count()
    if existing > 0 and not force_reindex:
        print(f"[RAG] Already indexed {existing} documents. Skipping.")
        return existing

    if force_reindex and existing > 0:
        print(f"[RAG] Force re-indexing. Clearing {existing} docs.")
        
        _chroma_client.delete_collection("job_descriptions")
        _jd_collection = _chroma_client.get_or_create_collection(
            name="job_descriptions",
            metadata={"hnsw:space": "cosine"},
        )

    print("[RAG] Loading HuggingFace dataset for indexing...")
    try:
        from datasets import load_dataset
        ds = load_dataset("NxtGenIntern/job_titles_and_descriptions", split="train")
    except Exception as e:
        print(f"[RAG] Could not load dataset: {e}")
        return 0

    print(f"[RAG] Dataset columns: {ds.column_names}")  # confirm field names

    model = _get_model()
    ids, embeddings, documents, metadatas = [], [], [], []

    for i, row in enumerate(ds):
        # ✅ Correct field names with spaces and capitals
        title  = (row.get("Job Title", "") or "").strip()
        skills = (row.get("Skills", "") or "").strip()
        desc   = (row.get("Job Description", "") or "").strip()

        if not title:
            continue

        document  = f"Job Title: {title}\nRequired Skills: {skills}\nDescription: {desc}"
        embedding = model.encode(document).tolist()

        ids.append(f"jd_{i}")
        embeddings.append(embedding)
        documents.append(document)
        metadatas.append({
            "job_title": title,
            "skills":    skills[:500],
        })

        # Batch upsert every 100 docs
        if len(ids) == 100:
            _jd_collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            ids, embeddings, documents, metadatas = [], [], [], []

    # Upsert remaining
    if ids:
        _jd_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    total = _jd_collection.count()
    print(f"[RAG] Successfully indexed {total} job descriptions.")
    return total


# ── Retrieval ─────────────────────────────────────────────────────────────────

def retrieve_relevant_jds(query: str, top_k: int = 3) -> list[dict]:
    if _jd_collection.count() == 0:
        print("[RAG] Collection empty. Triggering auto-index...")
        indexed = index_job_descriptions()
        if indexed == 0:
            return []

    model     = _get_model()
    query_vec = model.encode(query).tolist()

    results = _jd_collection.query(
        query_embeddings=[query_vec],
        n_results=min(top_k, _jd_collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    docs      = results.get("documents", [[]])[0]
    metas     = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        retrieved.append({
            "job_title": meta.get("job_title", "Unknown"),
            "skills":    meta.get("skills", ""),
            "document":  doc,
            "distance":  round(dist, 4),
        })

    return retrieved


# ── Augmentation ──────────────────────────────────────────────────────────────

def build_rag_context(target_role: str, candidate_skills: list[str], top_k: int = 3) -> str:
    query = f"{target_role} {' '.join(candidate_skills)}"
    jds   = retrieve_relevant_jds(query, top_k=top_k)

    if not jds:
        return "No relevant job descriptions found in the knowledge base."

    lines = ["=== RETRIEVED JOB DESCRIPTIONS (RAG Context) ==="]
    for i, jd in enumerate(jds, 1):
        lines.append(f"\n[JD {i}] Role: {jd['job_title']}")
        lines.append(f"Required Skills: {jd['skills']}")
        desc_part = jd["document"].split("Description:")[-1].strip()[:400]
        lines.append(f"Description: {desc_part}")
        lines.append(f"Relevance Distance: {jd['distance']}")
    lines.append("\n=== END OF RAG CONTEXT ===")

    return "\n".join(lines)


# ── Status ────────────────────────────────────────────────────────────────────

def get_index_status() -> dict:
    count = _jd_collection.count()
    return {
        "indexed_documents": count,
        "is_ready":          count > 0,
        "collection_name":   "job_descriptions",
        "db_path":           "./chroma_db",
    }
