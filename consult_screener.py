import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ============================== TRANSLATIONS ==============================
# All labels, options, routes, and notes are localized so UI and results match language choice.
T = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": "**Disclaimer:** Informational only. Not legal advice. No attorney–client relationship is created.",
        "start": "Start", "next": "Next", "back": "Back", "reset": "Reset", "restart": "Start Over",
        "progress": "Step {cur} of {total}", "results": "Informational Results",
        "answers_hdr": "Answers:", "routes_label": "Possible routes to explore",
        "notes_label": "Notes", "no_route": "No clear route identified. Further review recommended.",
        "pdf_btn": "Download PDF summary", "mailto_btn": "Open email to send summary",
        "admin_note": "Please send this summary to the administrator or the person who gave you this form.",
        "mail_subject": "Screener Results",

        # Options
        "Yes":"Yes","No":"No","NS":"Not sure","NA":"N/A",
        "InsideUS":"Inside the U.S.","OutsideUS":"Outside the U.S.",
        "Never":"Never","Once":"Once","MoreThanOnce":"More than once",
        "Less6":"<6 months","_6_12":"6–12 months","_12_36":"1–3 years","_3_10":"3–10 years","_10plus":"10+ years",

        # Questions
        "q_lang":"Choose language / Elija idioma / Escolha idioma",
        "q_where":"Where are you now?",
        "q_relatives":"Which U.S. relatives do you have? (select all that apply)",
        "opt_spouseUSC":"Spouse is U.S. citizen",
        "opt_spouseLPR":"Spouse is LPR",
        "opt_parentUSC":"Parent is U.S. citizen",
        "opt_child21USC":"U.S. citizen son/daughter age 21+ (you are the parent)",
        "opt_siblingUSC":"U.S. citizen brother/sister",
        "opt_none":"None",

        "q_last_entry_lawful":"If you are **inside** the U.S., was your last entry inspected or paroled (visa, wave-through, parole)?",
        "q_unlawful_presence":"Before your last departure, did you accrue **180+ days of unlawful presence**?",
        "q_time_out":"How long have you been **outside** the U.S. in your most recent continuous period?",
        "q_prior_removal":"Have you ever been **removed/deported** or departed after an order of removal?",
        "q_illegal_reentry":"After removal or after >1 year of unlawful presence, did you **reenter/attempt to reenter illegally**?",
        "q_crim_fraud":"Any criminal issues or fraud/misrepresentation in immigration applications?",

        # Citizenship short triage
        "q_under18":"Are you under 18 years old?",
        "q_parent_citizen_birth":"Was a parent a U.S. citizen **at your birth**?",
        "q_parent_presence_met":"Did that parent meet required **U.S. physical presence** before your birth?",
        "q_parent_natz_after":"Did a parent **naturalize after** your birth?",
        "q_child_LPR":"If under 18 and inside the U.S.: are/were you an **LPR living in the legal and physical custody** of the U.S. citizen parent?",

        # Routes (results)
        "r_crba":"CRBA + first U.S. passport at post (citizenship at birth).",
        "r_n600_birth":"N-600 / U.S. passport as proof of citizenship acquired at birth.",
        "r_n600_320":"N-600 (derivation under INA §320).",

        "r_ir1_aos":"Adjustment of Status via I-130/I-485 (spouse of U.S. citizen, lawful entry).",
        "r_ir1_cp":"Consular processing (IR-1/CR-1). If unlawful presence applies, I-601 at consular stage; I-601A only if applicant is **in the U.S.** with a USC/LPR spouse/parent as qualifying relative.",
        "r_f2a":"I-130 (spouse of LPR). When PD current → AOS (with lawful entry) or consular processing.",

        "r_ir5_aos":"IR-5 Adjustment of Status via I-130/I-485 (parent of U.S. citizen 21+, lawful entry).",
        "r_ir5_cp":"IR-5 Consular processing via NVC. If unlawful presence applies, file I-601 at consular stage.",

        "r_f4":"F4 (sibling of USC): maintain petition; when PD current → NVC and consular processing.",
        "r_i601":"I-601 waiver for unlawful presence (show **extreme hardship** to USC/LPR spouse or parent).",
        "r_i212":"I-212 (permission to reapply) due to prior removal/deportation (can be filed with the I-601 package).",
        "r_default":"Verify/file I-130 basis; if consular processing, prepare DS-260, fees, civil docs, and assess any required waivers (I-601 and/or I-212).",

        # Notes (results)
        "n_601_qr_child":"For I-601 hardship, the qualifying relative must be the applicant’s **USC/LPR spouse or parent** — not the USC child.",
        "n_601A_abroad":"I-601A provisional waiver is **not available outside** the U.S.; abroad use **Form I-601**.",
        "n_9c":"Possible INA 212(a)(9)(C) permanent bar (illegal reentry after removal or after >1 year unlawful presence). Often requires 10 years outside then I-212; I-601A not available.",
        "n_crime":"Potential additional inadmissibility (criminal/fraud). Case-specific waivers may be required.",
    },

    "es": {
        "title":"Evaluador de Consulta de Inmigración",
        "disclaimer":"**Aviso:** Solo informativo. No es asesoría legal. No crea relación abogado-cliente.",
        "start":"Iniciar","next":"Siguiente","back":"Atrás","reset":"Reiniciar","restart":"Comenzar de nuevo",
        "progress":"Paso {cur} de {total}","results":"Resultados informativos",
        "answers_hdr":"Respuestas:","routes_label":"Rutas posibles para explorar",
        "notes_label":"Notas","no_route":"No hay ruta clara. Se recomienda revisión adicional.",
        "pdf_btn":"Descargar resumen en PDF","mailto_btn":"Abrir correo para enviar resumen",
        "admin_note":"Envíe este resumen al administrador o a la persona que le dio este formulario.",
        "mail_subject":"Resultados del evaluador",

        "Yes":"Sí","No":"No","NS":"No seguro","NA":"N/A",
        "InsideUS":"Dentro de EE. UU.","OutsideUS":"Fuera de EE. UU.",
        "Never":"Nunca","Once":"Una vez","MoreThanOnce":"Más de una vez",
        "Less6":"<6 meses","_6_12":"6–12 meses","_12_36":"1–3 años","_3_10":"3–10 años","_10plus":"10+ años",

        "q_lang":"Elija idioma / Choose language / Escolha idioma",
        "q_where":"¿Dónde se encuentra ahora?",
        "q_relatives":"¿Qué familiares tiene en EE. UU.? (seleccione todos los que apliquen)",
        "opt_spouseUSC":"Cónyuge ciudadano de EE. UU.",
        "opt_spouseLPR":"Cónyuge residente (LPR)",
        "opt_parentUSC":"Padre/madre ciudadano(a) de EE. UU.",
        "opt_child21USC":"Hijo(a) ciudadano(a) de EE. UU. de 21+ (usted es el padre/madre)",
        "opt_siblingUSC":"Hermano(a) ciudadano(a) de EE. UU.",
        "opt_none":"Ninguno",

        "q_last_entry_lawful":"Si está **dentro** de EE. UU., ¿su última entrada fue inspeccionada o con parole (visa, pase permitido, parole)?",
        "q_unlawful_presence":"Antes de su última salida, ¿acumuló **180+ días de presencia ilegal**?",
        "q_time_out":"¿Cuánto tiempo lleva **fuera** de EE. UU. en su período continuo más reciente?",
        "q_prior_removal":"¿Alguna vez fue **removido/deportado** o salió tras una orden de remoción?",
        "q_illegal_reentry":"Después de una remoción o de >1 año de presencia ilegal, ¿**reingresó/intentó reingresar ilegalmente**?",
        "q_crim_fraud":"¿Algún problema penal o fraude/tergiversación en inmigración?",

        "q_under18":"¿Tiene menos de 18 años?",
        "q_parent_citizen_birth":"¿Algún padre era ciudadano de EE. UU. **al nacer usted**?",
        "q_parent_presence_met":"¿Ese padre cumplió la **presencia física** requerida en EE. UU. antes de su nacimiento?",
        "q_parent_natz_after":"¿Algún padre se **naturalizó después** de su nacimiento?",
        "q_child_LPR":"Si es menor de 18 y está dentro de EE. UU.: ¿es/era **residente permanente viviendo bajo custodia legal y física** del padre/madre ciudadano?",

        "r_crba":"CRBA + primer pasaporte estadounidense en el consulado (ciudadanía por nacimiento).",
        "r_n600_birth":"N-600 / pasaporte de EE. UU. como prueba de ciudadanía adquirida al nacer.",
        "r_n600_320":"N-600 (derivación bajo INA §320).",

        "r_ir1_aos":"Ajuste de Estatus vía I-130/I-485 (cónyuge de ciudadano, entrada lícita).",
        "r_ir1_cp":"Proceso consular (IR-1/CR-1). Si hay presencia ilegal, I-601 en fase consular; I-601A solo si el solicitante está **en EE. UU.** y el familiar calificador es cónyuge/padre LPR o ciudadano.",
        "r_f2a":"I-130 (cónyuge de residente LPR). Cuando la fecha esté vigente → AOS (con entrada lícita) o proceso consular.",

        "r_ir5_aos":"IR-5 Ajuste de Estatus vía I-130/I-485 (padre de ciudadano 21+, entrada lícita).",
        "r_ir5_cp":"IR-5 Proceso consular vía NVC. Si hay presencia ilegal, presentar I-601 en fase consular.",

        "r_f4":"F4 (hermano de ciudadano): mantener la petición; cuando la fecha esté vigente → NVC y proceso consular.",
        "r_i601":"I-601 por presencia ilegal (demostrar **dificultad extrema** a cónyuge/padre ciudadano o LPR).",
        "r_i212":"I-212 (permiso para volver a solicitar admisión) por remoción/deportación previa (puede presentarse junto con el I-601).",
        "r_default":"Verificar/presentar I-130; si es proceso consular, preparar DS-260, tarifas, documentos civiles y evaluar exenciones necesarias (I-601 y/o I-212).",

        "n_601_qr_child":"Para el I-601, el familiar calificador debe ser el **cónyuge o padre** ciudadano/LPR del solicitante; **no** el hijo ciudadano.",
        "n_601A_abroad":"El I-601A **no está disponible fuera** de EE. UU.; en el exterior se usa **Formulario I-601**.",
        "n_9c":"Posible barra permanente INA 212(a)(9)(C) (reingreso ilegal tras remoción o tras >1 año de presencia ilegal). Suele requerir 10 años fuera y luego I-212; I-601A no disponible.",
        "n_crime":"Posible inadmisibilidad adicional (penal/fraude). Puede requerir exenciones específicas.",
    },

    "pt": {
        "title":"Triagem de Consulta de Imigração",
        "disclaimer":"**Aviso:** Somente informativo. Não é aconselhamento jurídico. Não cria relação advogado-cliente.",
        "start":"Iniciar","next":"Avançar","back":"Voltar","reset":"Reiniciar","restart":"Começar novamente",
        "progress":"Etapa {cur} de {total}","results":"Resultados informativos",
        "answers_hdr":"Respostas:","routes_label":"Rotas possíveis para explorar",
        "notes_label":"Observações","no_route":"Nenhuma rota clara. Recomenda-se análise adicional.",
        "pdf_btn":"Baixar PDF","mailto_btn":"Abrir e-mail para enviar resumo",
        "admin_note":"Envie este resumo ao administrador ou à pessoa que lhe forneceu este formulário.",
        "mail_subject":"Resultados da triagem",

        "Yes":"Sim","No":"Não","NS":"Não sei","NA":"N/A",
        "InsideUS":"Dentro dos EUA","OutsideUS":"Fora dos EUA",
        "Never":"Nunca","Once":"Uma vez","MoreThanOnce":"Mais de uma vez",
        "Less6":"<6 meses","_6_12":"6–12 meses","_12_36":"1–3 anos","_3_10":"3–10 anos","_10plus":"10+ anos",

        "q_lang":"Escolha idioma / Choose language / Elija idioma",
        "q_where":"Onde você está agora?",
        "q_relatives":"Quais parentes você tem nos EUA? (selecione todos os aplicáveis)",
        "opt_spouseUSC":"Cônjuge cidadão dos EUA",
        "opt_spouseLPR":"Cônjuge residente (LPR)",
        "opt_parentUSC":"Pai/mãe cidadão(ã) dos EUA",
        "opt_child21USC":"Filho(a) cidadão(ã) dos EUA com 21+ (você é o pai/mãe)",
        "opt_siblingUSC":"Irmão(ã) cidadão(ã) dos EUA",
        "opt_none":"Nenhum",

        "q_last_entry_lawful":"Se você está **dentro** dos EUA, sua última entrada foi inspecionada ou com parole (visto, liberação, parole)?",
        "q_unlawful_presence":"Antes da última saída, acumulou **180+ dias de presença ilegal**?",
        "q_time_out":"Há quanto tempo você está **fora** dos EUA no período contínuo mais recente?",
        "q_prior_removal":"Você já foi **removido/deportado** ou saiu após ordem de remoção?",
        "q_illegal_reentry":"Após remoção ou >1 ano de presença ilegal, **reentrou/tentou reentrar ilegalmente**?",
        "q_crim_fraud":"Algum problema penal ou fraude/deturpação em imigração?",

        "q_under18":"Você tem menos de 18 anos?",
        "q_parent_citizen_birth":"Algum dos pais era cidadão dos EUA **no seu nascimento**?",
        "q_parent_presence_met":"Esse pai/mãe cumpriu a **presença física** exigida nos EUA antes do seu nascimento?",
        "q_parent_natz_after":"Algum dos pais **naturalizou após** o seu nascimento?",
        "q_child_LPR":"Se menor de 18 e dentro dos EUA: você é/era **residente permanente vivendo sob custódia legal e física** do pai/mãe cidadão?",

        "r_crba":"CRBA + primeiro passaporte dos EUA no consulado (cidadania ao nascer).",
        "r_n600_birth":"N-600 / passaporte dos EUA como prova de cidadania adquirida ao nascer.",
        "r_n600_320":"N-600 (derivação sob INA §320).",

        "r_ir1_aos":"Ajuste de Status via I-130/I-485 (cônjuge de cidadão, entrada lícita).",
        "r_ir1_cp":"Processo consular (IR-1/CR-1). Se houver presença ilegal, I-601 na fase consular; I-601A apenas se o requerente estiver **nos EUA** e o parente qualificador for cônjuge/pai LPR ou cidadão.",
        "r_f2a":"I-130 (cônjuge de residente LPR). Quando a data estiver atual → AOS (com entrada lícita) ou processo consular.",

        "r_ir5_aos":"IR-5 Ajuste de Status via I-130/I-485 (pai/mãe de cidadão 21+, entrada lícita).",
        "r_ir5_cp":"IR-5 Processo consular via NVC. Se houver presença ilegal, apresentar I-601 na fase consular.",

        "r_f4":"F4 (irmão de cidadão): manter a petição; quando a data estiver atual → NVC e processo consular.",
        "r_i601":"I-601 por presença ilegal (demonstrar **dificuldade extrema** a cônjuge/pai cidadão ou LPR).",
        "r_i212":"I-212 (permissão para voltar a solicitar admissão) por remoção/deportação prévia (pode ser apresentado com o I-601).",
        "r_default":"Verificar/apresentar I-130; se processo consular, preparar DS-260, taxas, documentos civis e avaliar as isenções necessárias (I-601 e/ou I-212).",

        "n_601_qr_child":"Para o I-601, o parente qualificador deve ser o **cônjuge ou pai** cidadão/LPR do requerente; **não** o filho cidadão.",
        "n_601A_abroad":"O I-601A **não está disponível fora** dos EUA; no exterior usa-se **Formulário I-601**.",
        "n_9c":"Possível barreira permanente INA 212(a)(9)(C) (reentrada ilegal após remoção ou após >1 ano de presença ilegal). Normalmente requer 10 anos fora e depois I-212; I-601A indisponível.",
        "n_crime":"Possível inadmissibilidade adicional (penal/fraude). Pode exigir isenções específicas.",
    }
}

# ============================== HELPERS ==============================
def rerun():
    if hasattr(st,"rerun"): st.rerun()
    else: st.experimental_rerun()  # noqa

def make_pdf(answers, routes, notes, lang):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(T[lang]["title"], styles["Title"]), Spacer(1, 12)]
    story += [Paragraph(T[lang]["disclaimer"], styles["Italic"]), Spacer(1, 12)]
    story += [Paragraph(T[lang]["answers_hdr"], styles["Heading2"])]
    for k,v in answers.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["routes_label"], styles["Heading2"])]
    for r in routes:
        story.append(Paragraph(f"- {r}", styles["Normal"]))
    if notes:
        story += [Spacer(1, 12), Paragraph(T[lang]["notes_label"], styles["Heading2"])]
        for n in notes:
            story.append(Paragraph(f"- {n}", styles["Normal"]))
    story += [Spacer(1, 12), Paragraph(T[lang]["admin_note"], styles["Italic"])]
    doc.build(story)
    return buf.getvalue()

# ============================== APP ==============================
st.set_page_config(page_title="Screener", layout="centered")

if "step" not in st.session_state: st.session_state.step = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "lang" not in st.session_state: st.session_state.lang = "en"

# Language picker
if st.session_state.step == 0:
    lang_choice = st.selectbox(T["en"]["q_lang"], ["English", "Español", "Português"])
    st.session_state.lang = {"English":"en","Español":"es","Português":"pt"}[lang_choice]
    if st.button(T[st.session_state.lang]["start"]):
        st.session_state.step = 1; rerun()

lang = st.session_state.lang
t = T[lang]
A = st.session_state.answers

# Always show header + disclaimer
st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

Yes, No, NS, NA = t["Yes"], t["No"], t["NS"], t["NA"]

def q(label, opts, key, cond=lambda a: True, widget="radio"):
    return {"label":label, "opts":opts, "key":key, "cond":cond, "widget":widget}

# Helpers for current selections
inside = lambda: A.get("where")==t["InsideUS"]
outside = lambda: A.get("where")==t["OutsideUS"]
def rels():
    return A.get("relatives") or []
def has(opt):
    return opt in rels()
def any_rel():
    return bool(rels())

# Build the dynamic question list
Q = [
    q(t["q_where"], [t["InsideUS"], t["OutsideUS"]], "where"),
    q(t["q_relatives"], [t["opt_spouseUSC"], t["opt_spouseLPR"], t["opt_parentUSC"], t["opt_child21USC"], t["opt_siblingUSC"], t["opt_none"]],
      "relatives", widget="multiselect"),

    # If inside + immediate-relative routes, ask about last entry for AOS eligibility; otherwise N/A
    q(t["q_last_entry_lawful"], [Yes, No, NA], "last_entry_lawful",
      cond=lambda a: inside() and (has(t["opt_spouseUSC"]) or has(t["opt_child21USC"]) or has(t["opt_parentUSC"]))),

    # Unlawful presence only relevant if consular processing likely (outside) OR inside without lawful entry
    q(t["q_unlawful_presence"], [Yes, No, NS, NA], "unlawful_presence",
      cond=lambda a: (outside()) or (inside() and a.get("last_entry_lawful")==No)),

    # Time outside only matters if outside AND unlawful presence == Yes (for 3/10-year bar analysis)
    q(t["q_time_out"], [t["Less6"], t["_6_12"], t["_12_36"], t["_3_10"], t["_10plus"]], "time_out",
      cond=lambda a: outside() and a.get("unlawful_presence")==Yes),

    # Prior removal relevant when outside, or inside without lawful entry
    q(t["q_prior_removal"], [Yes, No, NS, NA], "prior_removal",
      cond=lambda a: outside() or (inside() and a.get("last_entry_lawful")==No)),

    # Illegal reentry only relevant if prior removal or unlawful presence issues arose
    q(t["q_illegal_reentry"], [t["Never"], t["Once"], t["MoreThanOnce"], NA], "illegal_reentry",
      cond=lambda a: a.get("prior_removal") in [Yes, NS] or a.get("unlawful_presence") in [Yes, NS]),

    # Crime/fraud only if any route is being considered (has relatives)
    q(t["q_crim_fraud"], [Yes, No, NS, NA], "crim_fraud", cond=lambda a: any_rel()),

    # Citizenship short triage — lightweight, always shown but uses N/A where not applicable
    q(t["q_under18"], [Yes, No], "under18"),
    q(t["q_parent_citizen_birth"], [Yes, No, NS], "parent_citizen_birth"),
    q(t["q_parent_presence_met"], [Yes, No, NS, NA], "parent_presence_met",
      cond=lambda a: a.get("parent_citizen_birth") in [Yes, NS]),
    q(t["q_parent_natz_after"], [Yes, No, NS], "parent_natz_after"),
    q(t["q_child_LPR"], [Yes, No, NA], "child_LPR",
      cond=lambda a: a.get("under18")==Yes and inside()),
]

# Determine visible questions and current step
VISIBLE = [qq for qq in Q if qq["cond"](A)]
TOTAL = len(VISIBLE)
if st.session_state.step > TOTAL: st.session_state.step = TOTAL + 1
cur = st.session_state.step

if 1 <= cur <= TOTAL:
    st.write(t["progress"].format(cur=cur, total=TOTAL))
    st.progress((cur-1)/TOTAL if TOTAL else 1.0)

# Ask current question (one at a time)
if 1 <= cur <= TOTAL:
    qd = VISIBLE[cur-1]
    label, opts, key, widget = qd["label"], qd["opts"], qd["key"], qd["widget"]
    prev = A.get(key)

    # Relatives multiselect with "None" exclusivity
    if widget == "multiselect":
        default = prev if isinstance(prev, list) else ([] if prev is None else [prev])
        choice = st.multiselect(label, opts, default=default)
        # Make "None" exclusive
        if t["opt_none"] in choice and len(choice) > 1:
            choice = [t["opt_none"]]
    else:
        # Default index
        idx = opts.index(prev) if prev in opts else 0
        choice = st.radio(label, opts, index=idx, key=f"q_{key}")

    c1,c2,c3 = st.columns(3)
    if c1.button(t["back"], disabled=(cur==1), use_container_width=True):
        A[key] = choice; st.session_state.step = cur-1; rerun()
    if c2.button(t["reset"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 0; rerun()
    if c3.button(t["next"], use_container_width=True):
        A[key] = choice; st.session_state.step = cur+1; rerun()

# ============================== RESULTS ==============================
if cur > TOTAL:
    routes, notes = [], []

    rel_list = rels()
    has_spouse_USC   = t["opt_spouseUSC"] in rel_list
    has_spouse_LPR   = t["opt_spouseLPR"] in rel_list
    has_parent_USC   = t["opt_parentUSC"] in rel_list
    has_child21_USC  = t["opt_child21USC"] in rel_list       # IR-5 (parent of USC 21+)
    has_sibling_USC  = t["opt_siblingUSC"] in rel_list
    none_rel         = (t["opt_none"] in rel_list) or (not rel_list)

    # --- Citizenship quick checks (CRBA / N-600) ---
    if A.get("parent_citizen_birth") in [Yes] and A.get("parent_presence_met") == Yes:
        if A.get("under18")==Yes and outside():
            routes.append(t["r_crba"])
        else:
            routes.append(t["r_n600_birth"])
    if A.get("parent_natz_after") in [Yes] and A.get("under18")==Yes and A.get("child_LPR")==Yes and inside():
        routes.append(t["r_n600_320"])

    # --- Immediate relatives & family routes ---
    if has_spouse_USC:
        if inside() and A.get("last_entry_lawful")==Yes:
            routes.append(t["r_ir1_aos"])
        else:
            routes.append(t["r_ir1_cp"])
    if has_spouse_LPR:
        routes.append(t["r_f2a"])
    if has_child21_USC:
        if inside() and A.get("last_entry_lawful")==Yes:
            routes.append(t["r_ir5_aos"])
        else:
            routes.append(t["r_ir5_cp"])
            notes.append(t["n_601_qr_child"])
        if outside():
            notes.append(t["n_601A_abroad"])
    if has_sibling_USC:
        routes.append(t["r_f4"])

    if none_rel:
        routes.append(t["r_default"])

    # --- Waivers / bars ---
    if (outside() or (inside() and A.get("last_entry_lawful")==No)) and A.get("unlawful_presence")==Yes:
        routes.append(t["r_i601"])
        if outside():
            notes.append(t["n_601A_abroad"])
    if A.get("prior_removal") in [Yes]:
        routes.append(t["r_i212"])
    if A.get("illegal_reentry") in [t["Once"], t["MoreThanOnce"]]:
        notes.append(t["n_9c"])
    if A.get("crim_fraud") in [Yes]:
        notes.append(t["n_crime"])

    # Render
    st.subheader(t["results"])
    st.markdown(t["disclaimer"])
    if routes:
        st.success(t["routes_label"])
        for r in routes: st.write(f"- {r}")
    else:
        st.warning(t["no_route"])
    if notes:
        st.info(t["notes_label"])
        for n in notes: st.write(f"- {n}")

    # Export (PDF + mailto)
    pdf_bytes = make_pdf(A, routes, notes, lang)
    st.download_button(label=t["pdf_btn"], data=pdf_bytes, file_name="screener_summary.pdf", mime="application/pdf")

    subject = urllib.parse.quote(t["mail_subject"])
    lines = [f"{k}: {v}" for k,v in A.items()]
    lines += ["", t["routes_label"]] + [f"- {r}" for r in routes]
    if notes: lines += ["", t["notes_label"]] + [f"- {n}" for n in notes]
    lines += ["", t["admin_note"]]
    body = urllib.parse.quote("\n".join(lines)[:1500])
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject=' + subject + '&body=' + body})")

    # Controls
    c1,c2 = st.columns(2)
    if c1.button(t["restart"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 0; rerun()
    if c2.button(t["reset"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 1; rerun()
