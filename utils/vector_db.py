import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_db")
model = SentenceTransformer('all-MiniLM-L6-v2')
collection = client.get_or_create_collection(name="job_roles")

def add_jobs_to_db(jobs_list):
    # Fix: Prevent duplicates by checking if the collection is already populated
    if collection.count() > 0:
        return 

    for i, job in enumerate(jobs_list):
        text_content = f"Role: {job['role']}. Required Skills: {', '.join(job['skills'])}"
        embedding = model.encode(text_content).tolist()
        
        collection.add(
            ids=[f"job_{i}"],
            embeddings=[embedding],
            metadatas=[{"role": job['role']}],
            documents=[text_content]
        )

def search_jobs(resume_summary, n_results=5):
    query_embedding = model.encode(resume_summary).tolist()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )