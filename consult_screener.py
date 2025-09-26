# consult_screener_pdf.py
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import datetime
import urllib.parse

# ---------- Translations ----------
TEXT = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": (
            "**Disclaimer:** This tool is for informational purposes only. "
            "It does not provide legal advice, does not create an attorney-client relationship, "
            "and should not be relied on as a substitute for advice from a licensed immigration attorney."
        ),
        "lang_prompt": "Choose language / Elija idioma / Escolha idioma",
        "name": "Full name (optional)",
        "email": "Email (optional, for follow-up)",
        "start": "Start intake",
        "where": "Where are you now?",
        "inside": "Inside the U.S.",
        "outside": "Outside the U.S.",
        "born_abroad": "Were you born outside the United States?",
        "under_18": "Are you under 18 years old?",
        "usc_spouse": "Do you have a U.S. citizen spouse?",
        "usc_parent": "Do you have a U.S. citizen parent?",
        "usc_child21": "Do you have a U.S. citizen son/daughter age 21 or older?",
        "parent_citizen_at_birth": "Was at least one parent a U.S. citizen at the time of your birth?",
        "parent_pres_req": "Did that parent meet the U.S. physical presence requirement before the birth? (If unsure, choose 'Not sure')",
        "not_sure": "Not sure",
        "parent_natz_after": "Did a parent become a U.S. citizen after your birth?",
        "lawful_entry": "Was your most recent U.S. entry inspected by an officer (visa/parole/inspection)?",
        "current_status": "If inside the U.S., current status (select one)",
        "no_status": "No valid status",
        "inadmiss_flags": "Any of these apply? (select if apply)",
        "overstay": "Overstay / Unlawful presence",
        "removal": "Prior removal/deportation",
        "criminal": "Certain criminal history",
        "fraud": "Fraud / misrepresentation",
        "determine": "Show possible routes (informational only)",
        "results": "Informational Results",
        "pdf_btn": "Download PDF summary",
        "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this PDF or email to the administrator or the person who provided you this form.",
        "no_route": "No clear route identified based on inputs. Further review with counsel recommended.",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
    },
    "es": {
        "title": "Evaluador de Consulta de Inmigración",
        "disclaimer": (
            "**Aviso:** Esta herramienta es solo para información general. "
            "No ofrece asesoría legal, no crea una relación abogado-cliente y no debe usarse "
            "como sustituto de la asesoría de un abogado de inmigración autorizado."
        ),
        "lang_prompt": "Elija idioma / Choose language / Escolha idioma",
        "name": "Nombre completo (opcional)",
        "email": "Correo electrónico (opcional, para seguimiento)",
        "start": "Iniciar",
        "where": "¿Dónde se encuentra ahora?",
        "inside": "Dentro de EE. UU.",
        "outside": "Fuera de EE. UU.",
        "born_abroad": "¿Nació fuera de los Estados Unidos?",
        "under_18": "¿Tiene menos de 18 años?",
        "usc_spouse": "¿Tiene cónyuge ciudadano estadounidense?",
        "usc_parent": "¿Tiene padre/madre ciudadano(a) de EE. UU.?",
        "usc_child21": "¿Tiene hijo(a) ciudadano(a) de EE. UU. mayor de 21 años?",
        "parent_citizen_at_birth": "¿Algún progenitor era ciudadano(a) de EE. UU. en el momento de su nacimiento?",
        "parent_pres_req": "¿Ese progenitor cumplió el requisito de presencia física en EE. UU. antes del nacimiento? (Si no está seguro, elija 'No seguro')",
        "not_sure": "No seguro",
        "parent_natz_after": "¿Algún progenitor se naturalizó después de su nacimiento?",
        "lawful_entry": "¿Su ingreso más reciente a EE. UU. fue inspeccionado por un oficial (visa/parole/inspección)?",
        "current_status": "Si está en EE. UU., estatus actual (seleccione uno)",
        "no_status": "Sin estatus válido",
        "inadmiss_flags": "¿Alguno aplica? (marcar si aplica)",
        "overstay": "Permanencia ilegal / Overstay",
        "removal": "Expulsión/retorno previo",
        "criminal": "Ciertos antecedentes penales",
        "fraud": "Fraude / tergiversación",
        "determine": "Mostrar rutas posibles (solo informativo)",
        "results": "Resultados informativos",
        "pdf_btn": "Descargar resumen en PDF",
        "mailto_btn": "Abrir correo para enviar resumen",
        "admin_note": "Por favor envíe este PDF o correo al administrador o a la persona que le proporcionó este formulario.",
        "no_route": "No hay una ruta clara con base en las respuestas. Se recomienda revisión con asesoría.",
        "routes_label": "Rutas posibles para explorar",
        "notes_label": "Notas",
    },
    "pt": {
        "title": "Triagem de Consulta de Imigração",
        "disclaimer": (
            "**Aviso:** Esta ferramenta é apenas para fins informativos. "
            "Não fornece consultoria jurídica, não cria relação advogado-cliente e não deve substituir "
            "a orientação de um advogado de imigração licenciado."
        ),
        "lang_prompt": "Escolha idioma / Choose language / Elija idioma",
        "name": "Nome completo (opcional)",
        "email": "E-mail (opcional, para acompanhamento)",
        "start": "Iniciar",
        "where": "Onde você está agora?",
        "inside": "Dentro dos EUA",
        "outside": "Fora dos EUA",
        "born_abroad": "Você nasceu fora dos Estados Unidos?",
        "under_18": "Você tem menos de 18 anos?",
        "usc_spouse": "Você tem cônjuge cidadão dos EUA?",
        "usc_parent": "Você tem pai/mãe cidadão(a) dos EUA?",
        "usc_child21": "Você tem filho(a) cidadão(a) dos EUA com 21 anos ou mais?",
        "parent_citizen_at_birth": "Algum dos pais era cidadão dos EUA no momento do seu nascimento?",
        "parent_pres_req": "Esse pai/mãe cumpriu o requisito de presença física nos EUA antes do nascimento? (Se não souber, escolha 'Não sei')",
        "not_sure": "Não sei",
        "parent_natz_after": "Algum dos pais se naturalizou após o seu nascimento?",
        "lawful_entry": "Sua entrada mais recente nos EUA foi inspecionada por um oficial (visto/parole/inspeção)?",
        "current_status": "Se estiver nos EUA, status atual (selecione um)",
        "no_status": "Sem status válido",
        "inadmiss_flags": "Algum dos itens se aplica? (marque os que aplicam)",
        "overstay": "Permanência ilegal",
        "removal": "Remoção/Deportação anterior",
        "criminal": "Histórico criminal relevante",
        "fraud": "Fraude / deturpação",
        "determine": "Mostrar rotas possíveis (somente informativo)",
        "results": "Resultados informativos",
        "pdf_btn": "Baixar resumo em PDF",
        "mailto_btn": "Abrir e-mail para enviar resumo",
        "admin_note": "Por favor envie este PDF ou e-mail ao administrador ou à pessoa que lhe forneceu este formulário.",
        "no_route": "Nenhuma rota clara identificada com base nas respostas. Recomenda-se revisão com um advogado.",
        "routes_label": "Rotas possíveis a explorar",
        "notes_label": "Observações",
    },
}

# ---------- Helpers ----------
def T(key):
    return text_map.get(key, key)

def make_pdf_bytes(client_name, client_email, answers, routes, notes, lang):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    title = TEXT[lang]["title"]
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"{TEXT[lang]['name']}: {client_name or 'N/A'}", styles["Normal"]))
    story.append(Paragraph(f"{TEXT[lang]['email']}: {client_email or 'N/A'}", styles["Normal"]))
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
    story.append(Spacer(1, 12))
    if notes:
        story.append(Paragraph(TEXT[lang]["notes_label"], styles["Heading2"]))
        for n in notes:
            story.append(Paragraph(f"- {n}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(TEXT[lang]["admin_note"], styles["Italic"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated: {datetime.datetime.utcnow().isoformat()} UTC", styles["Normal"]))
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

# ---------- UI ----------
st.set_page_config(page_title="Screener", layout="centered")
# language selector
lang = st.selectbox("Choose language / Elija idioma / Escolha idioma", ["English", "Español", "Português"])
lang_code = {"English": "en", "Español": "es", "Português": "pt"}[lang]
text_map = TEXT[lang_code]

st.title(text_map["title"])
st.markdown(text_map["disclaimer"])
st.markdown("---")

# optional client contact
client_name = st.text_input(text_map["name"])
client_email = st.text_input(text_map["email"])

# Start basic facts
where = st.radio(text_map["where"], [text_map["inside"], text_map["outside"]])

# Show next Qs conditionally
born_abroad = None
if st.checkbox(text_map["born_abroad"]):
    born_abroad = "Yes
