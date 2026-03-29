import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from datetime import datetime

from backend.agent.tools import regenerate_itinerary_with_customization

st.set_page_config(page_title="Your travel plan", page_icon="📋", layout="wide")

if "user_inputs" not in st.session_state:
    st.warning("No trip data found. Start from the home page.")
    if st.button("← Back to planner"):
        st.switch_page("app.py")
    st.stop()

plan_text = (
    st.session_state.get("plan")
    or st.session_state.get("customized_plan")
    or st.session_state.get("generated_plan")
    or ""
).strip()
if not plan_text:
    st.warning("No plan to display yet.")
    if st.button("← Back to planner"):
        st.switch_page("app.py")
    st.stop()

ui = st.session_state["user_inputs"]
finalized = bool(st.session_state.get("finalized", False))

st.title("📋 Your travel plan")

with st.sidebar:
    st.header("Trip summary")
    st.write(f"**From:** {ui.get('start_location', '')}")
    st.write(f"**To:** {ui.get('destination', '')}")
    try:
        sd = datetime.strptime(ui["start_date"][:10], "%Y-%m-%d").date()
        ed = datetime.strptime(ui["end_date"][:10], "%Y-%m-%d").date()
        st.write(f"**Dates:** {sd} → {ed}")
    except Exception:
        st.write(f"**Dates:** {ui.get('start_date')} → {ui.get('end_date')}")
    st.write(f"**Days:** {ui.get('total_days', '')}")
    if st.button("← Edit trip (home)"):
        st.switch_page("app.py")

weather_md = st.session_state.get("weather_md")
weather_err = st.session_state.get("weather_err")
if weather_err:
    with st.expander("Weather", expanded=False):
        st.warning(weather_err)
elif weather_md:
    with st.expander("🌤️ Weather for your trip", expanded=False):
        st.markdown(weather_md)

if finalized:
    st.success("This plan is finalized.")
    st.markdown("---")
    st.markdown(plan_text)
else:
    st.markdown("---")
    st.markdown(plan_text)
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Customize Plan", type="primary", use_container_width=True):
            st.session_state["plan_show_customize"] = True
    with c2:
        if st.button("Finalize Plan", use_container_width=True):
            st.session_state["finalized"] = True
            st.session_state["plan_show_customize"] = False
            st.rerun()

    if st.session_state.get("plan_show_customize"):
        st.subheader("Customize your plan")
        changes = st.text_area(
            "Enter changes you want to make",
            key="plan_custom_changes",
            placeholder="Describe how you want the full itinerary updated…",
            height=140,
        )
        if st.button("Apply changes & regenerate", type="primary"):
            if not changes.strip():
                st.warning("Please describe the changes you want.")
            else:
                wsum = st.session_state.get("weather_md") or ""
                if st.session_state.get("weather_err"):
                    wsum = f"Weather unavailable: {st.session_state.get('weather_err')}"
                if not wsum.strip():
                    wsum = "No detailed weather forecast was provided."
                with st.spinner("Regenerating your full itinerary…"):
                    new_plan = regenerate_itinerary_with_customization(
                        ui,
                        plan_text,
                        changes.strip(),
                        weather_summary=wsum,
                    )
                st.session_state["customized_plan"] = new_plan
                st.session_state["plan"] = new_plan
                st.session_state["plan_show_customize"] = False
                st.rerun()
