import streamlit as st
import json

# --- Placeholder Logic Replacements for utils.py ---

def determine_language(text):
    if any(word in text.lower() for word in ["el", "la", "usted", "gracias"]):
        return "spanish"
    elif any(word in text.lower() for word in ["você", "obrigado", "qual", "como"]):
        return "portuguese"
    return "english"

def get_routes(text):
    if "parent" in text.lower():
        return ["I-130 Immediate Relative Petition", "Consular Processing"]
    elif "asylum" in text.lower():
        return ["I-589 Asylum"]
    return ["I-485 Adjustment of Status"]

def get_waiver_info(text):
    if "unlawful presence" in text.lower():
        return ["I-601A Provisional Waiver"]
    elif "removal" in text.lower():
        return ["I-212 Permission to Reapply"]
    return []

def generate_summary(text, routes, waivers):
    summary = f"For the given input, the suggested route(s) are: {', '.join(routes)}."
    if waivers:
        summary += f" Possible waivers include: {', '.join(waivers)}."
    return summary

def translate_output(text, language):
    translations = {
        "spanish": {
            "For the given input": "Para la información proporcionada",
            "the suggested route(s) are": "las rutas sugeridas son",
            "Possible waivers include": "Posibles exenciones incluyen"
        },
        "portuguese": {
            "For the given input": "Para as informações fornecidas",
            "the suggested route(s) are": "as rotas sugeridas são",
            "Possible waivers include": "Possíveis perdões incluem"
        }
    }

    if language not in translations:
        return text

    for eng, trans in translations[language].items():
        text = text.replace(eng, trans)
    return text

# --- Streamlit App ---

st.set_page_config(page_title="Immigration Screener", layout="centered")

st.title("🧾 Immigration Consultation Screener")
st.markdown("Enter details about your immigration case to view possible routes and waivers.")

text_input = st.text_area("Describe the situation:", height=200)

if st.button("Analyze"):
    if not text_input.strip():
        st.error("Please enter some details to analyze.")
    else:
        language = determine_language(text_input)
        routes = get_routes(text_input)
        waivers = get_waiver_info(text_input)
        summary = generate_summary(text_input, routes, waivers)
        translated = translate_output(summary, language)

        st.subheader("🧭 Immigration Route(s):")
        for r in routes:
            st.markdown(f"- {r}")

        if waivers:
            st.subheader("🛑 Waiver(s) Recommended:")
            for w in waivers:
                st.markdown(f"- {w}")

        st.subheader("📝 Summary")
        st.write(translated)

        st.download_button(
            label="📄 Download Summary",
            data=translated,
            file_name="immigration_summary.txt",
            mime="text/plain"
        )
