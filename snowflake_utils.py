import os
import json
import snowflake.connector
import streamlit as st

CONNECTION_NAME = os.getenv("SNOWFLAKE_CONNECTION_NAME") or "sales-enablement"


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(connection_name=CONNECTION_NAME)


def _run_query(sql: str, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur.fetchall(), [d[0] for d in cur.description]
    except Exception as e:
        st.error(f"Query error: {e}")
        return [], []


@st.cache_data(ttl=3600, show_spinner=False)
def get_plt_features(keywords: list[str], limit: int = 15) -> list[dict]:
    """Fetch live PLT features matching lesson keywords."""
    like_clauses = " OR ".join([f"SEARCH_TEXT ILIKE '%{kw}%'" for kw in keywords])
    sql = f"""
        SELECT
            FEATURE_NAME,
            CURRENT_AVAILABILITY,
            TARGET_AVAILABILITY,
            AVAILABLE_CLOUDS,
            PM_OWNER,
            TARGET_QUARTER,
            TARGET_END_DATE,
            SEARCH_TEXT
        FROM SALES.RAVEN.PLT_SEARCH_DATA
        WHERE ({like_clauses})
          AND CURRENT_AVAILABILITY IN ('Generally Available', 'Public Preview', 'Private Preview')
        ORDER BY
            CASE CURRENT_AVAILABILITY WHEN 'Generally Available' THEN 1 WHEN 'Public Preview' THEN 2 ELSE 3 END,
            TARGET_END_DATE DESC NULLS LAST
        LIMIT {limit}
    """
    rows, cols = _run_query(sql)
    return [dict(zip(cols, row)) for row in rows]


@st.cache_data(ttl=3600, show_spinner=False)
def get_whats_new(keywords: list[str]) -> list[dict]:
    """Features updated or released in the last 90 days."""
    like_clauses = " OR ".join([f"SEARCH_TEXT ILIKE '%{kw}%'" for kw in keywords])
    sql = f"""
        SELECT FEATURE_NAME, CURRENT_AVAILABILITY, TARGET_QUARTER, TARGET_END_DATE
        FROM SALES.RAVEN.PLT_SEARCH_DATA
        WHERE ({like_clauses})
          AND TARGET_END_DATE >= DATEADD(day, -90, CURRENT_DATE())
          AND CURRENT_AVAILABILITY IN ('Generally Available', 'Public Preview')
        ORDER BY TARGET_END_DATE DESC
        LIMIT 5
    """
    rows, cols = _run_query(sql)
    return [dict(zip(cols, row)) for row in rows]


@st.cache_data(ttl=1800, show_spinner=False)
def generate_lesson_summary(lesson_title: str, objectives: list[str], features: list[dict], role_context: str = "") -> str:
    """Use Cortex Complete to generate a live lesson summary grounded in PLT data."""
    feature_context = "\n".join([
        f"- {f['FEATURE_NAME']} ({f['CURRENT_AVAILABILITY']}): {f['SEARCH_TEXT'][:200]}"
        for f in features[:8]
    ])
    objectives_text = "\n".join([f"- {o}" for o in objectives])

    role_instruction = f"\nRole context: {role_context}" if role_context else ""

    prompt = f"""You are a Snowflake sales enablement expert writing a crisp lesson overview.{role_instruction}

Lesson: {lesson_title}

Learning objectives:
{objectives_text}

Current Snowflake features and capabilities relevant to this lesson (from the Product Launch Tracker):
{feature_context}

Write a concise lesson overview (3-4 paragraphs) that:
1. Sets context for why this topic matters for the learner's specific role
2. Highlights 2-3 most important concepts with customer value framed for this role
3. Calls out any recent capability updates that strengthen the pitch
4. Ends with a 1-sentence "bottom line" this role should be able to say in a customer conversation

Keep it sharp, role-specific, and grounded in the feature data above. Avoid generic filler."""

    sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', %s) AS response"
    rows, _ = _run_query(sql, [prompt])
    if rows:
        return rows[0][0]
    return "Summary unavailable — check Snowflake connection."


def chat_with_coach(lesson_title: str, scenario: str, persona: str, history: list[dict], user_message: str, role_label: str = "", role_context: str = "") -> str:
    """Stream a response from the AI coaching agent."""
    messages = [
        {
            "role": "system",
            "content": f"""You are a {persona} coaching a Snowflake {role_label or 'sales rep'} in a practice conversation.
Lesson topic: {lesson_title}
Practice scenario: {scenario}
{f'Learner role context: {role_context}' if role_context else ''}

Your job:
- Play the customer or manager role described in the scenario
- Ask probing follow-up questions when the rep gives vague answers
- Provide coaching feedback when they get something right or miss something important
- Keep responses concise (2-4 sentences)
- After 4-5 exchanges, offer a 1-paragraph debrief on what went well and what to improve

Stay in character as the {persona} unless explicitly asked for feedback."""
        }
    ]
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    messages_json = json.dumps(messages)
    sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', PARSE_JSON(%s)) AS response"
    rows, _ = _run_query(sql, [messages_json])
    if rows:
        return rows[0][0]
    return "Coach unavailable — check Snowflake connection."


def answer_plt_question(question: str, features: list[dict], role_label: str = "", role_context: str = "") -> str:
    """Answer a free-form question about PLT features using Cortex Complete."""
    if not features:
        return "No product data loaded — check Snowflake connection."
    feature_context = "\n".join([
        f"- {f['FEATURE_NAME']} ({f.get('CURRENT_AVAILABILITY', '')}) — {(f.get('SEARCH_TEXT') or '')[:250]}"
        for f in features[:20]
    ])
    role_instruction = f"Answer from the perspective of helping a Snowflake {role_label}. " if role_label else ""
    prompt = f"""You are a Snowflake product expert. {role_instruction}

Using the following features from the Snowflake Product Launch Tracker, answer this question concisely and accurately:

Question: {question}

Available product features:
{feature_context}

Give a direct answer in 2-4 sentences. Reference specific feature names where relevant. If the answer isn't covered by the features above, say so clearly."""
    sql = "SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3-70b', %s) AS response"
    rows, _ = _run_query(sql, [prompt])
    if rows:
        return rows[0][0]
    return "Unable to answer — check Snowflake connection."


@st.cache_data(ttl=86400, show_spinner=False)
def get_plt_stats() -> dict:
    """Get high-level PLT stats for the course header."""
    sql = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN CURRENT_AVAILABILITY = 'Generally Available' THEN 1 ELSE 0 END) as ga_count,
            SUM(CASE WHEN CURRENT_AVAILABILITY = 'Public Preview' THEN 1 ELSE 0 END) as pupr_count,
            SUM(CASE WHEN TARGET_END_DATE >= DATEADD(day, -90, CURRENT_DATE()) THEN 1 ELSE 0 END) as recent_count
        FROM SALES.RAVEN.PLT_SEARCH_DATA
    """
    rows, _ = _run_query(sql)
    if rows:
        return {"total": rows[0][0], "ga": rows[0][1], "pupr": rows[0][2], "recent": rows[0][3]}
    return {}
