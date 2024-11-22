import streamlit as st

# --- PAGE SETUP ---
current = st.Page(
    "views/current.py",
    title="Current Status",
    icon=":material/analytics:",
)

evolution = st.Page(
    "views/evolution.py",
    title="Evolution View",
    icon=":material/trending_up:",
)

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Menu": [current,evolution],
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")


# --- RUN NAVIGATION ---
pg.run()