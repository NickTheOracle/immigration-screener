import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# =========================== TRANSLATIONS ===========================
T = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": ("**Disclaimer:** Informational only. Not legal advice. "
                       "No attorney–client relationship is created."),
        "start": "Start", "next": "Next", "back": "Back", "reset": "Reset",
        "progress": "Step {cur} of {total}",
        "results": "Informational Results",
        "answers_hdr": "Answers:",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
        "no_route": "No clear route identified. Further review recommended.",
        "pdf_btn": "Download PDF summary", "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this summary to the administrator or the person who gave you this form.",
        "mail_subject": "Screener Results",

        # Common options
        "Yes":"Yes","No":"No","Not sure":"Not sure",
        "InsideUS":"Inside the U.S.","OutsideUS":"Outside the U.S.",
        "Single":"Single","Married":"Married","Divorced":"Divorced",
        "Never":"Never","Once":"Once","MoreThanOnce":"More than once",
        "Less6":"< 6 months","_6_12":"6–12 months","_12_36":"1–3 years","_3_10":"3–10 years","_10plus":"10+ years",

        # Questions (labels)
        "q_lang":"Choose language / Elija idioma / Escolha idioma",
        "q_where":"Where are you now?",
        "q_born_abroad":"Were you born outside the United States?",
        "q_lpr":"Are you a lawful permanent resident (green card holder)?",
        "q_lpr_years":"How long have you been an LPR?",
        "q_married_usc":"Are you married to a U.S. citizen and have you lived in marital union for 3+ years?",
        "q_continuous":"Have you maintained continuous residence (no 6+ month trips) during the eligibility period?",
        "q_trips6":"Have you had any single trip outside the U.S. of 6 months or more during that period?",
        "q_good_moral":"Any arrests/convictions in the last 5 years?",
        "q_selective":"If male and 18–26 during presence in U.S., registered for Selective Service?",
        "q_under_18":"Are you under 18 years old?",
        "q_parent_citizen_birth":"Was a parent a U.S. citizen at your birth?",
        "q_parent_presence_met":"Did that parent meet U.S. physical presence before your birth?",
        "q_parent_natz_after":"Did a parent naturalize after your birth?",
        "q_live_with_usc_parent":"Are/were you residing in the legal and physical custody of the U.S. citizen parent?",
        "q_is_LPR_child":"Do you (the child) have LPR status?",
        "q_family_heads":"Which U.S. relatives do you have? (select all that apply)",
        "opt_spouseUSC":"Spouse is U.S. citizen",
        "opt_spouseLPR":"Spouse is LPR",
        "opt_parentUSC":"Parent is U.S. citizen",
        "opt_child21USC":"U.S. citizen son/daughter age 21+",
        "opt_siblingUSC":"U.S. citizen brother/sister",
        "opt_none":"None",
        "q_pd_current":"If any petition is approved, is the priority date current on the Visa Bulletin?",
        "q_time_out":"How long have you been outside the U.S. in your most recent continuous period?",
        "q_prior_removal":"Were you ever removed/deported or did you take voluntary departure after proceedings?",
        "q_illegal_reentry":"After removal or >1 year unlawful presence, did you re-enter/attempt to re-enter illegally?",
        "q_unlawful_presence":"Before you last departed, did you accrue 180+ days of unlawful presence?",
        "q_lawful_entry_last":"Was your last U.S. entry inspected/paroled (visa, wave-through, parole)?",
        "q_crim_fraud":"Any criminal issues or fraud/misrepresentation in immigration applications?",
        "q_fear":"Do you fear harm if returned to your home country, or have you suffered past persecution?",
        "q_one_year":"If inside the U.S., did you enter less than 1 year ago? (or do you have an exception to the 1-year asylum filing rule)",
        "q_u_victim":"Were you a victim of certain crimes in the U.S. (e.g., DV, assault, trafficking, etc.)?",
        "q_u_harm":"Did you suffer substantial physical or mental harm from that crime?",
        "q_u_report":"Did you report to police or other authorities, and are/were you helpful/cooperating?",
    },
    "es": {
        "title":"Evaluador de Consulta de Inmigración",
        "disclaimer":"**Aviso:** Solo informativo. No es asesoría legal. No crea relación abogado-cliente.",
        "start":"Iniciar","next":"Siguiente","back":"Atrás","reset":"Reiniciar",
        "progress":"Paso {cur} de {total}",
        "results":"Resultados informativos",
        "answers_hdr":"Respuestas:",
        "routes_label":"Rutas posibles para explorar",
        "notes_label":"Notas",
        "no_route":"No hay ruta clara. Se recomienda revisión adicional.",
        "pdf_btn":"Descargar PDF","mailto_btn":"Abrir correo para enviar resumen",
        "admin_note":"Por favor envíe este resumen al administrador o a la persona que le dio este formulario.",
        "mail_subject":"Resultados del evaluador",

        "Yes":"Sí","No":"No","Not sure":"No seguro",
        "InsideUS":"Dentro de EE. UU.","OutsideUS":"Fuera de EE. UU.",
        "Single":"Soltero(a)","Married":"Casado(a)","Divorced":"Divorciado(a)",
        "Never":"Nunca","Once":"Una vez","MoreThanOnce":"Más de una vez",
        "Less6":"< 6 meses","_6_12":"6–12 meses","_12_36":"1–3 años","_3_10":"3–10 años","_10plus":"10+ años",

        "q_lang":"Elija idioma / Choose language / Escolha idioma",
        "q_where":"¿Dónde se encuentra ahora?",
        "q_born_abroad":"¿Nació fuera de los Estados Unidos?",
        "q_lpr":"¿Es residente permanente (green card)?",
        "q_lpr_years":"¿Desde cuándo es residente permanente?",
        "q_married_usc":"¿Está casado(a) con ciudadano(a) de EE. UU. y han vivido en unión matrimonial 3+ años?",
        "q_continuous":"¿Mantuvo residencia continua (sin viajes de 6+ meses) durante el período de elegibilidad?",
        "q_trips6":"¿Tuvo algún viaje único de 6+ meses durante ese período?",
        "q_good_moral":"¿Arrestos/condenas en los últimos 5 años?",
        "q_selective":"Si es hombre y tenía 18–26 años en EE. UU., ¿se registró para el Servicio Selectivo?",
        "q_under_18":"¿Tiene menos de 18 años?",
        "q_parent_citizen_birth":"¿Algún padre era ciudadano de EE. UU. al momento de su nacimiento?",
        "q_parent_presence_met":"¿Ese padre cumplió presencia física en EE. UU. antes de su nacimiento?",
        "q_parent_natz_after":"¿Algún padre se naturalizó después de su nacimiento?",
        "q_live_with_usc_parent":"¿Reside/rió bajo custodia legal y física del padre/madre ciudadano?",
        "q_is_LPR_child":"¿El menor tiene estatus de residente permanente?",
        "q_family_heads":"¿Qué familiares tiene en EE. UU.? (seleccione los que apliquen)",
        "opt_spouseUSC":"Cónyuge ciudadano",
        "opt_spouseLPR":"Cónyuge residente (LPR)",
        "opt_parentUSC":"Padre/madre ciudadano",
        "opt_child21USC":"Hijo(a) ciudadano mayor de 21",
        "opt_siblingUSC":"Hermano(a) ciudadano",
        "opt_none":"Ninguno",
        "q_pd_current":"Si alguna petición está aprobada, ¿su fecha de prioridad está vigente en el Boletín de Visas?",
        "q_time_out":"¿Cuánto tiempo lleva fuera de EE. UU. en su período continuo más reciente?",
        "q_prior_removal":"¿Fue removido/deportado o salió con salida voluntaria tras proceso?",
        "q_illegal_reentry":"Tras remoción o >1 año de presencia ilegal, ¿reingresó/intentó reingresar ilegalmente?",
        "q_unlawful_presence":"Antes de salir la última vez, ¿acumuló 180+ días de presencia ilegal?",
        "q_lawful_entry_last":"¿Su última entrada fue inspeccionada/parole (visa, paso permitido, parole)?",
        "q_crim_fraud":"¿Algún problema penal o fraude/tergiversación en inmigración?",
        "q_fear":"¿Teme daños si regresa o sufrió persecución pasada?",
        "q_one_year":"Si está en EE. UU., ¿entró hace menos de 1 año? (o tiene una excepción a la regla de 1 año de asilo)",
        "q_u_victim":"¿Fue víctima de ciertos delitos en EE. UU. (violencia doméstica, asalto, trata, etc.)?",
        "q_u_harm":"¿Sufrió daño físico o mental sustancial por ese delito?",
        "q_u_report":"¿Denunció a la policía/autoridades y coopera/ó?",
    },
    "pt": {
        "title":"Triagem de Consulta de Imigração",
        "disclaimer":"**Aviso:** Somente informativo. Não é aconselhamento jurídico. Não cria relação advogado-cliente.",
        "start":"Iniciar","next":"Avançar","back":"Voltar","reset":"Reiniciar",
        "progress":"Etapa {cur} de {total}",
        "results":"Resultados informativos",
        "answers_hdr":"Respostas:",
        "routes_label":"Rotas possíveis para explorar",
        "notes_label":"Observações",
        "no_route":"Nenhuma rota clara. Recomenda-se análise adicional.",
        "pdf_btn":"Baixar PDF","mailto_btn":"Abrir e-mail para enviar resumo",
        "admin_note":"Envie este resumo ao administrador ou à pessoa que lhe forneceu este formulário.",
        "mail_subject":"Resultados da triagem",

        "Yes":"Sim","No":"Não","Not sure":"Não sei",
        "InsideUS":"Dentro dos EUA","OutsideUS":"Fora dos EUA",
        "Single":"Solteiro(a)","Married":"Casado(a)","Divorced":"Divorciado(a)",
        "Never":"Nunca","Once":"Uma vez","MoreThanOnce":"Mais de uma vez",
        "Less6":"< 6 meses","_6_12":"6–12 meses","_12_36":"1–3 anos","_3_10":"3–10 anos","_10plus":"10+ anos",

        "q_lang":"Escolha idioma / Choose language / Elija idioma",
        "q_where":"Onde você está agora?",
        "q_born_abroad":"Você nasceu fora dos Estados Unidos?",
        "q_lpr":"Você é residente permanente (green card)?",
        "q_lpr_years":"Há quanto tempo é residente permanente?",
        "q_married_usc":"É casado(a) com cidadão(ã) dos EUA e vive em união marital há 3+ anos?",
        "q_continuous":"Manteve residência contínua (sem viagens de 6+ meses) no período de elegibilidade?",
        "q_trips6":"Teve alguma viagem única de 6+ meses nesse período?",
        "q_good_moral":"Prendeu/condenações nos últimos 5 anos?",
        "q_selective":"Se homem e 18–26 nos EUA, registrou-se no Serviço Militar (Selective Service)?",
        "q_under_18":"Tem menos de 18 anos?",
        "q_parent_citizen_birth":"Algum dos pais era cidadão dos EUA no seu nascimento?",
        "q_parent_presence_met":"Esse pai/mãe cumpriu presença física nos EUA antes do seu nascimento?",
        "q_parent_natz_after":"Algum dos pais se naturalizou após o seu nascimento?",
        "q_live_with_usc_parent":"Reside(u) sob custódia legal e física do pai/mãe cidadão?",
        "q_is_LPR_child":"O menor possui status de residente permanente?",
        "q_family_heads":"Quais parentes você tem nos EUA? (selecione os aplicáveis)",
        "opt_spouseUSC":"Cônjuge cidadão",
        "opt_spouseLPR":"Cônjuge residente (LPR)",
        "opt_parentUSC":"Pai/mãe cidadão",
        "opt_child21USC":"Filho(a) cidadão com 21+",
        "opt_siblingUSC":"Irmão(ã) cidadão",
        "opt_none":"Nenhum",
        "q_pd_current":"Se alguma petição está aprovada, a data de prioridade já está atual no Visa Bulletin?",
        "q_time_out":"Há quanto tempo você está fora dos EUA no período contínuo mais recente?",
        "q_prior_removal":"Já foi removido/deportado ou saiu com saída voluntária após processo?",
        "q_illegal_reentry":"Após remoção ou >1 ano de presença ilegal, reentrou/tentou reentrar ilegalmente?",
        "q_unlawful_presence":"Antes de sair da última vez, acumulou 180+ dias de presença ilegal?",
        "q_lawful_entry_last":"Sua última entrada foi inspecionada/parole (visto, liberação, parole)?",
        "q_crim_fraud":"Algum problema penal ou fraude/deturpação em imigração?",
        "q_fear":"Tem medo de sofrer danos se retornar ou sofreu perseguição passada?",
        "q_one_year":"Se está nos EUA, entrou há menos de 1 ano? (ou possui exceção à regra de 1 ano do asilo)",
        "q_u_victim":"Foi vítima de certos crimes nos EUA (violência doméstica, agressão, tráfico, etc.)?",
        "q_u_harm":"Sofreu dano físico ou mental substancial desse crime?",
        "q_u_report":"Denunciou à polícia/autoridades e é/foi cooperativo(a)?",
    },
}

# =========================== HELPERS ===========================
def rerun():
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()  # noqa

def make_pdf(answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(T[lang]["title"], styles["Title"]), Spacer(1, 12)]
    story += [Paragraph(T[lang]["answers_hdr"], styles["Heading2"]), Spacer(1, 6)]
    for k, v in answers.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["routes_label"], styles["Heading2"])]
    if routes:
        for r in routes: story.append(Paragraph(f"- {r}", styles["Normal"]))
    else:
        story.append(Paragraph(T[lang]["no_route"], styles["Normal"]))
    if notes:
        story += [Spacer(1, 12), Paragraph(T[lang]["notes_label"], styles["Heading2"])]
        for n in notes: story.append(Paragraph(f"- {n}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["admin_note"], styles["Italic"]),
              Spacer(1, 12), Paragraph(f"Generated: {datetime.datetime.utcnow().isoformat()} UTC", styles["Normal"])]
    doc.build(story)
    return buf.getvalue()

# =========================== APP ===========================
st.set_page_config(page_title="Screener", layout="centered")

# state
if "step" not in st.session_state: st.session_state.step = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "lang" not in st.session_state: st.session_state.lang = "en"

# step 0: language
if st.session_state.step == 0:
    lang_choice = st.selectbox(T["en"]["q_lang"], ["English","Español","Português"])
    st.session_state.lang = {"English":"en","Español":"es","Português":"pt"}[lang_choice]
    if st.button(T[st.session_state.lang]["start"]):
        st.session_state.step = 1; rerun()

lang = st.session_state.lang
t = T[lang]

st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

# ---------- dynamic question list with conditions ----------
def q(label, opts, key, cond=lambda a: True):
    return {"label":label, "opts":opts, "key":key, "cond":cond}

A = st.session_state.answers
Yes, No, NS = t["Yes"], t["No"], t["Not sure"]

def is_yes(v): return v == Yes
def is_no(v):  return v == No

Q = [
    q(t["q_where"], [t["InsideUS"], t["OutsideUS"]], "where"),
    q(t["q_born_abroad"], [Yes, No], "born_abroad"),
    q(t["q_lpr"], [Yes, No], "is_lpr"),

    # N-400 branch if LPR
    q(t["q_lpr_years"], ["<3", "3–5", "5+,"], "lpr_years", cond=lambda a: a.get("is_lpr")==Yes),
    q(t["q_married_usc"], [Yes, No], "married_usc", cond=lambda a: a.get("is_lpr")==Yes),
    q(t["q_continuous"], [Yes, No], "continuous", cond=lambda a: a.get("is_lpr")==Yes),
    q(t["q_trips6"], [Yes, No], "trips6", cond=lambda a: a.get("is_lpr")==Yes),
    q(t["q_good_moral"], [Yes, No], "gmh", cond=lambda a: a.get("is_lpr")==Yes),
    q(t["q_selective"], [Yes, No, "N/A"], "selserv", cond=lambda a: a.get("is_lpr")==Yes),

    # N-600 / CRBA branch
    q(t["q_under_18"], [Yes, No], "under18"),
    q(t["q_parent_citizen_birth"], [Yes, No], "parent_citizen_birth"),
    q(t["q_parent_presence_met"], [Yes, No, NS], "parent_presence_met", cond=lambda a: a.get("parent_citizen_birth")==Yes),
    q(t["q_parent_natz_after"], [Yes, No], "parent_natz_after"),
    q(t["q_is_LPR_child"], [Yes, No, "N/A"], "child_LPR", cond=lambda a: a.get("under18")==Yes),
    q(t["q_live_with_usc_parent"], [Yes, No, "N/A"], "custody", cond=lambda a: a.get("under18")==Yes),

    # Family petitions
    q(t["q_family_heads"], [t["opt_spouseUSC"], t["opt_spouseLPR"], t["opt_parentUSC"], t["opt_child21USC"], t["opt_siblingUSC"], t["opt_none"]],
      "relatives"),
    q(t["q_pd_current"], [Yes, No, NS], "pd_current"),

    # Bars / Waivers
    q(t["q_time_out"], [t["Less6"], t["_6_12"], t["_12_36"], t["_3_10"], t["_10plus"]], "time_out", cond=lambda a: a.get("where")==t["OutsideUS"]),
    q(t["q_prior_removal"], [Yes, No], "prior_removal"),
    q(t["q_illegal_reentry"], [t["Never"], t["Once"], t["MoreThanOnce"]], "illegal_reentry"),
    q(t["q_unlawful_presence"], [Yes, No, NS], "unlawful_presence"),
    q(t["q_lawful_entry_last"], [Yes, No, NS], "lawful_entry_last"),
    q(t["q_crim_fraud"], [Yes, No], "crim_fraud"),

    # Asylum branch
    q(t["q_fear"], [Yes, No], "fear", cond=lambda a: a.get("where")==t["InsideUS"]),
    q(t["q_one_year"], [Yes, No, NS], "one_year", cond=lambda a: a.get("where")==t["InsideUS"]),

    # U-visa branch
    q(t["q_u_victim"], [Yes, No, NS], "u_victim"),
    q(t["q_u_harm"], [Yes, No, NS], "u_harm", cond=lambda a: a.get("u_victim") in [Yes, NS]),
    q(t["q_u_report"], [Yes, No, NS], "u_report", cond=lambda a: a.get("u_victim") in [Yes, NS]),
]

# compute visible questions
VISIBLE = [qq for qq in Q if qq["cond"](A)]
TOTAL = len(VISIBLE)

# guard: if step beyond because visibility changed
if 1 <= st.session_state.step <= TOTAL:
    cur = st.session_state.step
else:
    st.session_state.step = max(1, min(TOTAL, st.session_state.step))
    cur = st.session_state.step

# progress
if 1 <= cur <= TOTAL:
    st.write(t["progress"].format(cur=cur, total=TOTAL))
    st.progress((cur - 1) / TOTAL)

# one-at-a-time UI
if 1 <= cur <= TOTAL:
    qd = VISIBLE[cur-1]
    label, opts, key = qd["label"], qd["opts"], qd["key"]
    prev = A.get(key)
    idx = opts.index(prev) if prev in opts else 0
    choice = st.radio(label, opts, index=idx, key=f"q_{key}")
    cols = st.columns(3)
    if cols[0].button(t["back"], disabled=(cur==1), use_container_width=True):
        A[key] = st.session_state.get(f"q_{key}", choice); st.session_state.step = cur-1; rerun()
    if cols[1].button(t["reset"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 0; rerun()
    if cols[2].button(t["next"], use_container_width=True):
        A[key] = st.session_state.get(f"q_{key}", choice); st.session_state.step = cur+1; 
        if st.session_state.step > TOTAL: st.session_state.step = TOTAL+1
        rerun()

# results
if st.session_state.step > TOTAL:
    a = A
    routes, notes = [], []

    inside = a.get("where")==t["InsideUS"]
    outside = a.get("where")==t["OutsideUS"]

    # ---------- N-400 ----------
    if a.get("is_lpr")==Yes:
        ok_years = (a.get("lpr_years")=="5+,") or (a.get("lpr_years") in ["3–5","5+,"] and a.get("married_usc")==Yes)
        cont_ok = a.get("continuous")==Yes and a.get("trips6")==No
        gmc_flag = a.get("gmh")==No
        if ok_years and cont_ok and gmc_flag:
            routes.append("N-400 naturalization (meets basic time/continuous residence/GM criteria as indicated).")
        else:
            notes.append("Potential N-400 issues: time as LPR, continuous residence or good moral character responses may be insufficient.")

    # ---------- Citizenship by birth / derivation (N-600 / CRBA) ----------
    if a.get("parent_citizen_birth")==Yes and a.get("parent_presence_met")==Yes:
        if a.get("under18")==Yes and outside:
            routes.append("CRBA + first U.S. passport at U.S. Embassy/Consulate (citizenship at birth).")
        else:
            routes.append("N-600 / U.S. passport as proof of citizenship acquired at birth.")
    if a.get("parent_natz_after")==Yes and a.get("under18")==Yes and a.get("child_LPR")==Yes and a.get("custody")==Yes and inside:
        routes.append("N-600 (derivation under INA §320).")

    # ---------- Family-based (I-130) ----------
    rels = a.get("relatives", t["opt_none"])
    if rels != t["opt_none"]:
        if a.get("pd_current")==Yes:
            routes.append("Consular processing via NVC (submit DS-260/fees/civil docs/I-864).")
        else:
            routes.append("Family petition path (I-130). Monitor Visa Bulletin until priority date is current.")
    else:
        notes.append("No qualifying relative selected; if one exists, consider filing I-130.")

    # ---------- Waivers / bars ----------
    if outside:
        notes.append("I-601A provisional waiver is not available abroad. If a waiver is needed outside the U.S., use Form I-601.")
    # Unlawful presence
    if a.get("time_out") in [t["_3_10"], t["_10plus"]] and a.get("unlawful_presence")==Yes:
        notes.append("Unlawful-presence 3/10-year bar likely satisfied by time outside (absent 212(a)(9)(C)).")
        routes.append("If inadmissible only for past unlawful presence → I-601 showing extreme hardship to USC/LPR spouse/parent.")
    elif a.get("unlawful_presence")==Yes and outside and a.get("time_out") in [t["Less6"], t["_6_12"], t["_12_36"]]:
        routes.append("I-601 for unlawful presence at consular stage (extreme hardship to USC/LPR spouse/parent).")
    # Prior removal
    if a.get("prior_removal")==Yes:
        routes.append("I-212 (permission to reapply) due to prior removal/deportation before seeking an immigrant visa.")
        notes.append("I-212 is discretionary; include equities, rehabilitation, time abroad, U.S. family hardship.")
    # 9(C) permanent bar
    if a.get("illegal_reentry") in [t["Once"], t["MoreThanOnce"]]:
        notes.append("Possible INA 212(a)(9)(C) permanent bar (illegal reentry after removal or >1yr UP). Often requires 10 years outside then I-212; many are ineligible for I-601A.")
    # Fraud/crime
    if a.get("crim_fraud")==Yes:
        notes.append("Potential additional inadmissibility for criminal/fraud issues; specific waivers may be required.")

    # ---------- Asylum (inside U.S.) ----------
    if inside and a.get("fear")==Yes:
        if a.get("one_year")==Yes or a.get("one_year")==NS:
            routes.append("Asylum/Withholding/CAT screening (fear of return; one-year filing within time or possible exception).")
        else:
            notes.append("One-year deadline may bar asylum unless an exception applies; consider withholding/CAT or other relief.")

    # ---------- U visa ----------
    if a.get("u_victim") in [Yes, NS] and a.get("u_report") in [Yes, NS] and a.get("u_harm") in [Yes, NS]:
        routes.append("U-Visa (victim of qualifying crime in U.S., substantial harm, helpfulness to law enforcement). Requires Form I-918 and law-enforcement certification.")
    elif a.get("u_victim")==Yes and a.get("u_report")==No:
        notes.append("U-Visa typically requires reporting/cooperation; seek law-enforcement certification (Form I-918B).")

    # ---------- Default guidance ----------
    if not routes:
        routes.append("General path: verify or file I-130; when PD current → NVC; assess waivers (I-601) and any I-212 before interview. Consider humanitarian/other categories as applicable.")

    # ---------- OUTPUT ----------
    st.subheader(t["results"])
    if routes:
        st.success(t["routes_label"])
        for r in routes: st.write(f"- {r}")
    else:
        st.warning(t["no_route"])
    if notes:
        st.info(t["notes_label"])
        for n in notes: st.write(f"- {n}")

    # Export
    pdf_bytes = make_pdf(A, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes, file_name="screener_summary.pdf", mime="application/pdf")

    subject = urllib.parse.quote(t["mail_subject"])
    lines = [f"{k}: {v}" for k,v in A.items()]
    if routes: lines += ["", t["routes_label"]] + [f"- {r}" for r in routes]
    if notes:  lines += ["", t["notes_label"]]  + [f"- {n}" for n in notes]
    lines += ["", t["admin_note"]]
    body = urllib.parse.quote("\n".join(lines)[:1500])
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")

    c1,c2 = st.columns(2)
    if c1.button(t["back"], use_container_width=True):
        st.session_state.step = TOTAL; rerun()
    if c2.button(t["reset"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 0; rerun()
