import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ===== Translations =====
TEXT = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": ("**Disclaimer:** This tool is for informational purposes only. "
                       "It does not provide legal advice, does not create an attorney-client relationship, "
                       "and should not be relied on as a substitute for advice from a licensed immigration attorney."),
        "lang_prompt": "Choose language / Elija idioma / Escolha idioma",
        "start": "Start",
        "next": "Next",
        "back": "Back",
        "determine": "Show results",
        "results": "Informational Results",
        "pdf_btn": "Download PDF summary",
        "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this PDF or email to the administrator or the person who provided you this form.",
        "no_route": "No clear route identified. Further review with counsel recommended.",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
        "progress": "Step {cur} of {total}",
    },
    "es": {
        "title": "Evaluador de Consulta de Inmigración",
        "disclaimer": ("**Aviso:** Esta herramienta es solo para información general. "
                       "No ofrece asesoría legal, no crea una relación abogado-cliente y no debe usarse "
                       "como sustituto de la asesoría de un abogado de inmigración autorizado."),
        "lang_prompt": "Elija idioma / Choose language / Escolha idioma",
        "start": "Iniciar",
        "next": "Siguiente",
        "back": "Atrás",
        "determine": "Mostrar resultados",
        "results": "Resultados informativos",
        "pdf_btn": "Descargar resumen en PDF",
        "mailto_btn": "Abrir correo para enviar resumen",
        "admin_note": "Por favor envíe este PDF o correo al administrador o a quien le dio este formulario.",
        "no_route": "No hay ruta clara según sus respuestas. Se recomienda revisión con abogado.",
        "routes_label": "Rutas posibles para explorar",
        "notes_label": "Notas",
        "progress": "Paso {cur} de {total}",
    },
    "pt": {
        "title": "Triagem de Consulta de Imigração",
        "disclaimer": ("**Aviso:** Esta ferramenta é apenas para fins informativos. "
                       "Não fornece aconselhamento jurídico, não cria relação advogado-cliente e não substitui "
                       "a orientação de um advogado de imigração licenciado."),
        "lang_prompt": "Escolha idioma / Choose language / Elija idioma",
        "start": "Iniciar",
        "next": "Avançar",
        "back": "Voltar",
        "determine": "Mostrar resultados",
        "results": "Resultados informativos",
        "pdf_btn": "Baixar resumo em PDF",
        "mailto_btn": "Abrir e-mail para enviar resumo",
        "admin_note": "Envie este PDF ou e-mail ao administrador ou a quem lhe forneceu este formulário.",
        "no_route": "Nenhuma rota clara identificada. Recomenda-se revisão com advogado.",
        "routes_label": "Rotas possíveis para explorar",
        "notes_label": "Observações",
        "progress": "Etapa {cur} de {total}",
    },
}

# ===== PDF maker =====
def make_pdf_bytes(answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(TEXT[lang]["title"], styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Answers:", styles["Heading2"]))
    for k, v in answers.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(TEXT[lang]["routes_label"], styles["Heading2"]))
    if routes:
        for r in routes:
            story.append(Paragraph(f"- {r}", styles["Normal"]))
    else:
        story.append(Paragraph(TEXT[lang]["no_route"], styles["Normal"]))
    if notes:
        story.append(Spacer(1, 12))
        story.append(Paragraph(TEXT[lang]["notes_label"], styles["Heading2"]))
        for n in notes:
            story.append(Paragraph(f"- {n}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(TEXT[lang]["admin_note"], styles["Italic"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated: {datetime.datetime.utcnow().isoformat()} UTC", styles["Normal"]))
    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf

# ===== Config =====
st.set_page_config(page_title="Screener", layout="centered")

# ===== State =====
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ===== Language selection (Step 0) =====
if st.session_state.step == 0:
    lang_choice = st.selectbox("Choose language / Elija idioma / Escolha idioma", ["English", "Español", "Português"])
    st.session_state.lang = {"English": "en", "Español": "es", "Português": "pt"}[lang_choice]
    if st.button(TEXT[st.session_state.lang]["start"]):
        st.session_state.step = 1

lang = st.session_state.lang
t = TEXT[lang]

# ===== Disclaimer (always visible) =====
st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

# ===== Questions definition =====
questions = [
    ("Where are you now?", ["Inside the U.S.", "Outside the U.S."], "where"),
    ("Were you born outside the United States?", ["Yes", "No"], "born_abroad"),
    ("Are you under 18 years old?", ["Yes", "No"], "under_18"),
    ("Do you have a U.S. citizen spouse?", ["Yes", "No"], "usc_spouse"),
    ("Do you have a U.S. citizen parent?", ["Yes", "No"], "usc_parent"),
    ("Do you have a U.S. citizen son/daughter age 21 or older?", ["Yes", "No"], "usc_child21"),
    ("Was at least one parent a U.S. citizen at the time of your birth?", ["Yes", "No", "Not sure"], "parent_citizen_at_birth"),
    ("Did that parent meet the physical presence requirement before your birth?", ["Yes", "No", "Not sure"], "parent_pres_req"),
    ("Did a parent become a U.S. citizen after your birth?", ["Yes", "No"], "parent_natz_after"),
]
total_steps = len(questions)

# ===== Progress =====
if 1 <= st.session_state.step <= total_steps:
    cur = st.session_state.step
    st.write(t["progress"].format(cur=cur, total=total_steps))
    st.progress((cur - 1) / total_steps)

# ===== One-question-at-a-time UI with Back/Next =====
if 1 <= st.session_state.step <= total_steps:
    q_text, options, key = questions[st.session_state.step - 1]

    # Restore prior answer if present
    prev = st.session_state.answers.get(key)
    if prev in options:
        try:
            idx = options.index(prev)
            choice = st.radio(q_text, options, index=idx, key=f"q_{key}")
        except ValueError:
            choice = st.radio(q_text, options, key=f"q_{key}")
    else:
        choice = st.radio(q_text, options, key=f"q_{key}")

    # Buttons row
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["back"], use_container_width=True):
            if st.session_state.step > 1:
                # persist current selection before going back
                st.session_state.answers[key] = st.session_state.get(f"q_{key}", prev)
                st.session_state.step -= 1
                st.experimental_rerun()
    with c2:
        if st.button(t["next"], use_container_width=True):
            # require a selection; radio always has one
            st.session_state.answers[key] = st.session_state.get(f"q_{key}", choice)
            if st.session_state.step < total_steps:
                st.session_state.step += 1
                st.experimental_rerun()
            else:
                # finished last question
                st.session_state.step = total_steps + 1
                st.experimental_rerun()

# ===== Results =====
if st.session_state.step > total_steps:
    answers = st.session_state.answers
    routes, notes = [], []

    # Routing logic (concise, informational)
    if answers.get("born_abroad") == "No":
        routes.append("Born in the U.S. → likely U.S. citizen by birth (state birth certificate / U.S. passport).")
    else:
        # Citizenship at birth
        if answers.get("parent_citizen_at_birth") == "Yes" and answers.get("parent_pres_req") == "Yes":
            if answers.get("under_18") == "Yes" and answers.get("where") == "Outside the U.S.":
                routes.append("CRBA (citizenship at birth; apply at U.S. Embassy/Consulate) + first U.S. passport.")
            else:
                routes.append("N-600 (proof of citizenship) if citizenship was acquired at birth.")
        # Derivation after birth
        if answers.get("parent_natz_after") == "Yes" and answers.get("under_18") == "Yes" and answers.get("where") == "Inside the U.S.":
            routes.append("N-600 (derivation under INA §320 if child is LPR and in legal/physical custody of U.S. citizen parent).")
        # Family petition fallback
        if not routes:
            if any(answers.get(k) == "Yes" for k in ("usc_spouse", "usc_parent", "usc_child21")):
                routes.append("I-130 family petition (then consular processing or adjustment when eligible).")
            else:
                notes.append("No clear family-based path indicated; consider employment or humanitarian categories.")

    st.subheader(t["results"])
    if routes:
        st.success(t["routes_label"])
        for r in routes:
            st.write(f"- {r}")
    else:
        st.warning(t["no_route"])

    if notes:
        st.info(t["notes_label"])
        for n in notes:
            st.write(f"- {n}")

    # PDF + Mailto
    pdf_bytes = make_pdf_bytes(answers, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes,
                       file_name="screener_summary.pdf", mime="application/pdf")

    subject = urllib.parse.quote("Screener Results")
    body_lines = [f"{k}: {v}" for k, v in answers.items()]
    if routes:
        body_lines += ["", "Possible routes:"]
        body_lines += [f"- {r}" for r in routes]
    if notes:
        body_lines += ["", "Notes:"]
        body_lines += [f"- {n}" for n in notes]
    body_lines += ["", TEXT[lang]["admin_note"]]
    body = urllib.parse.quote("\n".join(body_lines)[:1500])
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")

    # Allow going back from results if needed
    if st.button(t["back"]):
        st.session_state.step = total_steps
        st.experimental_rerun()
