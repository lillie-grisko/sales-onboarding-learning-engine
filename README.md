# Snowflake Sales Learning Engine

A living, role-personalized sales training app powered by live Snowflake product data and Cortex AI.

Reps choose their role (AE, SE, ACE, SDR), pick a product area, and work through lessons that are grounded in real-time data from the Snowflake Product Launch Tracker — with an AI coaching agent for practice conversations.

**Built with:** Streamlit · Snowflake Cortex Complete · Snowflake Connector for Python

---

## What it does

- **Role-personalized lessons** — content and AI summaries adapt to AE, SE, ACE, or SDR context
- **Live product data** — lessons pull current feature availability from `SALES.RAVEN.PLT_SEARCH_DATA`
- **AI lesson overviews** — Cortex Complete generates a fresh summary grounded in PLT data
- **Practice coach** — role-play customer conversations with an AI persona for each lesson
- **Ask the PLT** — free-form Q&A against the product catalog, answered by Cortex

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

```toml
[snowflake]
account   = "your-account-identifier"
user      = "YOUR_USERNAME"
password  = "YOUR_PASSWORD"
warehouse = "SNOWFLAKE_INTELLIGENCE_SALES_WH"
role      = "SALES_BASIC_RO"
```

5. Click **Deploy** — your app will be live at `https://your-app.streamlit.app`

> The `account` identifier follows the format `orgname-accountname` (e.g. `sfcogsops-snowhouse_aws_us_west_2`).

---

## Project structure

```
app.py              # Main Streamlit app — routing, UI, screens
course_data.py      # All lesson content: roles, topics, objectives, coach scenarios
snowflake_utils.py  # Snowflake connection + all data/AI functions
requirements.txt    # Python dependencies
snowflake.yml       # Snowflake CLI config for deploying as a Streamlit in Snowflake app
.streamlit/
  secrets.toml.example   # Template for Streamlit Cloud credentials (copy → secrets.toml)
```

---

## Data requirements

The app queries one Snowflake table:

| Object | Used for |
|---|---|
| `SALES.RAVEN.PLT_SEARCH_DATA` | Live product feature data powering all lessons |
| `SNOWFLAKE.CORTEX.COMPLETE` | AI lesson summaries, coaching, and Q&A |

Your Snowflake role needs `SELECT` on `SALES.RAVEN.PLT_SEARCH_DATA` and `USAGE` on the `CORTEX` functions.
