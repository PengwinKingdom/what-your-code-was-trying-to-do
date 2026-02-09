from config import BACKEND_URL
import json
import requests
import streamlit as st

def load_css(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

LANG_OPTIONS = ["", "Python", "JavaScript", "C++", "C#"]

lang_map = {
    "Python": "python",
    "JavaScript": "javascript",
    "C++": "cpp",
    "C#": "csharp",
    "": None
}

st.set_page_config(
    page_title="What Your Code Was Trying to Do",
    layout="wide",
    initial_sidebar_state="collapsed"
)

load_css("styles/main.css")

st.markdown("""
<div class="app-header">
  <h1>What Your Code Was Trying to Do</h1>
  <p>Paste your code to discover its intent, hidden assumptions, potential problems, and get actionable recommendations</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### Input")

    language_ui = st.selectbox(
        "Programming Language (optional)",
        LANG_OPTIONS,
        key="language_ui",
        help="Select the language for better analysis"
    )

    code = st.text_area(
        "Your Code (≤ 150 lines)",
        height=500,
        placeholder="Paste your code here...",
        help="Paste the code you want to analyze"
    )

    analyze = st.button("Analyze Code", type="primary", use_container_width=True)

with col2:
    st.markdown("### Analysis Results")

    if analyze:
        if not code.strip():
            st.warning("Please paste some code first.")
        else:
            payload = {
                "code": code,
                "language": lang_map.get(st.session_state.get("language_ui", ""))
            }

            with st.spinner("Analyzing your code..."):
                try:
                    r = requests.post(f"{BACKEND_URL}/analyze", json=payload, timeout=30)

                    if r.status_code != 200:
                        st.error(f"Backend error {r.status_code}")
                        st.code(r.text)
                    else:
                        data = r.json()

                        badges = data.get("badges", [])
                        confidence = data.get("confidence_score")
                        detected_lang = data.get("language_detected")
                        selected_ui = st.session_state.get("language_ui", "")

                        # Chips row
                        if confidence is not None or badges or (selected_ui == "" and detected_lang):
                            chips_html = '<div class="chips-row">'

                            # Show detected language ONLY if user left dropdown empty
                            if selected_ui == "" and detected_lang:
                                chips_html += f'<span class="chip">Detected: {detected_lang.capitalize()}</span>'

                            if confidence is not None:
                                chips_html += f'<span class="chip chip-strong">Confidence: {confidence}</span>'

                            for b in badges:
                                chips_html += f'<span class="chip">{b}</span>'

                            chips_html += '</div>'
                            st.markdown(chips_html, unsafe_allow_html=True)
                            st.divider()

                        # Intended Goal
                        ig = data.get("intended_goal", {})
                        if ig.get("summary"):
                            st.markdown('<div class="section-title">Intended Goal</div>', unsafe_allow_html=True)
                            st.markdown(f"**{ig.get('summary', '')}**")

                            signals = ig.get("signals", [])
                            if signals:
                                st.markdown("**Key Signals:**")
                                for s in signals:
                                    st.markdown(f"• {s}")

                        # Hidden Assumptions
                        assumptions = data.get("hidden_assumptions", [])
                        if assumptions:
                            st.markdown('<div class="section-title">Hidden Assumptions</div>', unsafe_allow_html=True)
                            for a in assumptions:
                                st.markdown(f"**{a.get('assumption','')}**")
                                st.markdown(f"*Risk:* {a.get('risk','')}")
                                st.markdown("")

                        # Future Problems
                        problems = data.get("future_problems", [])
                        if problems:
                            st.markdown('<div class="section-title">Future Problems</div>', unsafe_allow_html=True)
                            for p in problems:
                                sev = (p.get("severity") or "").lower()
                                sev_class = "tag-low"
                                if sev == "high":
                                    sev_class = "tag-high"
                                elif sev in ("med", "medium"):
                                    sev_class = "tag-med"

                                st.markdown(
                                    f'<span class="tag {sev_class}">{p.get("severity","").upper()}</span> '
                                    f'**{p.get("problem","")}**',
                                    unsafe_allow_html=True
                                )
                                st.markdown(f"*{p.get('why','')}*")
                                st.markdown("")

                        # Recommendation
                        rec = data.get("one_high_impact_recommendation", {})
                        if rec.get("action"):
                            st.markdown('<div class="section-title">High-Impact Recommendation</div>', unsafe_allow_html=True)
                            st.markdown(f"**Action:** {rec.get('action','')}")
                            st.markdown(f"**Why it matters:** {rec.get('why_it_matters','')}")
                            st.markdown(f"**First step:** {rec.get('first_step','')}")

                        with st.expander("Raw JSON"):
                            st.code(json.dumps(data, indent=2), language="json")

                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Is FastAPI running?")
                except requests.exceptions.RequestException as e:
                    st.error("Request failed.")
                    st.code(str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
    else:
        st.info("Paste your code and click 'Analyze Code' to get started.")
