import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ================= TRANSLATIONS (EN / ES / PT) =================
T = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": "**Disclaimer:** Informational only. Not legal advice. No attorney–client relationship is created.",
        "start": "Start", "next": "Next", "back": "Back", "reset": "Reset", "restart": "Start Over",
        "progress": "Step {cur} of {total}",
        "results": "Informational Results",
        "answers_hdr": "Answers:",
        "routes_label": "Possible routes to explore",
        "notes_label": "Notes",
        "no_route": "No clear route identified. Further review recommended.",
        "pdf_btn": "Download PDF summary",
        "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this summary to the administrator or the person who gave you this form.",
        "mail_subject": "Screener Results",

        # Common options
        "Yes": "Yes", "No": "No", "Not sure": "Not sure",
        "InsideUS": "Inside the U.S.", "OutsideUS": "Outside the U.S.",
        "Never": "Never", "Once": "Once", "MoreThanOnce": "More than once",
        "Less6": "<6 months", "_6_12": "6–12 months", "_12_36": "1–3 years", "_3_10": "3–10 years", "_10plus": "10+ years",

        # Questions
        "q_lang": "Choose language / Elija idioma / Escolha idioma",
        "q_where": "Where are you now?",
        "q_lpr": "Are you a lawful permanent resident (green card holder)?",
        "q_lpr_years": "How long have you been an LPR?",
        "q_married_usc": "Married to U.S. citizen and lived in union 3+ years?",
        "q_continuous": "Continuous residence (no 6+ month trips)?",
        "q_trips6": "Any single trip outside 6+ months?",
        "q_good_moral": "Any arrests/convictions in last 5 yrs?",
        "q_selective": "If male 18–26 in U.S., registered Selective Service?",
        "q_under_18": "Are you under 18?",
        "q_parent_citizen_birth": "Was a parent a U.S. citizen at your birth?",
        "q_parent_presence_met": "Did that parent meet U.S. physical presence?",
        "q_parent_natz_after": "Did a parent naturalize after your birth?",
        "q_live_with_usc_parent": "Did/Do you live with USC parent?",
        "q_is_LPR_child": "Is the child an LPR?",
        "q_family_heads": "Which U.S. relatives? (select all that apply)",
        "opt_spouseUSC": "Spouse USC",
        "opt_spouseLPR": "Spouse LPR",
        "opt_parentUSC": "Parent USC",
        "opt_child21USC": "Child USC 21+",
        "opt_siblingUSC": "Sibling USC",
        "opt_none": "None",
        "q_pd_current": "If any petition is approved, is the priority date current on the Visa Bulletin?",
        "q_time_out": "Time outside U.S. (most recent continuous period)?",
        "q_prior_removal": "Ever removed/deported or voluntary departure after proceedings?",
        "q_illegal_reentry": "After removal or >1yr unlawful presence, re-entered/attempted to re-enter illegally?",
        "q_unlawful_presence": "Before last departure, did you accrue 180+ days of unlawful presence?",
        "q_lawful_entry_last": "Last entry inspected/paroled?",
        "q_crim_fraud": "Any criminal issues or fraud/misrepresentation in immigration?",
        "q_fear": "Fear harm if returned or suffered past persecution?",
        "q_one_year": "If inside the U.S., did you enter less than 1 year ago? (or have an exception)",

        "q_u_victim": "Victim of qualifying crime in the U.S. (e.g., DV, assault, trafficking)?",
        "q_u_harm": "Substantial physical or mental harm from that crime?",
        "q_u_report": "Reported to and helpful with law enforcement?",

        # Routes / Notes (localized strings)
        "r_n400_ok": "N-400 naturalization possible (based on time, continuous residence, and good moral character responses).",
        "n_n400_issue": "Potential N-400 issues: time as LPR, continuous residence, long trips, or good moral character.",
        "r_crba": "CRBA and first U.S. passport at the U.S. Embassy/Consulate.",
        "r_n600_birth": "N-600 or U.S. passport as proof of citizenship acquired at birth.",
        "r_n600_320": "N-600 (derivation under INA §320).",
        "r_nvc": "Consular processing via NVC (DS-260, fees, civil docs, I-864).",
        "n_pd_wait": "Family petition filed; monitor Visa Bulletin until priority date is current.",
        "n_no_relative": "No qualifying relative indicated; consider filing an I-130 if eligible.",
        "n_i601a_abroad": "I-601A provisional waiver is not available outside the U.S.; abroad use Form I-601 if needed.",
        "r_i601": "I-601 waiver for unlawful presence showing extreme hardship to USC/LPR spouse or parent.",
        "r_i212": "I-212 (permission to reapply) required due to prior removal/deportation.",
        "n_9c": "Possible INA 212(a)(9)(C) permanent bar (illegal reentry after removal or >1yr unlawful presence); generally requires 10 years abroad then I-212; I-601A not available.",
        "r_asylum": "Asylum/Withholding/CAT screening possible.",
        "n_asylum_oneyear": "One-year filing bar may limit asylum absent an exception; consider withholding or CAT.",
        "r_uvisa": "U Visa (victim of qualifying crime, substantial harm, and cooperation with law enforcement).",
        "r_general": "General path: verify or file I-130; when PD is current proceed with NVC; evaluate I-601 and any I-212 before interview.",
    },

    "es": {
        "title": "Evaluador de Consulta de Inmigración",
        "disclaimer": "**Aviso:** Solo informativo. No es asesoría legal. No crea relación abogado–cliente.",
        "start": "Iniciar", "next": "Siguiente", "back": "Atrás", "reset": "Reiniciar", "restart": "Comenzar de nuevo",
        "progress": "Paso {cur} de {total}",
        "results": "Resultados informativos",
        "answers_hdr": "Respuestas:",
        "routes_label": "Rutas posibles para explorar",
        "notes_label": "Notas",
        "no_route": "No hay ruta clara. Se recomienda revisión adicional.",
        "pdf_btn": "Descargar resumen en PDF",
        "mailto_btn": "Abrir correo para enviar resumen",
        "admin_note": "Por favor envíe este resumen al administrador o a la persona que le proporcionó este formulario.",
        "mail_subject": "Resultados del evaluador",

        "Yes": "Sí", "No": "No", "Not sure": "No seguro",
        "InsideUS": "Dentro de EE. UU.", "OutsideUS": "Fuera de EE. UU.",
        "Never": "Nunca", "Once": "Una vez", "MoreThanOnce": "Más de una vez",
        "Less6": "<6 meses", "_6_12": "6–12 meses", "_12_36": "1–3 años", "_3_10": "3–10 años", "_10plus": "10+ años",

        "q_lang": "Elija idioma / Choose language / Escolha idioma",
        "q_where": "¿Dónde se encuentra ahora?",
        "q_lpr": "¿Es residente permanente (tarjeta verde)?",
        "q_lpr_years": "¿Cuánto tiempo lleva como residente permanente?",
        "q_married_usc": "¿Casado(a) con ciudadano(a) de EE. UU. y en unión 3+ años?",
        "q_continuous": "¿Residencia continua (sin viajes de 6+ meses)?",
        "q_trips6": "¿Algún viaje único de 6+ meses?",
        "q_good_moral": "¿Arrestos/condenas en los últimos 5 años?",
        "q_selective": "Si es hombre de 18–26 en EE. UU., ¿se registró en el Servicio Selectivo?",
        "q_under_18": "¿Menor de 18 años?",
        "q_parent_citizen_birth": "¿Algún padre era ciudadano de EE. UU. al nacer usted?",
        "q_parent_presence_met": "¿Ese padre cumplió presencia física en EE. UU.?",
        "q_parent_natz_after": "¿Algún padre se naturalizó después de su nacimiento?",
        "q_live_with_usc_parent": "¿Vivió/vive con padre/madre ciudadano(a) de EE. UU.?",
        "q_is_LPR_child": "¿El menor es residente permanente?",
        "q_family_heads": "¿Qué familiares tiene en EE. UU.? (seleccione todos los que apliquen)",
        "opt_spouseUSC": "Cónyuge ciudadano",
        "opt_spouseLPR": "Cónyuge residente (LPR)",
        "opt_parentUSC": "Padre/madre ciudadano",
        "opt_child21USC": "Hijo(a) ciudadano de 21+",
        "opt_siblingUSC": "Hermano(a) ciudadano",
        "opt_none": "Ninguno",
        "q_pd_current": "Si hay petición aprobada, ¿la fecha de prioridad está vigente en el Boletín de Visas?",
        "q_time_out": "Tiempo fuera de EE. UU. (período continuo más reciente)?",
        "q_prior_removal": "¿Fue removido/deportado o salió con salida voluntaria tras proceso?",
        "q_illegal_reentry": "Tras remoción o >1 año de presencia ilegal, ¿reingresó/intentó reingresar ilegalmente?",
        "q_unlawful_presence": "Antes de su última salida, ¿acumuló 180+ días de presencia ilegal?",
        "q_lawful_entry_last": "¿Su última entrada fue inspeccionada/parole?",
        "q_crim_fraud": "¿Algún problema penal o fraude/tergiversación en inmigración?",
        "q_fear": "¿Teme sufrir daños si regresa o sufrió persecución pasada?",
        "q_one_year": "Si está dentro de EE. UU., ¿entró hace menos de 1 año? (o tiene una excepción)",

        "q_u_victim": "¿Fue víctima de un delito calificado en EE. UU. (p. ej., violencia doméstica, asalto, trata)?",
        "q_u_harm": "¿Sufrió daño físico o mental sustancial por ese delito?",
        "q_u_report": "¿Reportó y cooperó con la policía/autoridades?",

        "r_n400_ok": "Posible naturalización N-400 (según tiempo, residencia continua y buen carácter moral).",
        "n_n400_issue": "Posibles problemas para N-400: tiempo como LPR, residencia continua, viajes largos o buen carácter moral.",
        "r_crba": "CRBA y primer pasaporte de EE. UU. en Embajada/Consulado.",
        "r_n600_birth": "N-600 o pasaporte de EE. UU. como prueba de ciudadanía adquirida al nacer.",
        "r_n600_320": "N-600 (derivación bajo INA §320).",
        "r_nvc": "Proceso consular por NVC (DS-260, tarifas, documentos civiles, I-864).",
        "n_pd_wait": "Petición familiar presentada; monitoree el Boletín de Visas hasta que la fecha esté vigente.",
        "n_no_relative": "No se indicó familiar calificado; considere presentar un I-130 si es elegible.",
        "n_i601a_abroad": "El I-601A no está disponible fuera de EE. UU.; en el extranjero use el Formulario I-601 si es necesario.",
        "r_i601": "Perdón I-601 por presencia ilegal mostrando dificultad extrema a cónyuge/padre residente o ciudadano.",
        "r_i212": "Se requiere I-212 (permiso para volver a solicitar admisión) por remoción/deportación previa.",
        "n_9c": "Posible barra permanente INA 212(a)(9)(C) (reingreso ilegal tras remoción o >1 año de presencia ilegal); usualmente 10 años fuera y luego I-212; I-601A no disponible.",
        "r_asylum": "Posible asilo/withholding/CAT.",
        "n_asylum_oneyear": "La regla de 1 año puede impedir asilo sin excepción; considere withholding o CAT.",
        "r_uvisa": "Visa U (víctima de delito, daño sustancial y cooperación con las autoridades).",
        "r_general": "Ruta general: verificar o presentar I-130; cuando la PD esté vigente continuar con NVC; evaluar I-601 y cualquier I-212 antes de la entrevista.",
    },

    "pt": {
        "title": "Triagem de Consulta de Imigração",
        "disclaimer": "**Aviso:** Apenas informativo. Não é aconselhamento jurídico. Não cria relação advogado–cliente.",
        "start": "Iniciar", "next": "Avançar", "back": "Voltar", "reset": "Reiniciar", "restart": "Recomeçar",
        "progress": "Etapa {cur} de {total}",
        "results": "Resultados informativos",
        "answers_hdr": "Respostas:",
        "routes_label": "Rotas possíveis para explorar",
        "notes_label": "Observações",
        "no_route": "Nenhuma rota clara. Recomenda-se análise adicional.",
        "pdf_btn": "Baixar resumo em PDF",
        "mailto_btn": "Abrir e-mail para enviar resumo",
        "admin_note": "Envie este resumo ao administrador ou à pessoa que lhe forneceu este formulário.",
        "mail_subject": "Resultados da triagem",

        "Yes": "Sim", "No": "Não", "Not sure": "Não sei",
        "InsideUS": "Dentro dos EUA", "OutsideUS": "Fora dos EUA",
        "Never": "Nunca", "Once": "Uma vez", "MoreThanOnce": "Mais de uma vez",
        "Less6": "<6 meses", "_6_12": "6–12 meses", "_12_36": "1–3 anos", "_3_10": "3–10 anos", "_10plus": "10+ anos",

        "q_lang": "Escolha idioma / Choose language / Elija idioma",
        "q_where": "Onde você está agora?",
        "q_lpr": "Você é residente permanente (green card)?",
        "q_lpr_years": "Há quanto tempo é residente permanente?",
        "q_married_usc": "Casado(a) com cidadão(ã) dos EUA e em união há 3+ anos?",
        "q_continuous": "Residência contínua (sem viagens de 6+ meses)?",
        "q_trips6": "Alguma viagem única de 6+ meses?",
        "q_good_moral": "Prisões/condenações nos últimos 5 anos?",
        "q_selective": "Se homem 18–26 nos EUA, registrou-se no Serviço Militar?",
        "q_under_18": "Menor de 18 anos?",
        "q_parent_citizen_birth": "Algum dos pais era cidadão dos EUA no seu nascimento?",
        "q_parent_presence_met": "Esse pai/mãe cumpriu presença física nos EUA?",
        "q_parent_natz_after": "Algum dos pais se naturalizou após seu nascimento?",
        "q_live_with_usc_parent": "Reside(u) com pai/mãe cidadão dos EUA?",
        "q_is_LPR_child": "A criança é residente permanente?",
        "q_family_heads": "Quais parentes você tem nos EUA? (selecione todos os aplicáveis)",
        "opt_spouseUSC": "Cônjuge cidadão",
        "opt_spouseLPR": "Cônjuge residente (LPR)",
        "opt_parentUSC": "Pai/mãe cidadão",
        "opt_child21USC": "Filho(a) cidadão 21+",
        "opt_siblingUSC": "Irmão(ã) cidadão",
        "opt_none": "Nenhum",
        "q_pd_current": "Se alguma petição foi aprovada, a data de prioridade está atual no Visa Bulletin?",
        "q_time_out": "Tempo fora dos EUA (período contínuo mais recente)?",
        "q_prior_removal": "Já foi removido/deportado ou saiu com saída voluntária após processo?",
        "q_illegal_reentry": "Após remoção ou >1 ano de presença ilegal, reentrou/tentou reentrar ilegalmente?",
        "q_unlawful_presence": "Antes da última saída, acumulou 180+ dias de presença ilegal?",
        "q_lawful_entry_last": "A última entrada foi inspecionada/parole?",
        "q_crim_fraud": "Algum problema penal ou fraude/deturpação em imigração?",
        "q_fear": "Tem medo de sofrer danos se retornar ou sofreu perseguição passada?",
        "q_one_year": "Se está dentro dos EUA, entrou há menos de 1 ano? (ou possui exceção)",

        "q_u_victim": "Foi vítima de crime qualificado nos EUA (p.ex., violência doméstica, agressão, tráfico)?",
        "q_u_harm": "Sofreu dano físico ou mental substancial desse crime?",
        "q_u_report": "Denunciou e cooperou com as autoridades?",

        "r_n400_ok": "Possível naturalização N-400 (com base em tempo, residência contínua e bom caráter moral).",
        "n_n400_issue": "Possíveis problemas para N-400: tempo como LPR, residência contínua, viagens longas ou bom caráter moral.",
        "r_crba": "CRBA e primeiro passaporte dos EUA no Consulado/Embaixada.",
        "r_n600_birth": "N-600 ou passaporte dos EUA como prova de cidadania ao nascer.",
        "r_n600_320": "N-600 (derivação pelo INA §320).",
        "r_nvc": "Processamento consular via NVC (DS-260, taxas, documentos civis, I-864).",
        "n_pd_wait": "Petição familiar apresentada; acompanhe o Visa Bulletin até a data estar atual.",
        "n_no_relative": "Nenhum parente qualificado indicado; considere apresentar um I-130 se elegível.",
        "n_i601a_abroad": "O I-601A não está disponível fora dos EUA; no exterior use o Formulário I-601 se necessário.",
        "r_i601": "I-601 para presença ilegal demonstrando dificuldade extrema a cônjuge/pai cidadão ou residente.",
        "r_i212": "I-212 (permissão para reaplicar) necessário devido a remoção/deportação prévia.",
        "n_9c": "Possível barreira permanente INA 212(a)(9)(C) (reentrada ilegal após remoção ou >1 ano de presença ilegal); normalmente exige 10 anos fora e então I-212; I-601A indisponível.",
        "r_asylum": "Possível asilo/withholding/CAT.",
        "n_asylum_oneyear": "A regra de 1 ano pode impedir asilo sem exceção; considere withholding ou CAT.",
        "r_uvisa": "Visto U (vítima de crime, dano substancial e cooperação com as autoridades).",
        "r_general": "Rota geral: verificar ou apresentar I-130; quando a PD estiver atual prosseguir com NVC; avaliar I-601 e eventual I-212 antes da entrevista.",
    }
}

# ================= HELPERS =================
def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()  # legacy

def make_pdf(answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(T[lang]["title"], styles["Title"]), Spacer(1, 12)]
    story += [Paragraph(T[lang]["disclaimer"], styles["Italic"]), Spacer(1, 12)]
    story += [Paragraph(T[lang]["answers_hdr"], styles["Heading2"])]
    for k, v in answers.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["routes_label"], styles["Heading2"])]
    if routes:
        for r in routes:
            story.append(Paragraph(f"- {r}", styles["Normal"]))
    else:
        story.append(Paragraph(T[lang]["no_route"], styles["Normal"]))
    if notes:
        story += [Spacer(1, 12), Paragraph(T[lang]["notes_label"], styles["Heading2"])]
        for n in notes:
            story.append(Paragraph(f"- {n}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["admin_note"], styles["Italic"])]
    doc.build(story)
    return buf.getvalue()

def q(label, opts, key, cond=lambda a: True):
    return {"label": label, "opts": opts, "key": key, "cond": cond}

# ================= APP =================
st.set_page_config(page_title="Screener", layout="centered")

if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Step 0: language
if st.session_state.step == 0:
    lang_choice = st.selectbox(T["en"]["q_lang"], ["English", "Español", "Português"])
    st.session_state.lang = {"English": "en", "Español": "es", "Português": "pt"}[lang_choice]
    if st.button(T[st.session_state.lang]["start"]):
        st.session_state.step = 1
        rerun()

lang = st.session_state.lang
t = T[lang]
A = st.session_state.answers

Yes, No, NS = t["Yes"], t["No"], t["Not sure"]

# Always show disclaimer
st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

# Question list (one-at-a-time, with conditions)
Q = [
    q(t["q_where"], [t["InsideUS"], t["OutsideUS"]], "where"),
    q(t["q_lpr"], [Yes, No], "is_lpr"),

    # N-400 branch if LPR
    q(t["q_lpr_years"], ["<3", "3–5", "5+"], "lpr_years", cond=lambda a: a.get("is_lpr") == Yes),
    q(t["q_married_usc"], [Yes, No], "married_usc", cond=lambda a: a.get("is_lpr") == Yes),
    q(t["q_continuous"], [Yes, No], "continuous", cond=lambda a: a.get("is_lpr") == Yes),
    q(t["q_trips6"], [Yes, No], "trips6", cond=lambda a: a.get("is_lpr") == Yes),
    q(t["q_good_moral"], [Yes, No], "gmh", cond=lambda a: a.get("is_lpr") == Yes),
    q(t["q_selective"], [Yes, No, "N/A"], "selserv", cond=lambda a: a.get("is_lpr") == Yes),

    # Citizenship at birth / derivation
    q(t["q_under_18"], [Yes, No], "under18"),
    q(t["q_parent_citizen_birth"], [Yes, No], "parent_citizen_birth"),
    q(t["q_parent_presence_met"], [Yes, No, NS], "parent_presence_met", cond=lambda a: a.get("parent_citizen_birth") == Yes),
    q(t["q_parent_natz_after"], [Yes, No], "parent_natz_after"),
    q(t["q_is_LPR_child"], [Yes, No, "N/A"], "child_LPR", cond=lambda a: a.get("under18") == Yes),
    q(t["q_live_with_usc_parent"], [Yes, No, "N/A"], "custody", cond=lambda a: a.get("under18") == Yes),

    # Family relationships (multiselect)
    {"label": t["q_family_heads"], "opts": [t["opt_spouseUSC"], t["opt_spouseLPR"], t["opt_parentUSC"],
                                            t["opt_child21USC"], t["opt_siblingUSC"], t["opt_none"]],
     "key": "relatives", "cond": lambda a: True},

    q(t["q_pd_current"], [Yes, No, NS], "pd_current"),

    # Bars / waivers
    q(t["q_time_out"], [t["Less6"], t["_6_12"], t["_12_36"], t["_3_10"], t["_10plus"]], "time_out",
      cond=lambda a: a.get("where") == t["OutsideUS"]),
    q(t["q_prior_removal"], [Yes, No], "prior_removal"),
    q(t["q_illegal_reentry"], [t["Never"], t["Once"], t["MoreThanOnce"]], "illegal_reentry"),
    q(t["q_unlawful_presence"], [Yes, No, NS], "unlawful_presence"),
    q(t["q_lawful_entry_last"], [Yes, No, NS], "lawful_entry_last"),
    q(t["q_crim_fraud"], [Yes, No], "crim_fraud"),

    # Asylum (inside)
    q(t["q_fear"], [Yes, No], "fear", cond=lambda a: a.get("where") == t["InsideUS"]),
    q(t["q_one_year"], [Yes, No, NS], "one_year", cond=lambda a: a.get("where") == t["InsideUS"]),

    # U visa
    q(t["q_u_victim"], [Yes, No, NS], "u_victim"),
    q(t["q_u_harm"], [Yes, No, NS], "u_harm", cond=lambda a: a.get("u_victim") in [Yes, NS]),
    q(t["q_u_report"], [Yes, No, NS], "u_report", cond=lambda a: a.get("u_victim") in [Yes, NS]),
]

# Compute visible questions
VISIBLE = [qq for qq in Q if qq["cond"](A)]
TOTAL = len(VISIBLE)

# Clamp step
if st.session_state.step > TOTAL:
    st.session_state.step = TOTAL + 1
cur = st.session_state.step

# Progress
if 1 <= cur <= TOTAL:
    st.write(t["progress"].format(cur=cur, total=TOTAL))
    st.progress((cur - 1) / TOTAL)

# One-at-a-time UI
if 1 <= cur <= TOTAL:
    qd = VISIBLE[cur - 1]
    label, opts, key = qd["label"], qd["opts"], qd["key"]
    prev = A.get(key)

    if key == "relatives":
        default = prev if isinstance(prev, list) else []
        choice = st.multiselect(label, opts, default=default)
    else:
        idx = opts.index(prev) if prev in opts else 0
        choice = st.radio(label, opts, index=idx, key=f"q_{key}")

    cols = st.columns(3)
    if cols[0].button(t["back"], disabled=(cur == 1)):
        A[key] = choice
        st.session_state.step = cur - 1
        rerun()
    if cols[1].button(t["reset"]):
        st.session_state.answers = {}
        st.session_state.step = 0
        rerun()
    if cols[2].button(t["next"]):
        A[key] = choice
        st.session_state.step = cur + 1
        rerun()

# Results
if cur > TOTAL:
    routes, notes = [], []

    inside = A.get("where") == t["InsideUS"]
    outside = A.get("where") == t["OutsideUS"]

    # N-400
    if A.get("is_lpr") == Yes:
        ok_years = (A.get("lpr_years") in ["5+", "3–5"])  # basic window; marriage 3-year nuance not over-fitted here
        cont_ok = A.get("continuous") == Yes and A.get("trips6") == No
        gmc_ok = A.get("gmh") == No
        if ok_years and cont_ok and gmc_ok:
            routes.append(t["r_n400_ok"])
        else:
            notes.append(t["n_n400_issue"])

    # Citizenship by birth / derivation (N-600 / CRBA)
    if A.get("parent_citizen_birth") == Yes and A.get("parent_presence_met") == Yes:
        if A.get("under18") == Yes and outside:
            routes.append(t["r_crba"])
        else:
            routes.append(t["r_n600_birth"])
    if A.get("parent_natz_after") == Yes and A.get("under18") == Yes and A.get("child_LPR") == Yes and A.get("custody") == Yes and inside:
        routes.append(t["r_n600_320"])

    # Family-based (I-130)
    rels = A.get("relatives", [])
    if isinstance(rels, str):
        rels = [rels]
    # sanitize "None" with others
    if t["opt_none"] in rels and len(rels) > 1:
        rels = [r for r in rels if r != t["opt_none"]]
    if rels and t["opt_none"] not in rels:
        if A.get("pd_current") == Yes:
            routes.append(t["r_nvc"])
        else:
            notes.append(t["n_pd_wait"])
    else:
        notes.append(t["n_no_relative"])

    # Waivers / bars
    if outside:
        notes.append(t["n_i601a_abroad"])
    if A.get("unlawful_presence") == Yes and outside:
        routes.append(t["r_i601"])
    if A.get("prior_removal") == Yes:
        routes.append(t["r_i212"])
    if A.get("illegal_reentry") in [t["Once"], t["MoreThanOnce"]]:
        notes.append(t["n_9c"])
    if A.get("crim_fraud") == Yes:
        # keep generic; specific waivers vary
        notes.append(t["q_crim_fraud"])

    # Asylum
    if inside and A.get("fear") == Yes:
        if A.get("one_year") in [Yes, NS]:
            routes.append(t["r_asylum"])
        else:
            notes.append(t["n_asylum_oneyear"])

    # U visa
    if A.get("u_victim") == Yes and A.get("u_report") == Yes and A.get("u_harm") in [Yes, NS]:
        routes.append(t["r_uvisa"])

    if not routes:
        routes.append(t["r_general"])

    st.subheader(t["results"])
    st.markdown(t["disclaimer"])

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

    pdf_bytes = make_pdf(A, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes, file_name="screener_summary.pdf", mime="application/pdf")

    subject = urllib.parse.quote(t["mail_subject"])
    lines = [f"{k}: {v}" for k, v in A.items()]
    if routes:
        lines += ["", t["routes_label"]] + [f"- {r}" for r in routes]
    if notes:
        lines += ["", t["notes_label"]] + [f"- {n}" for n in notes]
    lines += ["", t["admin_note"]]
    body = urllib.parse.quote("\n".join(lines)[:1800])
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")

    c1, c2 = st.columns(2)
    if c1.button(t["restart"]):
        st.session_state.answers = {}
        st.session_state.step = 0
        rerun()
    if c2.button(t["reset"]):
        st.session_state.answers = {}
        st.session_state.step = 1
        rerun()
