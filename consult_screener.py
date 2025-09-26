import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ===== Translations =====
TEXT = {
    "en": {
        # UI
        "title": "Immigration Consultation Screener",
        "disclaimer": ("**Disclaimer:** This tool is for informational purposes only. "
                       "It does not provide legal advice, does not create an attorney-client relationship, "
                       "and should not be relied on as a substitute for advice from a licensed immigration attorney."),
        "lang_prompt": "Choose language / Elija idioma / Escolha idioma",
        "start": "Start",
        "next": "Next",
        "back": "Back",
        "reset": "Reset",
        "results": "Informational Results",
        "answers_hdr": "Answers:",
        "pdf_btn": "Download PDF summary",
        "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this PDF or email to the administrator or the person who provided you this form.",
        "no_route": "No clear route identified. Further review with counsel recommended.",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
        "progress": "Step {cur} of {total}",

        # Common options
        "Yes": "Yes",
        "No": "No",
        "Not sure": "Not sure",
        "InsideUS": "Inside the U.S.",
        "OutsideUS": "Outside the U.S.",

        # Questions
        "q_where": "Where are you now?",
        "q_born_abroad": "Were you born outside the United States?",
        "q_under_18": "Are you under 18 years old?",
        "q_usc_spouse": "Do you have a U.S. citizen spouse?",
        "q_usc_parent": "Do you have a U.S. citizen parent?",
        "q_usc_child21": "Do you have a U.S. citizen son/daughter age 21 or older?",
        "q_parent_citizen_at_birth": "Was at least one parent a U.S. citizen at the time of your birth?",
        "q_parent_pres_req": "Did that U.S. citizen parent meet U.S. physical presence before your birth?",
        "q_parent_natz_after": "Did a parent become a U.S. citizen after your birth?",

        # Result strings
        "r_us_born": "Born in the United States → likely U.S. citizen by birth (obtain state birth certificate and/or U.S. passport).",
        "r_crba": "CRBA (citizenship at birth; apply at U.S. Embassy/Consulate) and first U.S. passport.",
        "r_n600_birth": "N-600 (proof of citizenship) if citizenship was acquired at birth.",
        "r_n600_320": "N-600 (derivation under INA §320 if the child is an LPR and resides in the legal and physical custody of the U.S. citizen parent).",
        "r_i130": "I-130 family petition (then consular processing or adjustment when eligible).",
        "n_no_family": "No clear family-based path indicated; consider employment or humanitarian categories.",
        "n_inadmiss": "Potential inadmissibility noted; waivers (I-601/I-601A) or other remedies may be required depending on facts.",
        "routes_hdr_mail": "Possible routes:",
        "notes_hdr_mail": "Notes:",
        "mail_subject": "Screener Results",
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
        "reset": "Reiniciar",
        "results": "Resultados informativos",
        "answers_hdr": "Respuestas:",
        "pdf_btn": "Descargar resumen en PDF",
        "mailto_btn": "Abrir correo para enviar resumen",
        "admin_note": "Por favor envíe este PDF o correo al administrador o a la persona que le proporcionó este formulario.",
        "no_route": "No hay una ruta clara según sus respuestas. Se recomienda revisión con abogado.",
        "routes_label": "Rutas posibles para explorar",
        "notes_label": "Notas",
        "progress": "Paso {cur} de {total}",

        "Yes": "Sí",
        "No": "No",
        "Not sure": "No seguro",
        "InsideUS": "Dentro de EE. UU.",
        "OutsideUS": "Fuera de EE. UU.",

        "q_where": "¿Dónde se encuentra ahora?",
        "q_born_abroad": "¿Nació fuera de los Estados Unidos?",
        "q_under_18": "¿Tiene menos de 18 años?",
        "q_usc_spouse": "¿Tiene cónyuge ciudadano estadounidense?",
        "q_usc_parent": "¿Tiene padre/madre ciudadano(a) de EE. UU.?",
        "q_usc_child21": "¿Tiene hijo(a) ciudadano(a) de EE. UU. mayor de 21 años?",
        "q_parent_citizen_at_birth": "¿Algún progenitor era ciudadano de EE. UU. en el momento de su nacimiento?",
        "q_parent_pres_req": "¿Ese progenitor cumplió presencia física en EE. UU. antes de su nacimiento?",
        "q_parent_natz_after": "¿Algún progenitor se naturalizó después de su nacimiento?",

        "r_us_born": "Nacido en Estados Unidos → probablemente ciudadano por nacimiento (obtenga acta de nacimiento estatal y/o pasaporte estadounidense).",
        "r_crba": "CRBA (ciudadanía al nacer; solicítelo en Embajada/Consulado de EE. UU.) y primer pasaporte estadounidense.",
        "r_n600_birth": "N-600 (prueba de ciudadanía) si hubo ciudadanía al nacer.",
        "r_n600_320": "N-600 (derivación bajo INA §320 si el menor es residente permanente y vive bajo custodia legal y física del padre/madre ciudadano).",
        "r_i130": "I-130 (petición familiar) y luego proceso consular o ajuste cuando sea elegible.",
        "n_no_family": "No se identifica vía familiar clara; considere categorías laborales o humanitarias.",
        "n_inadmiss": "Posible inadmisibilidad; pueden requerirse perdones (I-601/I-601A) u otros remedios según los hechos.",
        "routes_hdr_mail": "Rutas posibles:",
        "notes_hdr_mail": "Notas:",
        "mail_subject": "Resultados del evaluador",
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
        "reset": "Reiniciar",
        "results": "Resultados informativos",
        "answers_hdr": "Respostas:",
        "pdf_btn": "Baixar resumo em PDF",
        "mailto_btn": "Abrir e-mail para enviar resumo",
        "admin_note": "Envie este PDF ou e-mail ao administrador ou à pessoa que lhe forneceu este formulário.",
        "no_route": "Nenhuma rota clara identificada. Recomenda-se revisão com advogado.",
        "routes_label": "Rotas possíveis para explorar",
        "notes_label": "Observações",
        "progress": "Etapa {cur} de {total}",

        "Yes": "Sim",
        "No": "Não",
        "Not sure": "Não sei",
        "InsideUS": "Dentro dos EUA",
        "OutsideUS": "Fora dos EUA",

        "q_where": "Onde você está agora?",
        "q_born_abroad": "Você nasceu fora dos Estados Unidos?",
        "q_under_18": "Você tem menos de 18 anos?",
        "q_usc_spouse": "Você tem cônjuge cidadão dos EUA?",
        "q_usc_parent": "Você tem pai/mãe cidadão(ã) dos EUA?",
        "q_usc_child21": "Você tem filho(a) cidadão(ã) dos EUA com 21 anos ou mais?",
        "q_parent_citizen_at_birth": "Algum dos pais era cidadão dos EUA no momento do seu nascimento?",
        "q_parent_pres_req": "Esse pai/mãe cumpriu presença física nos EUA antes do seu nascimento?",
        "q_parent_natz_after": "Algum dos pais se naturalizou após o seu nascimento?",

        "r_us_born": "Nascido nos Estados Unidos → provavelmente cidadão por nascimento (obter certidão estadual e/ou passaporte dos EUA).",
        "r_crba": "CRBA (cidadania ao nascer; solicite na Embaixada/Consulado dos EUA) e primeiro passaporte dos EUA.",
        "r_n600_birth": "N-600 (prova de cidadania) se houve cidadania ao nascer.",
        "r_n600_320": "N-600 (derivação pelo INA §320 se o menor é residente permanente e vive sob custódia legal e física do pai/mãe cidadão).",
        "r_i130": "I-130 (petição familiar) e depois processamento consular ou ajuste quando elegível.",
        "n_no_family": "Nenhuma via familiar clara identificada; considere categorias de trabalho ou humanitárias.",
        "n_inadmiss": "Possível inadmissibilidade; podem ser necessários perdões (I-601/I-601A) ou outras medidas conforme os fatos.",
        "routes_hdr_mail": "Rotas possíveis:",
        "notes_hdr_mail": "Observações:",
        "mail_subject": "Resultados da triagem",
    },
}

# ===== Helpers =====
def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()  # noqa

def make_pdf_bytes(answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(TEXT[lang]["title"], styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(TEXT[lang]["answers_hdr"], styles["Heading2"]))
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

# ===== App config =====
st.set_page_config(page_title="Screener", layout="centered")

# ===== State =====
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ===== Step 0: Language =====
if st.session_state.step == 0:
    lang_choice = st.selectbox(
        "Choose language / Elija idioma / Escolha idioma",
        ["English", "Español", "Português"]
    )
    st.session_state.lang = {"English": "en", "Español": "es", "Português": "pt"}[lang_choice]
    if st.button(TEXT[st.session_state.lang]["start"]):
        st.session_state.step = 1
        rerun()

lang = st.session_state.lang
t = TEXT[lang]

# ===== Disclaimer =====
st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

# ===== Questions (localized) =====
Q = [
    (t["q_where"],            [t["InsideUS"], t["OutsideUS"]],          "where"),
    (t["q_born_abroad"],      [t["Yes"], t["No"]],                      "born_abroad"),
    (t["q_under_18"],         [t["Yes"], t["No"]],                      "under_18"),
    (t["q_usc_spouse"],       [t["Yes"], t["No"]],                      "usc_spouse"),
    (t["q_usc_parent"],       [t["Yes"], t["No"]],                      "usc_parent"),
    (t["q_usc_child21"],      [t["Yes"], t["No"]],                      "usc_child21"),
    (t["q_parent_citizen_at_birth"], [t["Yes"], t["No"], t["Not sure"]], "parent_citizen_at_birth"),
    (t["q_parent_pres_req"],  [t["Yes"], t["No"], t["Not sure"]],       "parent_pres_req"),
    (t["q_parent_natz_after"],[t["Yes"], t["No"]],                      "parent_natz_after"),
]
TOTAL = len(Q)

# ===== Progress =====
if 1 <= st.session_state.step <= TOTAL:
    cur = st.session_state.step
    st.write(t["progress"].format(cur=cur, total=TOTAL))
    st.progress((cur - 1) / TOTAL)

# ===== Navigation =====
def goto(delta):
    st.session_state.step = max(1, min(TOTAL + 1, st.session_state.step + delta))
    rerun()

if 1 <= st.session_state.step <= TOTAL:
    label, opts, key = Q[st.session_state.step - 1]
    saved = st.session_state.answers.get(key)
    idx = opts.index(saved) if saved in opts else 0
    choice = st.radio(label, opts, index=idx, key=f"q_{key}")

    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button(t["back"], disabled=(st.session_state.step == 1), use_container_width=True):
            st.session_state.answers[key] = st.session_state.get(f"q_{key}", choice)
            goto(-1)
    with c2:
        if st.button(t["reset"], use_container_width=True):
            st.session_state.answers = {}
            st.session_state.step = 0
            rerun()
    with c3:
        if st.button(t["next"], use_container_width=True):
            st.session_state.answers[key] = st.session_state.get(f"q_{key}", choice)
            goto(+1)

# ===== Results (localized strings) =====
if st.session_state.step > TOTAL:
    a = st.session_state.answers
    routes, notes = [], []

    def is_yes(v):  return v == t["Yes"]
    def is_no(v):   return v == t["No"]
    def is_inside(v): return v == t["InsideUS"]
    def is_outside(v): return v == t["OutsideUS"]

    if is_no(a.get("born_abroad", t["No"])):
        routes.append(t["r_us_born"])
    else:
        if is_yes(a.get("parent_citizen_at_birth", t["No"])) and is_yes(a.get("parent_pres_req", t["No"])):
            if is_yes(a.get("under_18", t["No"])) and is_outside(a.get("where", t["OutsideUS"])):
                routes.append(t["r_crba"])
            else:
                routes.append(t["r_n600_birth"])
        if is_yes(a.get("parent_natz_after", t["No"])) and is_yes(a.get("under_18", t["No"])) and is_inside(a.get("where", t["InsideUS"])):
            routes.append(t["r_n600_320"])
        if not routes:
            if any(is_yes(a.get(k, t["No"])) for k in ("usc_spouse", "usc_parent", "usc_child21")):
                routes.append(t["r_i130"])
            else:
                notes.append(t["n_no_family"])

    # Example inadmissibility note hook (if you later add flags)
    # notes.append(t["n_inadmiss"])

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
    pdf_bytes = make_pdf_bytes(a, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes, file_name="screener_summary.pdf", mime="application/pdf")

    subject = urllib.parse.quote(TEXT[lang]["mail_subject"])
    lines = [f"{k}: {v}" for k, v in a.items()]
    if routes:
        lines += ["", TEXT[lang]["routes_hdr_mail"]] + [f"- {r}" for r in routes]
    if notes:
        lines += ["", TEXT[lang]["notes_hdr_mail"]] + [f"- {n}" for n in notes]
    lines += ["", TEXT[lang]["admin_note"]]
    body = urllib.parse.quote("\n".join(lines)[:1500])
    st.markdown(f"[{TEXT[lang]['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")

    c1, c2 = st.columns(2)
    with c1:
        if st.button(t["back"], use_container_width=True):
            st.session_state.step = TOTAL
            rerun()
    with c2:
        if st.button(t["reset"], use_container_width=True):
            st.session_state.answers = {}
            st.session_state.step = 0
            rerun()
