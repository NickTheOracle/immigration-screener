# consult_screener_pdf.py
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
        "name": "Full name (optional)",
        "email": "Email (optional, for follow-up)",
        "where": "Where are you now?",
        "inside": "Inside the U.S.",
        "outside": "Outside the U.S.",
        "born_abroad": "Were you born outside the United States?",
        "under_18": "Are you under 18 years old?",
        "usc_spouse": "Do you have a U.S. citizen spouse?",
        "lpr_spouse": "Do you have a lawful permanent resident (green card holder) spouse?",
        "usc_parent": "Do you have a U.S. citizen parent?",
        "usc_child21": "Do you have a U.S. citizen son/daughter age 21 or older?",
        "parent_citizen_at_birth": "Was at least one parent a U.S. citizen at the time of your birth?",
        "parent_pres_req": "Did that U.S. citizen parent meet U.S. physical presence/residence before your birth?",
        "not_sure": "Not sure",
        "parent_natz_after": "Did a parent become a U.S. citizen after your birth?",
        "lawful_entry": "Was your most recent U.S. entry inspected (visa/parole/wave-through)?",
        "current_status": "If inside the U.S., current status",
        "no_status": "No valid status",
        "inadmiss_flags": "Any of these apply? (select if applicable)",
        "overstay": "Overstay / Unlawful presence",
        "removal": "Prior removal/deportation",
        "criminal": "Certain criminal history",
        "fraud": "Fraud / Misrepresentation",
        "determine": "Show possible routes (informational only)",
        "results": "Informational Results",
        "pdf_btn": "Download PDF summary",
        "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this PDF or email to the administrator or the person who provided you this form.",
        "no_route": "No clear route identified based on inputs. Further review with counsel recommended.",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
        "is_lpr_q": "Does the child have lawful permanent resident (green card) status?",
        "custody_q": "Is the child living in the legal and physical custody of a U.S. citizen parent?",
    },
    "es": {
        "title": "Evaluador de Consulta de Inmigración",
        "disclaimer": ("**Aviso:** Esta herramienta es solo para información general. "
                       "No ofrece asesoría legal, no crea una relación abogado-cliente y no debe usarse "
                       "como sustituto de la asesoría de un abogado de inmigración autorizado."),
        "lang_prompt": "Elija idioma / Choose language / Escolha idioma",
        "name": "Nombre completo (opcional)",
        "email": "Correo electrónico (opcional, para seguimiento)",
        "where": "¿Dónde se encuentra ahora?",
        "inside": "Dentro de EE. UU.",
        "outside": "Fuera de EE. UU.",
        "born_abroad": "¿Nació fuera de los Estados Unidos?",
        "under_18": "¿Tiene menos de 18 años?",
        "usc_spouse": "¿Tiene cónyuge ciudadano estadounidense?",
        "lpr_spouse": "¿Tiene cónyuge residente permanente (green card)?",
        "usc_parent": "¿Tiene padre/madre ciudadano(a) de EE. UU.?",
        "usc_child21": "¿Tiene hijo(a) ciudadano(a) de EE. UU. mayor de 21 años?",
        "parent_citizen_at_birth": "¿Algún progenitor era ciudadano(a) de EE. UU. en el momento de su nacimiento?",
        "parent_pres_req": "¿Ese progenitor cumplió presencia física/residencia en EE. UU. antes de su nacimiento?",
        "not_sure": "No seguro",
        "parent_natz_after": "¿Algún progenitor se naturalizó después de su nacimiento?",
        "lawful_entry": "¿Su ingreso más reciente fue inspeccionado (visa/parole/paso permitido)?",
        "current_status": "Si está en EE. UU., estatus actual",
        "no_status": "Sin estatus válido",
        "inadmiss_flags": "¿Alguno de estos aplica? (seleccione si aplica)",
        "overstay": "Permanencia ilegal / Overstay",
        "removal": "Expulsión/deportación previa",
        "criminal": "Ciertos antecedentes penales",
        "fraud": "Fraude / tergiversación",
        "determine": "Mostrar rutas posibles (solo informativo)",
        "results": "Resultados informativos",
        "pdf_btn": "Descargar resumen en PDF",
        "mailto_btn": "Abrir correo para enviar resumen",
        "admin_note": "Por favor envíe este PDF o correo al administrador o a quien le dio este formulario.",
        "no_route": "No hay ruta clara según sus respuestas. Se recomienda revisión con abogado.",
        "routes_label": "Rutas posibles para explorar",
        "notes_label": "Notas",
        "is_lpr_q": "¿El menor tiene estatus de residente permanente (green card)?",
        "custody_q": "¿El menor vive bajo custodia legal y física de un padre ciudadano estadounidense?",
    },
    "pt": {
        "title": "Triagem de Consulta de Imigração",
        "disclaimer": ("**Aviso:** Esta ferramenta é apenas para fins informativos. "
                       "Não fornece aconselhamento jurídico, não cria relação advogado-cliente e não substitui "
                       "a orientação de um advogado de imigração licenciado."),
        "lang_prompt": "Escolha idioma / Choose language / Elija idioma",
        "name": "Nome completo (opcional)",
        "email": "E-mail (opcional, para acompanhamento)",
        "where": "Onde você está agora?",
        "inside": "Dentro dos EUA",
        "outside": "Fora dos EUA",
        "born_abroad": "Você nasceu fora dos Estados Unidos?",
        "under_18": "Você tem menos de 18 anos?",
        "usc_spouse": "Você tem cônjuge cidadão dos EUA?",
        "lpr_spouse": "Você tem cônjuge residente permanente (green card)?",
        "usc_parent": "Você tem pai/mãe cidadão(ã) dos EUA?",
        "usc_child21": "Você tem filho(a) cidadão(ã) dos EUA com 21 anos ou mais?",
        "parent_citizen_at_birth": "Algum dos pais era cidadão dos EUA no momento do seu nascimento?",
        "parent_pres_req": "Esse pai/mãe cumpriu presença física/residência nos EUA antes do seu nascimento?",
        "not_sure": "Não sei",
        "parent_natz_after": "Algum dos pais se naturalizou após o seu nascimento?",
        "lawful_entry": "Sua entrada mais recente foi inspecionada (visto/parole/liberação)?",
        "current_status": "Se está nos EUA, status atual",
        "no_status": "Sem status válido",
        "inadmiss_flags": "Algum destes se aplica? (selecione se aplicável)",
        "overstay": "Permanência ilegal",
        "removal": "Remoção/Deportação anterior",
        "criminal": "Histórico criminal relevante",
        "fraud": "Fraude / deturpação",
        "determine": "Mostrar rotas possíveis (somente informativo)",
        "results": "Resultados informativos",
        "pdf_btn": "Baixar resumo em PDF",
        "mailto_btn": "Abrir e-mail para enviar resumo",
        "admin_note": "Envie este PDF ou e-mail ao administrador ou a quem lhe forneceu este formulário.",
        "no_route": "Nenhuma rota clara identificada. Recomenda-se revisão com advogado.",
        "routes_label": "Rotas possíveis para explorar",
        "notes_label": "Observações",
        "is_lpr_q": "O menor possui residência permanente (green card)?",
        "custody_q": "O menor vive sob custódia legal e física de um dos pais cidadão dos EUA?",
    },
}

# ===== PDF maker =====
def make_pdf_bytes(client_name, client_email, answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(TEXT[lang]["title"], styles["Title"]))
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

# ===== UI =====
st.set_page_config(page_title="Screener", layout="centered")

# Language
lang_label = "Choose language / Elija idioma / Escolha idioma"
lang_choice = st.selectbox(lang_label, ["English", "Español", "Português"])
lang = {"English": "en", "Español": "es", "Português": "pt"}[lang_choice]
t = TEXT[lang]

st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

# Contact (optional)
client_name = st.text_input(t["name"])
client_email = st.text_input(t["email"])

# Core starter Qs
where = st.radio(t["where"], [t["inside"], t["outside"]])
born_abroad = st.radio(t["born_abroad"], ["Yes", "No"])
under_18 = st.radio(t["under_18"], ["Yes", "No"])

# Show dependent blocks progressively
st.markdown("---")
st.subheader("Family / Citizenship Factors")

usc_spouse = st.radio(t["usc_spouse"], ["Yes", "No"])
lpr_spouse = st.radio(t["lpr_spouse"], ["Yes", "No"])
usc_parent = st.radio(t["usc_parent"], ["Yes", "No"])
usc_child21 = st.radio(t["usc_child21"], ["Yes", "No"])

parent_citizen_at_birth = t["not_sure"]
parent_pres_req = t["not_sure"]
if born_abroad == "Yes":
    parent_citizen_at_birth = st.radio(t["parent_citizen_at_birth"], ["Yes", "No", t["not_sure"]])
    if parent_citizen_at_birth in ["Yes", t["not_sure"]]:
        parent_pres_req = st.radio(t["parent_pres_req"], ["Yes", "No", t["not_sure"]])

parent_natz_after = st.radio(t["parent_natz_after"], ["Yes", "No"])

# U.S. entry/status only if inside U.S.
lawful_entry = "N/A"
current_status = "N/A"
inadmissibility = []
if where == t["inside"]:
    st.markdown("---")
    lawful_entry = st.radio(t["lawful_entry"], ["Yes", "No", "N/A"])
    current_status = st.selectbox(t["current_status"], ["USC/LPR", "Nonimmigrant", t["no_status"]])
    inadmissibility = st.multiselect(t["inadmiss_flags"], [t["overstay"], t["removal"], t["criminal"], t["fraud"]])

# Derivation (only relevant if under 18 and inside U.S.)
is_LPR = "N/A"
living_with_citizen_parent = "N/A"
if under_18 == "Yes" and where == t["inside"]:
    st.markdown("---")
    is_LPR = st.radio(t["is_lpr_q"], ["Yes", "No"])
    living_with_citizen_parent = st.radio(t["custody_q"], ["Yes", "No"])

st.markdown("---")

if st.button(t["determine"]):
    # Collect answers
    answers = {
        t["where"]: where,
        t["born_abroad"]: born_abroad,
        t["under_18"]: under_18,
        t["usc_spouse"]: usc_spouse,
        t["lpr_spouse"]: lpr_spouse,
        t["usc_parent"]: usc_parent,
        t["usc_child21"]: usc_child21,
        t["parent_citizen_at_birth"]: parent_citizen_at_birth,
        t["parent_pres_req"]: parent_pres_req,
        t["parent_natz_after"]: parent_natz_after,
        t["lawful_entry"]: lawful_entry,
        t["current_status"]: current_status,
        t["inadmiss_flags"]: ", ".join(inadmissibility) if inadmissibility else "None",
        "LPR?": is_LPR,
        "Custody with USC parent?": living_with_citizen_parent,
    }

    routes, notes = [], []

    # U.S.-born
    if born_abroad == "No":
        routes.append("Born in the U.S. → likely U.S. citizen by birth (provide state birth certificate/U.S. passport).")
    else:
        # Citizenship at birth
        if parent_citizen_at_birth == "Yes" and parent_pres_req == "Yes":
            if where == t["outside"] and under_18 == "Yes":
                routes.append("CRBA + first U.S. passport at U.S. Embassy/Consulate (citizenship at birth).")
            elif where == t["inside"]:
                routes.append("N-600 (proof of citizenship) if citizenship was acquired at birth.")
            else:
                routes.append("Outside U.S. and 18+: apply for U.S. passport abroad with evidence of citizenship at birth (CRBA unavailable after 18).")
        elif parent_citizen_at_birth in ["Yes", t["not_sure"]] and parent_pres_req == t["not_sure"]:
            notes.append("If the U.S. citizen parent met pre-birth physical presence, citizenship at birth may apply (CRBA if <18 abroad; N-600/passport if in the U.S.). Gather parent’s presence evidence.")

        # Derivation (INA §320)
        if parent_natz_after == "Yes":
            if where == t["inside"] and under_18 == "Yes" and is_LPR == "Yes" and living_with_citizen_parent == "Yes":
                routes.append("N-600 (derivation under INA §320).")
            else:
                notes.append("For derivation under INA §320, child must be LPR, under 18, and residing in the U.S. in legal/physical custody of the U.S. citizen parent.")

        # Family petition fallback
        if not routes:
            if usc_spouse == "Yes" or lpr_spouse == "Yes" or usc_parent == "Yes" or usc_child21 == "Yes":
                routes.append("I-130 family petition (then consular processing or adjustment when eligible).")
            else:
                notes.append("No qualifying immediate family relationship indicated; consider employment or humanitarian categories.")

    if inadmissibility:
        notes.append("Potential inadmissibility noted; waivers (I-601/I-601A) or other remedies may be required depending on facts.")

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

    # PDF download
    pdf_bytes = make_pdf_bytes(client_name, client_email, answers, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes,
                       file_name=f"screener_{(client_name or 'client').replace(' ', '_')}.pdf",
                       mime="application/pdf")

    # mailto link
    subject = urllib.parse.quote(f"Screener Results - {(client_name or 'Client')}")
    lines = [f"{k}: {v}" for k, v in answers.items()]
    if routes:
        lines += ["", "Possible routes:"]
        lines += [f"- {r}" for r in routes]
    if notes:
        lines += ["", "Notes:"]
        lines += [f"- {n}" for n in notes]
    lines += ["", t["admin_note"]]
    body = urllib.parse.quote("\n".join(lines)[:1500])
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")
