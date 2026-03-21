import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from agents.dsa import (
    get_all_topics,
    progress_tracker,
    get_topic_problems,
    get_topic_info,
    generate_daily_schedule,
    get_easy_problems,
    get_medium_problems,
    generate_problem_explanation,
    TIME_PLAN_CONFIGS,
)
from agents.dsa.dsa_tutor_agent import generate_hint, evaluate_readiness

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
DSA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&family=Bebas+Neue&display=swap');

:root {
  --bg:#0d0f14;--surface:#13161e;--border:#1f2333;
  --accent:#7c6af7;--accent2:#4af0c4;
  --easy:#22c55e;--medium:#f59e0b;--hard:#ef4444;
  --text:#e2e8f0;--muted:#64748b;--card:#161a26;
  --glow:rgba(124,106,247,0.18);
}
html,body,[class*="css"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:2rem 2.5rem 4rem!important;max-width:1200px;}
.dsa-hero{background:linear-gradient(135deg,#0d0f14,#181b2e 60%,#1a1230);border:1px solid var(--border);border-radius:20px;padding:3rem 3rem 2.5rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.dsa-hero::before{content:'';position:absolute;top:-80px;right:-80px;width:320px;height:320px;background:radial-gradient(circle,rgba(124,106,247,.22),transparent 70%);border-radius:50%;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:3.6rem;letter-spacing:3px;background:linear-gradient(90deg,#fff,#c4b9ff 50%,var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 .4rem;line-height:1;}
.hero-sub{font-size:1.05rem;color:var(--muted);font-weight:300;letter-spacing:.5px;margin:0;}
.hero-badge{display:inline-block;background:rgba(124,106,247,.15);border:1px solid rgba(124,106,247,.35);color:#c4b9ff;font-family:'Space Mono',monospace;font-size:.72rem;padding:4px 12px;border-radius:20px;margin-bottom:1rem;letter-spacing:1px;}
.streak-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.35);border-radius:10px;padding:6px 16px;font-family:'Space Mono',monospace;font-size:.88rem;color:#fbbf24;}
.metric-row{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;}
.metric-card{flex:1;min-width:130px;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.25rem 1.5rem;position:relative;overflow:hidden;transition:border-color .25s;}
.metric-card:hover{border-color:var(--accent);}
.metric-card::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:14px 14px 0 0;}
.metric-label{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;font-family:'Space Mono',monospace;margin-bottom:.4rem;}
.metric-value{font-family:'Bebas Neue',sans-serif;font-size:2.2rem;letter-spacing:1px;color:#fff;line-height:1;}
.metric-unit{font-size:.85rem;color:var(--muted);margin-top:.2rem;}
.plan-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.8rem;transition:all .25s;position:relative;overflow:hidden;}
.plan-card:hover{border-color:var(--accent);transform:translateY(-3px);box-shadow:0 8px 32px var(--glow);}
.plan-card.active{border-color:var(--accent);background:linear-gradient(135deg,#161a26,#1a1535);box-shadow:0 4px 24px var(--glow);}
.plan-card.active::before{content:'checkmark ACTIVE';position:absolute;top:14px;right:14px;font-family:'Space Mono',monospace;font-size:.65rem;color:var(--accent2);background:rgba(74,240,196,.12);border:1px solid rgba(74,240,196,.3);padding:3px 9px;border-radius:10px;letter-spacing:1px;}
.plan-icon{font-size:2rem;margin-bottom:.8rem;}
.plan-title{font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:2px;color:#fff;margin:0 0 .3rem;}
.plan-pace{font-size:.78rem;font-family:'Space Mono',monospace;color:var(--accent2);margin-bottom:1rem;}
.plan-stat{display:flex;justify-content:space-between;margin:.4rem 0;font-size:.9rem;color:var(--muted);}
.plan-stat span{color:var(--text);font-weight:500;}
.problem-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.6rem;margin-bottom:1rem;transition:border-color .2s;}
.problem-card:hover{border-color:var(--accent);}
.problem-card.done{border-color:rgba(34,197,94,.4);background:linear-gradient(135deg,var(--card),rgba(34,197,94,.04));}
.diff-badge{display:inline-block;font-family:'Space Mono',monospace;font-size:.68rem;letter-spacing:1px;padding:3px 10px;border-radius:20px;font-weight:700;margin-bottom:.8rem;}
.diff-easy{background:rgba(34,197,94,.15);color:var(--easy);border:1px solid rgba(34,197,94,.3);}
.diff-medium{background:rgba(245,158,11,.15);color:var(--medium);border:1px solid rgba(245,158,11,.3);}
.diff-hard{background:rgba(239,68,68,.15);color:var(--hard);border:1px solid rgba(239,68,68,.3);}
.problem-name{font-size:1.1rem;font-weight:600;color:#fff;margin-bottom:.4rem;}
.problem-meta{font-size:.82rem;color:var(--muted);margin-bottom:1rem;font-family:'Space Mono',monospace;}
.lc-link{display:inline-flex;align-items:center;gap:6px;background:rgba(124,106,247,.12);border:1px solid rgba(124,106,247,.3);color:#c4b9ff;text-decoration:none;padding:7px 16px;border-radius:8px;font-size:.82rem;font-family:'Space Mono',monospace;transition:all .2s;}
.lc-link:hover{background:rgba(124,106,247,.22);border-color:var(--accent);color:#fff;}
.prog-track{background:rgba(255,255,255,.06);border-radius:99px;height:6px;overflow:hidden;margin:.4rem 0 1rem;}
.prog-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:99px;transition:width .6s ease;}
.diff-stat-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:1.5rem;text-align:center;}
.diff-stat-num{font-family:'Bebas Neue',sans-serif;font-size:2.4rem;line-height:1;margin-bottom:.3rem;}
.diff-stat-label{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;font-family:'Space Mono',monospace;}
.diff-stat-pct{font-size:.88rem;margin-top:.3rem;font-weight:500;}
.section-header{display:flex;align-items:center;gap:12px;margin:2rem 0 1.2rem;padding-bottom:.8rem;border-bottom:1px solid var(--border);}
.section-header-icon{width:36px;height:36px;background:rgba(124,106,247,.15);border:1px solid rgba(124,106,247,.3);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;}
.section-title{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:2px;color:#fff;margin:0;}
.day-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(124,106,247,.12);border:1px solid rgba(124,106,247,.3);border-radius:10px;padding:8px 18px;font-family:'Space Mono',monospace;font-size:.9rem;color:#c4b9ff;margin-bottom:1.5rem;}
.hint-box{background:rgba(74,240,196,.06);border:1px solid rgba(74,240,196,.25);border-radius:14px;padding:1.4rem 1.6rem;margin-top:1rem;}
.hint-title{font-family:'Space Mono',monospace;font-size:.75rem;color:var(--accent2);letter-spacing:1px;text-transform:uppercase;margin-bottom:.6rem;}
.hint-text{color:var(--text);font-size:.95rem;line-height:1.6;}
.hint-encouragement{margin-top:.8rem;font-size:.85rem;color:var(--muted);font-style:italic;}
.explanation-section{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.5rem;margin-top:.8rem;}
.explanation-label{font-family:'Space Mono',monospace;font-size:.72rem;color:var(--accent);letter-spacing:1px;text-transform:uppercase;margin-bottom:.5rem;}
.search-result{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:1rem 1.3rem;margin-bottom:.5rem;display:flex;justify-content:space-between;align-items:center;transition:border-color .2s;}
.search-result:hover{border-color:var(--accent);}
.readiness-score{font-family:'Bebas Neue',sans-serif;font-size:5rem;letter-spacing:3px;line-height:1;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:12px!important;padding:4px!important;gap:4px!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:9px!important;font-family:'Space Mono',monospace!important;font-size:.8rem!important;letter-spacing:.5px!important;}
.stTabs [aria-selected="true"]{background:rgba(124,106,247,.2)!important;color:#c4b9ff!important;}
.stButton>button{background:rgba(124,106,247,.12)!important;border:1px solid rgba(124,106,247,.3)!important;color:#c4b9ff!important;border-radius:10px!important;font-family:'Space Mono',monospace!important;font-size:.82rem!important;letter-spacing:.5px!important;transition:all .2s!important;font-weight:600!important;}
.stButton>button:hover{background:rgba(124,106,247,.22)!important;border-color:var(--accent)!important;color:#fff!important;transform:translateY(-1px)!important;box-shadow:0 4px 16px var(--glow)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:10px!important;}
.stSelectbox>div>div{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:10px!important;}
.stAlert{background:rgba(124,106,247,.08)!important;border:1px solid rgba(124,106,247,.25)!important;border-radius:12px!important;color:var(--text)!important;}
hr{border-color:var(--border)!important;margin:1.5rem 0!important;}
.stSlider>div>div>div>div{background:var(--accent)!important;}
</style>
"""


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _diff_badge(difficulty: str) -> str:
    css = {"Easy": "diff-easy", "Medium": "diff-medium", "Hard": "diff-hard"}.get(difficulty, "diff-easy")
    sym = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "")
    return f'<span class="diff-badge {css}">{sym} {difficulty.upper()}</span>'


def _lc_slug(link: str) -> str:
    return link.rstrip("/").split("/")[-1]


def _section(icon: str, title: str):
    st.markdown(f"""
    <div class="section-header">
      <div class="section-header-icon">{icon}</div>
      <h2 class="section-title">{title}</h2>
    </div>""", unsafe_allow_html=True)


def _prog_bar(pct: int, color: str = "linear-gradient(90deg,var(--accent),var(--accent2))") -> str:
    return f'<div class="prog-track"><div class="prog-fill" style="width:{pct}%;background:{color};"></div></div>'


# ─────────────────────────────────────────────
#  MAIN ENTRY
# ─────────────────────────────────────────────

def render_dsa_tutor():
    st.markdown(DSA_CSS, unsafe_allow_html=True)

    overall = progress_tracker.get_all_progress()
    streak  = overall.get("streak", {})

    st.markdown(f"""
    <div class="dsa-hero">
      <div class="hero-badge">// DATA STRUCTURES &amp; ALGORITHMS</div>
      <h1 class="hero-title">DSA Learning<br>Command Center</h1>
      <p class="hero-sub">Structured prep &nbsp;·&nbsp; Daily challenges &nbsp;·&nbsp; AI-powered hints &nbsp;·&nbsp; Real-time tracking</p>
      <div style="margin-top:1.2rem;">
        <span class="streak-badge">&#128293; {streak.get('current',0)}-day streak &nbsp;&middot;&nbsp; &#127942; Best: {streak.get('longest',0)} days</span>
      </div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "  📋  ROADMAP  ",
        "  🎯  DAILY CHALLENGE  ",
        "  📚  TOPIC EXPLORER  ",
        "  🔍  SEARCH &amp; EVALUATE  ",
    ])

    with tab1:
        render_roadmap_selector()
    with tab2:
        render_daily_challenge()
    with tab3:
        render_topic_explorer()
    with tab4:
        render_search_and_evaluate()


# ─────────────────────────────────────────────
#  TAB 1 — ROADMAP
# ─────────────────────────────────────────────

def render_roadmap_selector():
    _section("🗺️", "CHOOSE YOUR PLAN")
    st.markdown('<p style="color:var(--muted);font-size:.9rem;margin-bottom:1.5rem;">Each plan delivers 1 Easy + 1 Medium problem per day.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    plan_3 = st.session_state.get("selected_plan") == "3_months"
    plan_6 = st.session_state.get("selected_plan") == "6_months"

    with col1:
        st.markdown(f"""
        <div class="plan-card{'  active' if plan_3 else ''}">
          <div class="plan-icon">&#9889;</div>
          <div class="plan-title">3-MONTH SPRINT</div>
          <div class="plan-pace">INTENSIVE PACE</div>
          <div class="plan-stat">Duration <span>90 days</span></div>
          <div class="plan-stat">Daily <span>1 Easy + 1 Medium</span></div>
          <div class="plan-stat">Total problems <span>180</span></div>
          <div class="plan-stat">Best for <span>Focused interview prep</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select 3-Month Plan", key="3month", use_container_width=True):
            st.session_state.selected_plan = "3_months"
            st.rerun()

    with col2:
        st.markdown(f"""
        <div class="plan-card{'  active' if plan_6 else ''}">
          <div class="plan-icon">&#129504;</div>
          <div class="plan-title">6-MONTH DEEP DIVE</div>
          <div class="plan-pace">MODERATE PACE</div>
          <div class="plan-stat">Duration <span>180 days</span></div>
          <div class="plan-stat">Daily <span>1 Easy + 1 Medium</span></div>
          <div class="plan-stat">Total problems <span>360 (cycling)</span></div>
          <div class="plan-stat">Best for <span>Learning + retention</span></div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select 6-Month Plan", key="6month", use_container_width=True):
            st.session_state.selected_plan = "6_months"
            st.rerun()

    if not st.session_state.get("selected_plan"):
        return

    plan   = st.session_state.selected_plan
    months = int(plan.split("_")[0])

    _section("📅", f"WEEKLY BREAKDOWN — {months}-MONTH PLAN")
    daily_schedule = generate_daily_schedule(months)
    if not daily_schedule:
        return

    weeks_topics: dict = {}
    for da in daily_schedule:
        week = (da["day"] - 1) // 7 + 1
        weeks_topics.setdefault(week, set())
        for k in ("easy_topic", "medium_topic"):
            if da.get(k) not in (None, "N/A"):
                weeks_topics[week].add(da[k])

    for wn in sorted(weeks_topics):
        topics = sorted(weeks_topics[wn])
        sd     = (wn - 1) * 7 + 1
        ed     = min(wn * 7, len(daily_schedule))
        with st.expander(f"Week {wn}  ·  Days {sd}–{ed}  ·  {', '.join(topics)}", expanded=False):
            rows = [{"Day": f"Day {d}",
                     "Easy Topic":   daily_schedule[d-1].get("easy_topic","N/A"),
                     "Medium Topic": daily_schedule[d-1].get("medium_topic","N/A")}
                    for d in range(sd, ed+1) if d <= len(daily_schedule)]
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                             column_config={
                                 "Day":          st.column_config.TextColumn("DAY", width="small"),
                                 "Easy Topic":   st.column_config.TextColumn("🟢 EASY TOPIC"),
                                 "Medium Topic": st.column_config.TextColumn("🟡 MEDIUM TOPIC"),
                             })


# ─────────────────────────────────────────────
#  TAB 2 — DAILY CHALLENGE
# ─────────────────────────────────────────────

def render_daily_challenge():
    if not st.session_state.get("selected_plan"):
        st.markdown("""
        <div style="background:rgba(124,106,247,.08);border:1px dashed rgba(124,106,247,.35);border-radius:16px;padding:2.5rem;text-align:center;margin-top:1rem;">
          <div style="font-size:2.5rem;margin-bottom:.8rem;">&#128507;</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;letter-spacing:2px;color:#c4b9ff;margin-bottom:.5rem;">SELECT A PLAN FIRST</div>
          <div style="color:var(--muted);font-size:.9rem;">Go to the <strong style="color:#c4b9ff;">Roadmap</strong> tab to pick your plan.</div>
        </div>""", unsafe_allow_html=True)
        return

    plan           = st.session_state.selected_plan
    months         = int(plan.split("_")[0])
    daily_schedule = generate_daily_schedule(months)

    if not daily_schedule:
        st.error("Failed to generate daily schedule.")
        return

    total_days = len(daily_schedule)
    st.session_state.setdefault("current_day", 1)

    overall     = progress_tracker.get_all_progress()
    prog_pct    = overall["overall_completion"]
    completed   = overall["completed_problems"]
    total_probs = overall["total_problems"]
    streak      = overall.get("streak", {})

    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card"><div class="metric-label">Plan</div><div class="metric-value">{months}MO</div><div class="metric-unit">{total_days} days</div></div>
      <div class="metric-card"><div class="metric-label">Solved</div><div class="metric-value">{completed}</div><div class="metric-unit">of {total_probs}</div></div>
      <div class="metric-card"><div class="metric-label">Completion</div><div class="metric-value">{prog_pct}%</div><div class="metric-unit">overall</div></div>
      <div class="metric-card"><div class="metric-label">Streak</div><div class="metric-value">{streak.get('current',0)}</div><div class="metric-unit">&#128293; days</div></div>
      <div class="metric-card"><div class="metric-label">Remaining</div><div class="metric-value">{total_probs - completed}</div><div class="metric-unit">problems left</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown(_prog_bar(prog_pct), unsafe_allow_html=True)

    _section("🎯", "TODAY'S CHALLENGE")
    selected_day = st.slider("Select a Day", 1, total_days,
                              st.session_state.current_day, key="day_slider")
    st.session_state.current_day = selected_day

    da       = daily_schedule[selected_day - 1]
    week_num = (selected_day - 1) // 7 + 1
    ws       = (week_num - 1) * 7 + 1
    we       = min(ws + 6, total_days)

    st.markdown(f"""
    <div class="day-badge">
      &#128197; Day {selected_day} / {total_days} &nbsp;&middot;&nbsp;
      Week {week_num} (Days {ws}&#8211;{we}) &nbsp;&middot;&nbsp;
      {total_days - selected_day} days remaining
    </div>""", unsafe_allow_html=True)

    ecol, mcol = st.columns(2, gap="large")
    with ecol:
        _render_problem_column(da, "easy",   selected_day)
    with mcol:
        _render_problem_column(da, "medium", selected_day)

    st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
    nc1, nc2, nc3 = st.columns([1, 2, 1])
    with nc1:
        if st.button("← Previous Day", use_container_width=True, disabled=(selected_day <= 1)):
            st.session_state.current_day = selected_day - 1
            st.rerun()
    with nc2:
        pct2 = round(selected_day / total_days * 100)
        st.markdown(f'<div style="text-align:center;padding:.7rem 0;font-family:\'Space Mono\',monospace;font-size:.8rem;color:var(--muted);">DAY {selected_day} / {total_days} &middot; {pct2}% THROUGH PLAN</div>', unsafe_allow_html=True)
    with nc3:
        if st.button("Next Day →", use_container_width=True, disabled=(selected_day >= total_days)):
            st.session_state.current_day = selected_day + 1
            st.rerun()

    _section("📊", "PROGRESS OVERVIEW")
    _render_progress_charts(completed, total_probs, prog_pct)


def _render_problem_column(da: dict, kind: str, selected_day: int):
    problem = da.get(f"{kind}_problem")
    topic   = da.get(f"{kind}_topic", "N/A")
    label   = "Easy" if kind == "easy" else "Medium"

    if not problem:
        return

    prob_id = problem["id"]
    tp      = progress_tracker.get_topic_progress(topic)
    # Avoid prechecking anything unless progress tracker marks it completed
    is_done = tp["problems"].get(prob_id, {}).get("completed", False) if tp else False
    s_notes = tp["problems"].get(prob_id, {}).get("notes", "") if tp else ""
    s_time  = tp["problems"].get(prob_id, {}).get("time_spent_mins", 0) if tp else 0
    slug    = _lc_slug(problem["leetcode_link"])

    st.markdown(f"""
    <div class="{'problem-card done' if is_done else 'problem-card'}">
      {_diff_badge(label)}
      <div class="problem-name">#{problem['id']} &middot; {problem['name']}</div>
      <div class="problem-meta">&#9201; Est. {problem['time_estimate_mins']} mins &nbsp;|&nbsp; &#127991; {topic}</div>
      <a class="lc-link" href="https://leetcode.com/problems/{slug}/" target="_blank">&#8594; Open on LeetCode</a>
    </div>""", unsafe_allow_html=True)

    new_done = st.checkbox(f"Mark {label} as Completed", value=is_done,
                            key=f"{kind}_complete_{selected_day}")
    if new_done != is_done:
        if new_done:
            progress_tracker.mark_problem_completed(topic, prob_id)
        else:
            progress_tracker.mark_problem_incomplete(topic, prob_id)
        st.rerun()

    with st.expander(f"📝 Notes — #{problem['id']}", expanded=False):
        notes_val = st.text_area("Notes / approach", value=s_notes,
                                  placeholder="Write your approach, key insights, edge cases…",
                                  key=f"{kind}_notes_{selected_day}_{prob_id}")
        if st.button("Save Notes", key=f"{kind}_save_{selected_day}_{prob_id}"):
            progress_tracker.update_problem_notes(topic, prob_id, notes_val)
            st.success("Saved!")

    with st.expander(f"🔬 Full AI Explanation — #{problem['id']}", expanded=False):
        if st.button("Generate Full Explanation 🤖", key=f"{kind}_explain_{selected_day}_{prob_id}"):
            with st.spinner("Generating explanation…"):
                res = generate_problem_explanation(problem["id"], problem["name"], label)
            _render_explanation(res)


def _render_explanation(data: dict):
    if "error" in data:
        st.error(f"Explanation error: {data['error']}")
        return

    st.markdown(f"""
    <div class="explanation-section">
      <div class="explanation-label">Problem Understanding</div>
      <p>{data.get('problem_understanding','')}</p>
    </div>""", unsafe_allow_html=True)

    approach = data.get("approach", {})
    if approach:
        st.markdown(f"""
        <div class="explanation-section">
          <div class="explanation-label">Approach — {approach.get('algorithm_name','')}</div>
          <p>{approach.get('strategy','')}</p>
        </div>""", unsafe_allow_html=True)
        for i, step in enumerate(approach.get("steps", []), 1):
            st.markdown(f"**{i}.** {step}")

    code = data.get("solution_code", {})
    if code.get("code"):
        st.markdown("**Solution**")
        st.code(code["code"], language=code.get("language", "python"))

    cx = data.get("complexity_analysis", {})
    if cx:
        c1, c2 = st.columns(2)
        c1.metric("Time", cx.get("time_complexity", "—"))
        c2.metric("Space", cx.get("space_complexity", "—"))
        st.caption(cx.get("explanation", ""))

    if data.get("key_insights"):
        st.markdown("**Key Insights**")
        for ins in data["key_insights"]:
            st.markdown(f"- {ins}")


def _render_progress_charts(completed: int, total: int, pct: int):
    cc, sc = st.columns([3, 2], gap="large")

    with cc:
        fig = go.Figure(data=[go.Pie(
            labels=["Solved", "Remaining"],
            values=[completed, total - completed],
            hole=0.72,
            marker=dict(colors=["#7c6af7", "#1f2333"],
                        line=dict(color="#0d0f14", width=2)),
            textposition="none",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )])
        fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.55,
                           font=dict(size=28, color="#fff", family="Bebas Neue"),
                           showarrow=False)
        fig.add_annotation(text="SOLVED", x=0.5, y=0.38,
                           font=dict(size=11, color="#64748b", family="Space Mono"),
                           showarrow=False)
        fig.update_layout(height=280, showlegend=False,
                          margin=dict(t=10, b=10, l=10, r=10),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with sc:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:1rem;padding-top:1rem;">
          <div><div class="metric-label">Total Solved</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:#fff;line-height:1;">{completed}<span style="font-size:1rem;color:var(--muted);"> / {total}</span></div></div>
          <div><div class="metric-label">Remaining</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:2.2rem;color:var(--accent);line-height:1;">{total-completed}</div></div>
        </div>""", unsafe_allow_html=True)

    _section("💪", "DIFFICULTY BREAKDOWN")
    dp = progress_tracker.get_progress_by_difficulty()
    dc1, dc2, dc3 = st.columns(3, gap="medium")

    for col, diff, key, color, rgba in [
        (dc1, "EASY",   "easy",   "var(--easy)",   "34,197,94"),
        (dc2, "MEDIUM", "medium", "var(--medium)", "245,158,11"),
        (dc3, "HARD",   "hard",   "var(--hard)",   "239,68,68"),
    ]:
        d = dp[key]
        with col:
            st.markdown(f"""
            <div class="diff-stat-card" style="border-color:rgba({rgba},.25);">
              <div class="diff-badge diff-{key}" style="margin-bottom:.8rem;">{diff}</div>
              <div class="diff-stat-num" style="color:{color};">{d['completed']}<span style="font-size:1.1rem;color:var(--muted);">/{d['total']}</span></div>
              <div class="diff-stat-label">problems solved</div>
              <div class="diff-stat-pct" style="color:{color};">{d['percentage']}%</div>
              {_prog_bar(d['percentage'], color)}
            </div>""", unsafe_allow_html=True)

    _section("📆", "ACTIVITY — LAST 90 DAYS")
    hd = progress_tracker.get_activity_heatmap_data(90)
    dates  = [x["date"]  for x in hd]
    counts = [x["count"] for x in hd]
    max_c  = max(counts) if any(counts) else 1

    fig2 = go.Figure(go.Bar(
        x=dates, y=counts,
        marker=dict(color=counts,
                    colorscale=[[0, "#1f2333"], [0.01, "#2d1f7a"], [1, "#7c6af7"]],
                    cmin=0, cmax=max_c),
    ))
    fig2.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       xaxis=dict(showgrid=False, color="#64748b", tickfont=dict(size=9)),
                       yaxis=dict(showgrid=False, color="#64748b", tickfont=dict(size=9)))
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  TAB 3 — TOPIC EXPLORER
# ─────────────────────────────────────────────

def render_topic_explorer():
    _section("📚", "TOPIC EXPLORER")

    diff_filter = st.selectbox("Filter by difficulty", ["All", "Easy", "Medium", "Hard"],
                                key="topic_diff_filter")

    for topic_name in get_all_topics():
        all_probs = get_topic_problems(topic_name)
        probs = all_probs if diff_filter == "All" else [p for p in all_probs if p["difficulty"] == diff_filter]
        info  = get_topic_info(topic_name)
        tp    = progress_tracker.get_topic_progress(topic_name)
        done  = tp["completed_problems"] if tp else 0
        total = tp["total_problems"]     if tp else len(all_probs)
        pct   = tp["completion_percentage"] if tp else 0

        if diff_filter != "All" and not probs:
            continue

        with st.expander(f"{topic_name}  ·  {done}/{total} solved  ·  {pct}%", expanded=False):
            st.markdown(f'<p style="color:var(--muted);font-size:.9rem;">{info["description"]}</p>', unsafe_allow_html=True)
            st.markdown(_prog_bar(pct), unsafe_allow_html=True)

            rows = []
            for p in probs:
                p_done  = tp["problems"].get(p["id"], {}).get("completed", False) if tp else False
                p_time  = tp["problems"].get(p["id"], {}).get("time_spent_mins", 0) if tp else 0
                p_notes = tp["problems"].get(p["id"], {}).get("notes", "") if tp else ""
                rows.append({
                    "Done":       "✓" if p_done else "○",
                    "ID":         p["id"],
                    "Problem":    p["name"],
                    "Difficulty": p["difficulty"],
                    "Est (min)":  p["time_estimate_mins"],
                    "Spent (min)": p_time or "—",
                    "Notes":      (p_notes[:50] + "…") if len(p_notes) > 50 else p_notes,
                    "Tags":       ", ".join(p.get("tags", [])),
                })

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                         column_config={
                             "Done":       st.column_config.TextColumn("✅", width="small"),
                             "ID":         st.column_config.TextColumn("ID", width="small"),
                             "Problem":    st.column_config.TextColumn("Problem"),
                             "Difficulty": st.column_config.TextColumn("Diff", width="small"),
                             "Est (min)":  st.column_config.NumberColumn("Est.", width="small"),
                             "Spent (min)":st.column_config.TextColumn("Spent", width="small"),
                             "Notes":      st.column_config.TextColumn("Notes"),
                             "Tags":       st.column_config.TextColumn("Tags"),
                         })

            mc1, mc2 = st.columns(2)
            with mc1:
                if st.button(f"✅ Mark All Complete", key=f"mark_all_{topic_name}"):
                    for p in probs:
                        progress_tracker.mark_problem_completed(topic_name, p["id"])
                    st.rerun()
            with mc2:
                if st.button(f"↩ Reset Topic", key=f"reset_{topic_name}"):
                    for p in probs:
                        progress_tracker.mark_problem_incomplete(topic_name, p["id"])
                    st.rerun()


# ─────────────────────────────────────────────
#  TAB 4 — SEARCH & EVALUATE
# ─────────────────────────────────────────────

def render_search_and_evaluate():
    _section("🔍", "PROBLEM SEARCH")
    query = st.text_input("Search by problem name or topic",
                           placeholder="e.g. binary search, two sum, graph…")

    if query:
        results = progress_tracker.search_problems(query)
        if not results:
            st.info("No problems found. Try a different query.")
        else:
            st.markdown(f'<p style="color:var(--muted);font-size:.88rem;margin-bottom:.8rem;">{len(results)} result(s)</p>', unsafe_allow_html=True)
            for r in results:
                done_icon = "✓" if r["completed"] else "○"
                color = {"Easy": "var(--easy)", "Medium": "var(--medium)", "Hard": "var(--hard)"}.get(r["difficulty"], "#fff")
                slug  = _lc_slug(r.get("leetcode_link", ""))
                st.markdown(f"""
                <div class="search-result">
                  <div>
                    <span style="color:{color};font-weight:700;font-size:.8rem;font-family:'Space Mono',monospace;">{done_icon} {r['difficulty'].upper()}</span>
                    &nbsp;&nbsp;
                    <span style="color:#fff;font-weight:600;">#{r['id']} {r['name']}</span>
                    &nbsp;&nbsp;
                    <span style="color:var(--muted);font-size:.85rem;">{r['topic']}</span>
                  </div>
                  <a class="lc-link" href="https://leetcode.com/problems/{slug}/" target="_blank" style="font-size:.75rem;">&#8594; LeetCode</a>
                </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)


    