import streamlit as st
from course_data import ROLES, TOPICS, BLOOM_COLORS, COURSE_META
from snowflake_utils import (
    get_plt_features,
    get_whats_new,
    generate_lesson_summary,
    chat_with_coach,
    answer_plt_question,
    get_plt_stats,
)

st.set_page_config(
    page_title="Snowflake Learning Engine",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0f1117; color: #e2e8f0; }
    [data-testid="stSidebar"] { background: #1a1f2e !important; border-right: 1px solid #2d3748; }

    .sidebar-header { padding: 1rem 0 0.5rem 0; }
    .sidebar-header h1 { font-size: 1rem !important; color: #60a5fa; font-weight: 700; margin: 0; }
    .sidebar-header p { font-size: 0.7rem; color: #64748b; margin: 0; }

    .stButton button {
        background: transparent !important; border: none !important;
        color: #94a3b8 !important; text-align: left !important;
        width: 100% !important; font-size: 0.78rem !important;
        padding: 0.4rem 0.6rem !important; border-radius: 6px !important;
        transition: all 0.15s;
    }
    .stButton button:hover { background: #1e3a5f !important; color: #e2e8f0 !important; }

    .hero {
        text-align: center; padding: 3.5rem 2rem 2rem 2rem;
    }
    .hero h1 { font-size: 2.4rem; color: #ffffff; margin: 0 0 0.5rem 0; font-weight: 700; }
    .hero p { color: #64748b; font-size: 1rem; margin: 0; }

    .role-card {
        background: #1a1f2e; border: 1px solid #2d3748;
        border-radius: 14px; padding: 1.6rem 1.2rem 1.4rem 1.2rem;
        text-align: center; cursor: pointer;
        transition: border-color 0.2s, transform 0.1s;
        height: 100%;
    }
    .role-card:hover { border-color: #3b82f6; transform: translateY(-2px); }
    .role-card .role-icon { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .role-card h3 { font-size: 1rem; color: #e2e8f0; margin: 0 0 0.4rem 0; font-weight: 700; }
    .role-card p { font-size: 0.78rem; color: #64748b; margin: 0; line-height: 1.5; }

    .topic-card {
        background: #1a1f2e; border: 1px solid #2d3748;
        border-radius: 14px; padding: 1.4rem 1.2rem;
        cursor: pointer; transition: border-color 0.2s, transform 0.1s;
        height: 100%;
    }
    .topic-card:hover { transform: translateY(-2px); }
    .topic-card .topic-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .topic-card h3 { font-size: 0.95rem; color: #e2e8f0; margin: 0 0 0.3rem 0; font-weight: 700; }
    .topic-card p { font-size: 0.75rem; color: #64748b; margin: 0; line-height: 1.45; }

    .lesson-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #1a2744 100%);
        border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1rem;
        border: 1px solid #2d4a7a;
    }
    .lesson-header h1 { font-size: 1.5rem; color: #ffffff; margin: 0 0 0.3rem 0; }
    .lesson-header p { color: #94a3b8; margin: 0; font-size: 0.88rem; }

    .role-badge {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.2rem 0.7rem; border-radius: 20px;
        font-size: 0.7rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
        margin-right: 0.4rem;
    }
    .bloom-badge {
        display: inline-block; padding: 0.2rem 0.7rem;
        border-radius: 20px; font-size: 0.7rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem;
    }
    .new-badge {
        background: #065f46; color: #34d399; border: 1px solid #059669;
        padding: 0.15rem 0.5rem; border-radius: 4px;
        font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .avail-ga { background: #064e3b; color: #34d399; border: 1px solid #059669; }
    .avail-pupr { background: #1e3a5f; color: #60a5fa; border: 1px solid #3b82f6; }
    .avail-prpr { background: #2d1f4e; color: #a78bfa; border: 1px solid #7c3aed; }

    .feature-card {
        background: #1a1f2e; border: 1px solid #2d3748;
        border-radius: 8px; padding: 0.75rem 1rem; margin: 0.4rem 0;
    }
    .feature-card h4 { margin: 0 0 0.3rem 0; font-size: 0.85rem; color: #e2e8f0; }
    .feature-card p { margin: 0; font-size: 0.75rem; color: #64748b; }

    .chat-bubble-user {
        background: #1e3a5f; border-radius: 12px 12px 4px 12px;
        padding: 0.6rem 0.9rem; margin: 0.4rem 0 0.4rem auto;
        max-width: 85%; font-size: 0.85rem; color: #e2e8f0;
    }
    .chat-bubble-coach {
        background: #1a2744; border: 1px solid #2d4a7a;
        border-radius: 12px 12px 12px 4px;
        padding: 0.6rem 0.9rem; margin: 0.4rem auto 0.4rem 0;
        max-width: 90%; font-size: 0.85rem; color: #94a3b8;
    }
    .section-label {
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #475569; margin: 1rem 0 0.5rem 0;
    }
    .summary-box {
        background: #1a1f2e; border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0; padding: 1rem 1.2rem;
        font-size: 0.88rem; line-height: 1.7; color: #cbd5e1;
    }
    [data-testid="stChatInput"] textarea { background: #1a1f2e !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("role", None),
    ("topic", None),
    ("active_lesson", 0),
    ("chat_history", {}),
    ("summary_cache", {}),
    ("plt_qa", {}),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── SCREEN 1: Role selection ───────────────────────────────────────────────────
def show_landing():
    st.markdown("""
    <div class="hero">
        <h1>❄️ Snowflake Learning Engine</h1>
        <p>Living Course · Content grounded in live Snowflake product data</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p style="text-align:center;color:#94a3b8;font-size:1rem;margin-bottom:1.5rem;">'
        'Who are you? Choose your role to get a personalized learning experience.</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(4, gap="large")
    for col, (role_key, role) in zip(cols, ROLES.items()):
        with col:
            st.markdown(f"""
            <div class="role-card">
                <div class="role-icon">{role['icon']}</div>
                <h3>{role['label']}</h3>
                <p>{role['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start as {role['label']}", key=f"role_{role_key}", use_container_width=True):
                st.session_state.role = role_key
                st.session_state.topic = None
                st.session_state.active_lesson = 0
                st.session_state.chat_history = {}
                st.session_state.summary_cache = {}
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    stats = get_plt_stats()
    if stats:
        st.markdown(
            f'<p style="text-align:center;color:#475569;font-size:0.75rem;">'
            f'Powered by live Snowflake PLT data · {stats.get("ga", 0)} GA features · '
            f'{stats.get("recent", 0)} updated in the last 90 days</p>',
            unsafe_allow_html=True,
        )


# ── SCREEN 2: Topic selection ──────────────────────────────────────────────────
def show_topic_selection():
    role = ROLES[st.session_state.role]

    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-header">
            <h1>❄️ Snowflake Learning Engine</h1>
            <p>{role['icon']} {role['label']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        if st.button("← Switch role", use_container_width=True):
            st.session_state.role = None
            st.rerun()

    st.markdown(f"""
    <div class="hero" style="padding-top:2rem;">
        <h1>Welcome, {role['label']} {role['icon']}</h1>
        <p>Choose a product area to start your learning path.</p>
    </div>
    """, unsafe_allow_html=True)

    topic_keys = list(TOPICS.keys())
    row1 = st.columns(3, gap="large")
    row2_cols = st.columns([1, 3, 3, 1], gap="large")
    row2 = [row2_cols[1], row2_cols[2]]

    for i, (col, topic_key) in enumerate(zip(row1 + row2, topic_keys)):
        topic = TOPICS[topic_key]
        with col:
            lesson_count = len(topic["lessons"])
            st.markdown(f"""
            <div class="topic-card" style="border-color:{topic['color']}33;">
                <div class="topic-icon">{topic['icon']}</div>
                <h3 style="color:{topic['color']};">{topic['label']}</h3>
                <p>{topic['description']}</p>
                <p style="margin-top:0.6rem;color:#475569;">{lesson_count} lessons</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {topic['label']}", key=f"topic_{topic_key}", use_container_width=True):
                st.session_state.topic = topic_key
                st.session_state.active_lesson = 0
                st.session_state.chat_history = {}
                st.session_state.summary_cache = {}
                st.rerun()


# ── SCREEN 3: Course view ──────────────────────────────────────────────────────
def show_course():
    role_key = st.session_state.role
    topic_key = st.session_state.topic
    role = ROLES[role_key]
    topic = TOPICS[topic_key]
    lessons = topic["lessons"]
    lesson_idx = st.session_state.active_lesson
    lesson = lessons[lesson_idx]

    if lesson_idx not in st.session_state.chat_history:
        st.session_state.chat_history[lesson_idx] = []

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-header">
            <h1>{topic['icon']} {topic['label']}</h1>
            <p>{role['icon']} {role['label']}</p>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        for i, ls in enumerate(lessons):
            is_active = lesson_idx == i
            has_chat = bool(st.session_state.chat_history.get(i))
            check = "✅ " if has_chat else ("▶ " if is_active else "  ")
            label = f"{check}{ls['id']:02d}. {ls['title']}"
            if st.button(label, key=f"nav_{i}", use_container_width=True):
                st.session_state.active_lesson = i
                st.rerun()

        st.divider()
        if st.button("← Change topic", use_container_width=True):
            st.session_state.topic = None
            st.rerun()
        if st.button("← Switch role", use_container_width=True):
            st.session_state.role = None
            st.session_state.topic = None
            st.rerun()

        st.divider()
        stats = get_plt_stats()
        if stats:
            st.markdown('<div class="section-label">Live Product Data</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.metric("GA Features", stats.get("ga", "—"))
            c2.metric("In Preview", stats.get("pupr", "—"))
            st.caption(f"↑ {stats.get('recent', 0)} updated in last 90 days")

    # ── Main + Coach columns ──
    col_main, col_chat = st.columns([3, 2], gap="large")

    with col_main:
        bloom_color = BLOOM_COLORS.get(lesson["bloom_level"], "#64748b")
        topic_color = topic["color"]
        role_color = role["color"]

        st.markdown(f"""
        <div class="lesson-header">
            <h1>{lesson['title']}</h1>
            <p>{lesson['subtitle']}</p>
            <div style="margin-top:0.6rem;">
                <span class="role-badge" style="background:{role_color}22;color:{role_color};border:1px solid {role_color}55;">
                    {role['icon']} {role['label']}
                </span>
                <span class="role-badge" style="background:{topic_color}22;color:{topic_color};border:1px solid {topic_color}55;">
                    {topic['icon']} {topic['label']}
                </span>
                <span class="bloom-badge" style="background:{bloom_color}22;color:{bloom_color};border:1px solid {bloom_color}55;">
                    {lesson['bloom_level']}
                </span>
                <span style="color:#475569;font-size:0.75rem;margin-left:0.5rem;">⏱ {lesson['duration']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav_c1, nav_c2, nav_c3 = st.columns([1, 4, 1])
        with nav_c1:
            if lesson_idx > 0:
                if st.button("← Previous", key="prev"):
                    st.session_state.active_lesson -= 1
                    st.rerun()
        with nav_c2:
            completed = sum(1 for i in range(len(lessons)) if st.session_state.chat_history.get(i))
            st.progress(completed / len(lessons), text=f"{completed}/{len(lessons)} lessons practiced")
        with nav_c3:
            if lesson_idx < len(lessons) - 1:
                if st.button("Next →", key="next"):
                    st.session_state.active_lesson += 1
                    st.rerun()

        st.markdown("---")

        tab_summary, tab_features, tab_objectives, tab_qa = st.tabs(["📖 Lesson Overview", "⚡ Live Features", "🎯 Objectives", "💬 Ask the PLT"])

        with tab_summary:
            with st.spinner("Fetching live product data..."):
                features = get_plt_features(lesson["plt_keywords"])
                whats_new = get_whats_new(lesson["plt_keywords"])

            if whats_new:
                st.markdown(f'<span class="new-badge">🆕 {len(whats_new)} new this quarter</span>', unsafe_allow_html=True)
                with st.expander(f"What's New — {len(whats_new)} recent updates"):
                    for f in whats_new:
                        avail = f.get("CURRENT_AVAILABILITY", "")
                        badge_class = "avail-ga" if avail == "Generally Available" else "avail-pupr"
                        st.markdown(f"""
                        <div class="feature-card">
                            <h4>{f['FEATURE_NAME']} <span class="{badge_class}" style="padding:2px 6px;border-radius:3px;font-size:0.65rem;">{avail}</span></h4>
                            <p>{f.get('TARGET_QUARTER', '') or ''}</p>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown('<div class="section-label">AI-Generated Lesson Overview</div>', unsafe_allow_html=True)
            st.caption(f"Personalized for {role['label']} · Grounded in live PLT data · Refreshes every 30 min")

            cache_key = f"{role_key}_{topic_key}_{lesson_idx}"
            if cache_key not in st.session_state.summary_cache:
                with st.spinner("Generating your personalized lesson overview..."):
                    summary = generate_lesson_summary(
                        lesson["title"],
                        lesson["objectives"],
                        features,
                        role_context=role["context"],
                    )
                    st.session_state.summary_cache[cache_key] = summary

            summary = st.session_state.summary_cache.get(cache_key, "")
            st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

            if st.button("🔄 Regenerate", key=f"regen_{lesson_idx}"):
                if cache_key in st.session_state.summary_cache:
                    del st.session_state.summary_cache[cache_key]
                st.rerun()

        with tab_features:
            st.markdown('<div class="section-label">Features from Snowflake PLT</div>', unsafe_allow_html=True)
            st.caption(f"Matching: {', '.join(lesson['plt_keywords'][:4])}")
            if features:
                for f in features:
                    avail = f.get("CURRENT_AVAILABILITY", "")
                    badge_class = "avail-ga" if avail == "Generally Available" else ("avail-pupr" if avail == "Public Preview" else "avail-prpr")
                    label = "GA" if avail == "Generally Available" else ("Public Preview" if avail == "Public Preview" else "Private Preview")
                    snippet = (f.get("SEARCH_TEXT") or "")[:200]
                    st.markdown(f"""
                    <div class="feature-card">
                        <h4>{f['FEATURE_NAME']}
                            <span class="{badge_class}" style="padding:2px 6px;border-radius:3px;font-size:0.65rem;">{label}</span>
                        </h4>
                        <p>{snippet}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No PLT features loaded — check Snowflake connection.")

        with tab_objectives:
            st.markdown('<div class="section-label">Learning Objectives</div>', unsafe_allow_html=True)
            for obj in lesson["objectives"]:
                st.markdown(f"✓ {obj}")
            st.markdown('<div class="section-label">Key Features Covered</div>', unsafe_allow_html=True)
            for feat in lesson["key_features"]:
                st.markdown(f"• **{feat}**")
            st.markdown('<div class="section-label">Matrix Alignment</div>', unsafe_allow_html=True)
            st.markdown(f"🗂 {lesson['domain_tag']}")
            st.markdown('<div class="section-label">Bloom\'s Taxonomy</div>', unsafe_allow_html=True)
            bc = BLOOM_COLORS.get(lesson["bloom_level"], "#64748b")
            st.markdown(f"""
            <span class="bloom-badge" style="background:{bc}22;color:{bc};border:1px solid {bc}55;">
                {lesson['bloom_level']}
            </span>
            """, unsafe_allow_html=True)

        with tab_qa:
            st.markdown('<div class="section-label">Ask the Product Catalog</div>', unsafe_allow_html=True)
            st.caption(f"Ask any question about the {topic['label']} features loaded for this lesson. Powered by Snowflake Cortex.")

            qa_key = f"{role_key}_{topic_key}_{lesson_idx}"
            qa_history = st.session_state.plt_qa.get(qa_key, [])

            qa_container = st.container(height=300)
            with qa_container:
                if not qa_history:
                    st.markdown(
                        '<div style="color:#475569;font-size:0.82rem;padding:0.5rem 0;">'
                        'Examples: "Which features are GA on Azure?" · '
                        '"What\'s new in the last 90 days?" · '
                        '"How does this compare to Databricks?"</div>',
                        unsafe_allow_html=True,
                    )
                for qa in qa_history:
                    st.markdown(f'<div class="chat-bubble-user">{qa["q"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-bubble-coach">{qa["a"]}</div>', unsafe_allow_html=True)

            qa_input = st.chat_input("Ask about this product area...", key=f"qa_{lesson_idx}")
            if qa_input:
                with st.spinner("Querying the PLT..."):
                    answer = answer_plt_question(
                        qa_input,
                        features if features else get_plt_features(lesson["plt_keywords"]),
                        role_label=role["label"],
                        role_context=role["context"],
                    )
                qa_history.append({"q": qa_input, "a": answer})
                st.session_state.plt_qa[qa_key] = qa_history
                st.rerun()

            if qa_history:
                if st.button("Clear Q&A", key=f"clear_qa_{lesson_idx}"):
                    st.session_state.plt_qa[qa_key] = []
                    st.rerun()

    with col_chat:
        st.markdown(f"""
        <div style="background:#1a1f2e;border:1px solid #2d3748;border-radius:10px;padding:1rem 1.2rem;margin-bottom:0.8rem;">
            <div style="font-size:0.7rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">Practice Coach</div>
            <div style="font-size:0.9rem;font-weight:600;color:#e2e8f0;">{lesson['coach_persona']}</div>
            <div style="font-size:0.75rem;color:#64748b;margin-top:0.3rem;">{lesson['scenario']}</div>
        </div>
        """, unsafe_allow_html=True)

        history = st.session_state.chat_history[lesson_idx]

        chat_container = st.container(height=450)
        with chat_container:
            if not history:
                st.markdown(f"""
                <div class="chat-bubble-coach">
                    👋 I'm your {lesson['coach_persona']} for this practice session.<br><br>
                    <em>{lesson['scenario']}</em><br><br>
                    Go ahead — how would you respond?
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in history:
                    css_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-coach"
                    st.markdown(f'<div class="{css_class}">{msg["content"]}</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Respond to the scenario...", key=f"chat_{lesson_idx}")
        if user_input:
            history.append({"role": "user", "content": user_input})
            with st.spinner("Coach is responding..."):
                response = chat_with_coach(
                    lesson["title"],
                    lesson["scenario"],
                    lesson["coach_persona"],
                    history[:-1],
                    user_input,
                    role_label=role["label"],
                    role_context=role["context"],
                )
            history.append({"role": "assistant", "content": response})
            st.session_state.chat_history[lesson_idx] = history
            st.rerun()

        if history:
            if st.button("🔄 Reset practice", key=f"reset_{lesson_idx}"):
                st.session_state.chat_history[lesson_idx] = []
                st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.role is None:
    show_landing()
elif st.session_state.topic is None:
    show_topic_selection()
else:
    show_course()
