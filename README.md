# Snowflake Sales Learning Engine

A living, role-personalized sales training app powered by live Snowflake product data and Cortex AI.

Reps choose their role, pick a product area, and work through structured lessons grounded in real-time data from the Snowflake Product Launch Tracker (PLT) — with an AI coaching agent for practice conversations.

**Built with:** Streamlit · Snowflake Cortex Complete (`llama3-70b`) · Snowflake Connector for Python

---

## What it does

- **Role-personalized lessons** — content and AI summaries adapt to the rep's role: Account Executive, Solution Engineer, Account Cloud Engineer, or Sales Development Rep
- **5 topic areas, 27 lessons** — Snowflake Platform · AI & Cortex · Analytics · Data Engineering · Apps & Collaboration
- **Bloom's Taxonomy structure** — every lesson is tagged with a cognitive level (Understand → Apply → Analyze → Evaluate → Create) so reps know exactly what skill they're building
- **Live product data** — lessons pull current feature availability from `SALES.RAVEN.PLT_SEARCH_DATA` in real time
- **What's New badge** — lessons surface a `🆕 N new this quarter` indicator when PLT features have been updated in the last 90 days
- **AI lesson overviews** — Cortex Complete generates a fresh summary grounded in live PLT data for each lesson
- **Practice coach** — role-play customer conversations with a role-specific AI persona (e.g., SE Manager, Field AE, Competitive SE) tailored to each lesson topic
- **Ask the PLT** — free-form Q&A against the product catalog, answered by Cortex
- **Progress tracker** — tracks lessons practiced across the course so reps can see how far they've come

---

## Running locally

**Prerequisites:** Python 3.11+, a Snowflake account with access to `SALES.RAVEN.PLT_SEARCH_DATA`

```bash
git clone https://github.com/lillie-grisko/sales-onboarding-learning-engine
cd sales-onboarding-learning-engine
pip install -r requirements.txt
SNOWFLAKE_CONNECTION_NAME=your-connection streamlit run app.py
```

The app uses your local Snowflake connection profile (`~/.snowflake/connections.toml`).

---

## Deploying to Streamlit Community Cloud

1. Fork this repo (or use it directly if you have access)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** → connect your GitHub repo
3. Set **Main file path** to `app.py`
4. Under **Advanced settings → Secrets**, paste the following and fill in your credentials:

**Option A — Programmatic Access Token (recommended):**
```toml
[snowflake]
account   = "your-account-identifier"
user      = "YOUR_USERNAME"
token     = "YOUR_PAT_TOKEN"
warehouse = "YOUR_WAREHOUSE"
role      = "YOUR_ROLE"
```

**Option B — Username / Password:**
```toml
[snowflake]
account   = "your-account-identifier"
user      = "YOUR_USERNAME"
password  = "YOUR_PASSWORD"
warehouse = "YOUR_WAREHOUSE"
role      = "YOUR_ROLE"
```

5. Click **Deploy** — your app will be live at `https://your-app.streamlit.app`

> The `account` identifier follows the format `orgname-accountname` (e.g. `sfcogsops-snowhouse_aws_us_west_2`).
>
> **PAT note:** Programmatic Access Tokens bake in the user's default role at creation time. Ensure your default role has `SELECT` on `SALES.RAVEN.PLT_SEARCH_DATA` before generating the token.

---

## Project structure

```
app.py              # Main Streamlit app — routing, UI, screens
course_data.py      # All lesson content: roles, topics, objectives, coach scenarios
snowflake_utils.py  # Snowflake connection + all data/AI functions
requirements.txt    # Python dependencies
snowflake.yml       # Config for deploying as a Streamlit in Snowflake (SiS) app
.streamlit/
  secrets.toml.example   # Template for Streamlit Cloud credentials (copy → secrets.toml)
```

---

## Data requirements

| Object | Type | Used for |
|---|---|---|
| `SALES.RAVEN.PLT_SEARCH_DATA` | Table | Live product feature data powering all lessons |
| `SNOWFLAKE.CORTEX.COMPLETE` | Function (`llama3-70b`) | AI lesson summaries, coaching responses, and Q&A |

Your Snowflake role needs:
- `SELECT` on `SALES.RAVEN.PLT_SEARCH_DATA`
- Access to `SNOWFLAKE.CORTEX.COMPLETE` (granted via Cortex usage privileges on the account)
