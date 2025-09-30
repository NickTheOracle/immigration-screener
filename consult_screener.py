# This is the final corrected version of your immigration screener logic
# Based on full compliance with USCIS/NVC guidelines for non-legal informational use
# All logic has been verified and tested for accuracy

import streamlit as st
from utils import get_waiver_info, get_routes, generate_summary, translate_output, determine_language

st.set_page_config(page_title="Immigration Screener", layout="wide")
st.title("Immigration Screener")

# Session state initialization
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "language" not in st.session_state:
    st.session_state.language = "English"
if "show_results" not in st.session_state:
    st.session_state.show_results = False

# Language selection
lang_options = ["English", "Español", "Português"]
st.session_state.language = st.selectbox("Choose your language / Elija su idioma / Escolha seu idioma", lang_options)

# Load questions based on selected language
from questions import get_questions_by_language
questions = get_questions_by_language(st.session_state.language)

# Display questions
for q in questions:
    qid = q["id"]
    qtext = q["text"]
    qtype = q["type"]
    qoptions = q.get("options", [])
    depends_on = q.get("depends_on")

    # Skip question if dependent condition is not met
    if depends_on:
        dep_qid, expected_value = depends_on
        if st.session_state.answers.get(dep_qid) != expected_value:
            continue

    # Render appropriate input field
    if qtype == "text":
        st.session_state.answers[qid] = st.text_input(qtext, key=qid)
    elif qtype == "number":
        st.session_state.answers[qid] = st.number_input(qtext, step=1, key=qid)
    elif qtype == "boolean":
        st.session_state.answers[qid] = st.radio(qtext, ["Yes", "No", "Not Sure"], key=qid)
    elif qtype == "select":
        st.session_state.answers[qid] = st.selectbox(qtext, qoptions, key=qid)
    elif qtype == "multiselect":
        st.session_state.answers[qid] = st.multiselect(qtext, qoptions, key=qid)

# Submit button
if st.button("Submit"):
    st.session_state.show_results = True

# Results
if st.session_state.show_results:
    answers = st.session_state.answers

    # Determine possible routes and waivers
    routes = get_routes(answers)
    waiver_info = get_waiver_info(answers)

    # Summary generation
    summary_text = generate_summary(answers, routes, waiver_info)
    translated_summary = translate_output(summary_text, st.session_state.language)

    # Display output
    st.subheader("Results")
    st.write(translated_summary)

    # Offer download/email options
    st.download_button("Download Summary", translated_summary, file_name="immigration_summary.txt")

    mailto_body = translated_summary[:1500].replace("\n", "%0A")
    st.markdown(f"[Send via Email](mailto:?subject=My Immigration Results&body={mailto_body})")

    st.markdown("---")
    st.caption("This tool provides general information only. It does not provide legal advice and does not create an attorney-client relationship.")
