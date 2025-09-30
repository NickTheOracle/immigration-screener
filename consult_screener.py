import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ================= TRANSLATIONS =================
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
        "Yes":"Yes","No":"No","Not sure":"Not sure",
        "InsideUS":"Inside the U.S.","OutsideUS":"Outside the U.S.",
        "Never":"Never","Once":"Once","MoreThanOnce":"More than once",
        "Less6":"<6 months","_6_12":"6–12 months","_12_36":"1–3 years","_3_10":"3–10 years","_10plus":"10+ years",
        # Questions
        "q_lang":"Choose language / Elija idioma / Escolha idioma",
        "q_where":"Where are you now?",
        "q_is_lpr":"Are you a lawful permanent resident (green card holder)?",
        "q_relatives":"Which U.S. relatives do you have? (select all that apply)",
        "opt_spouseUSC":"Spouse is U.S. citizen",
        "opt_spouseLPR":"Spouse is LPR",
        "opt_parentUSC":"Parent is U.S. citizen",
        "opt_child21USC":"U.S. citizen son/daughter age 21+ (you are the parent)",
        "opt_siblingUSC":"U.S. citizen brother/sister",
        "opt_none":"None",
        "q_last_entry_lawful":"Was your last U.S. entry inspected or paroled (visa, wave-through, parole)?",
        "q_unlawful_presence":"Before your last departure, did you accrue 180+ days of unlawful presence?",
        "q_time_out":"How long have you been outside the U.S. in your most recent continuous period?",
        "q_prior_removal":"Were you ever removed/deported or did you depart after being ordered removed?",
        "q_illegal_reentry":"After a removal or after >1 year of unlawful presence, did you reenter or attempt to reenter illegally?",
        "q_crim_fraud":"Any criminal issues or fraud/misrepresentation in immigration applications?",
        # Citizenship branches (N-600 / CRBA) – compact set
        "q_under18":"Are you under 18 years old?",
        "q_parent_citizen_birth":"Was a parent a U.S. citizen at your birth?",
        "q_parent_presence_met":"Did that parent meet U.S. physical presence before your birth?",
        "q_parent_natz_after":"Did a parent naturalize after your birth?",
        "q_child_LPR":"If under 18, are/were you an LPR residing in the legal and physical custody of the U.S. citizen parent?",
    },
    "es": {
        "title":"Evaluador de Consulta de Inmigración",
        "disclaimer":"**Aviso:** Solo informativo. No es asesoría legal. No crea relación abogado-cliente.",
        "start":"Iniciar","next":"Siguiente","back":"Atrás","reset":"Reiniciar","restart":"Comenzar de nuevo",
        "progress":"Paso {cur} de {total}","results":"Resultados informativos",
        "answers_hdr":"Respuestas:","routes_label":"Rutas posibles para explorar",
        "notes_label":"Notas","no_route":"No hay ruta clara. Se recomienda revisión adicional.",
        "pdf_btn":"Descargar resumen en PDF","mailto_btn":"Abrir correo para enviar resumen",
        "admin_note":"Por favor envíe este resumen al administrador o a la persona que le dio este formulario.",
        "mail_subject":"Resultados del evaluador",
        "Yes":"Sí","No":"No","Not sure":"No seguro",
        "InsideUS":"Dentro de EE. UU.","OutsideUS":"Fuera de EE. UU.",
        "Never":"Nunca","Once":"Una vez","MoreThanOnce":"Más de una vez",
        "Less6":"<6 meses","_6_12":"6–12 meses","_12_36":"1–3 años","_3_10":"3–10 años","_10plus":"10+ años",
        "q_lang":"Elija idioma / Choose language / Escolha idioma",
        "q_where":"¿Dónde se encuentra ahora?",
        "q_is_lpr":"¿Es residente permanente (green card)?",
        "q_relatives":"¿Qué familiares tiene en EE. UU.? (seleccione todos los que apliquen)",
        "opt_spouseUSC":"Cónyuge ciudadano estadounidense",
        "opt_spouseLPR":"Cónyuge residente (LPR)",
        "opt_parentUSC":"Padre/madre ciudadano(a) de EE. UU.",
        "opt_child21USC":"Hijo(a) ciudadano(a) de EE. UU. de 21+ (usted es el padre/madre)",
        "opt_siblingUSC":"Hermano(a) ciudadano(a) de EE. UU.",
        "opt_none":"Ninguno",
        "q_last_entry_lawful":"¿Su última entrada fue inspeccionada o con parole (visa, pase permitido, parole)?",
        "q_unlawful_presence":"Antes de su última salida, ¿acumuló 180+ días de presencia ilegal?",
        "q_time_out":"¿Cuánto tiempo lleva fuera de EE. UU. en su período continuo más reciente?",
        "q_prior_removal":"¿Fue alguna vez removido/deportado o salió después de una orden de remoción?",
        "q_illegal_reentry":"Después de una remoción o >1 año de presencia ilegal, ¿reingresó o intentó reingresar ilegalmente?",
        "q_crim_fraud":"¿Algún problema penal o fraude/tergiversación en inmigración?",
        "q_under18":"¿Tiene menos de 18 años?",
        "q_parent_citizen_birth":"¿Algún padre era ciudadano estadounidense al momento de su nacimiento?",
        "q_parent_presence_met":"¿Ese padre cumplió presencia física en EE. UU. antes de su nacimiento?",
        "q_parent_natz_after":"¿Algún padre se naturalizó después de su nacimiento?",
        "q_child_LPR":"Si es menor de 18, ¿es/era residente permanente viviendo bajo custodia legal y física del padre/madre ciudadano?",
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
        "Yes":"Sim","No":"Não","Not sure":"Não sei",
        "InsideUS":"Dentro dos EUA","OutsideUS":"Fora dos EUA",
        "Never":"Nunca","Once":"Uma vez","MoreThanOnce":"Mais de uma vez",
        "Less6":"<6 meses","_6_12":"6–12 meses","_12_36":"1–3 anos","_3_10":"3–10 anos","_10plus":"10+ anos",
        "q_lang":"Escolha idioma / Choose language / Elija idioma",
        "q_where":"Onde você está agora?",
        "q_is_lpr":"Você é residente permanente (green card)?",
        "q_relatives":"Quais parentes você tem nos EUA? (selecione todos os aplicáveis)",
        "opt_spouseUSC":"Cônjuge cidadão dos EUA",
        "opt_spouseLPR":"Cônjuge residente (LPR)",
        "opt_parentUSC":"Pai/mãe cidadão(ã) dos EUA",
        "opt_child21USC":"Filho(a) cidadão(ã) dos EUA com 21+ (você é o pai/mãe)",
        "opt_siblingUSC":"Irmão(ã) cidadão(ã) dos EUA",
        "opt_none":"Nenhum",
        "q_last_entry_lawful":"Sua última entrada foi inspecionada ou com parole (visto, liberação, parole)?",
        "q_unlawful_presence":"Antes da última saída, acumulou 180+ dias de presença ilegal?",
        "q_time_out":"Há quanto tempo está fora dos EUA no período contínuo mais recente?",
        "q_prior_removal":"Já foi removido/deportado ou saiu após ordem de remoção?",
        "q_illegal_reentry":"Após remoção ou >1 ano de presença ilegal, reentrou ou tentou reentrar ilegalmente?",
        "q_crim_fraud":"Algum problema penal ou fraude/deturpação em imigração?",
        "q_under18":"Você tem menos de 18 anos?",
        "q_parent_citizen_birth":"Algum dos pais era cidadão dos EUA no seu nascimento?",
        "q_parent_presence_met":"Esse pai/mãe cumpriu presença física nos EUA antes do seu nascimento?",
        "q_parent_natz_after":"Algum dos pais se naturalizou após o seu nascimento?",
        "q_child_LPR":"Se menor de 18, você é/era residente permanente residindo sob custódia legal e física do pai/mãe cidadão?",
    }
}

# ================= HELPERS =================
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
    for k, v in answers.items():
        story.append(Paragraph(f"- {k}: {v}", styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(T[lang]["routes_label"], styles["Heading2"]))
    for r in routes:
        story.append(Paragraph(f"- {r}", styles["Normal"]))
    if notes:
        story.append(Spacer(1, 12))
        story.append(Paragraph(T[lang]["notes_label"], styles["Heading2"]))
        for n in notes:
            story.append(Paragraph(f"- {n}", styles["Normal"]))
    story.append(Spacer(1, 12)); story.append(Paragraph(T[lang]["admin_note"], styles["Italic"]))
    doc.build(story)
    return buf.getvalue()

# ================= APP =================
st.set_page_config(page_title="Screener", layout="centered")

if "step" not in st.session_state: st.session_state.step = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "lang" not in st.session_state: st.session_state.lang = "en"

# Step 0: language
if st.session_state.step == 0:
    lang_choice = st.selectbox(T["en"]["q_lang"], ["English", "Español", "Português"])
    st.session_state.lang = {"English":"en", "Español":"es", "Português":"pt"}[lang_choice]
    if st.button(T[st.session_state.lang]["start"]):
        st.session_state.step = 1; rerun()

lang = st.session_state.lang
t = T[lang]
A = st.session_state.answers
Yes, No, NS = t["Yes"], t["No"], t["Not sure"]

# Show disclaimer always
st.title(t["title"])
st.markdown(t["disclaimer"])
st.markdown("---")

def q(label, opts, key, cond=lambda a: True, widget="radio"):
    return {"label":label, "opts":opts, "key":key, "cond":cond, "widget":widget}

# Cond helpers
def has(rel): return rel in (A.get("relatives") or [])
def any_rel(): return bool(A.get("relatives"))
inside = lambda: A.get("where")==t["InsideUS"]
outside = lambda: A.get("where")==t["OutsideUS"]

# Core questions (only what’s needed for branching)
Q = [
    q(t["q_where"], [t["InsideUS"], t["OutsideUS"]], "where"),
    q(t["q_relatives"], [t["opt_spouseUSC"], t["opt_spouseLPR"], t["opt_parentUSC"], t["opt_child21USC"], t["opt_siblingUSC"], t["opt_none"]],
      "relatives", widget="multiselect"),
    # For immediate relatives in the U.S. we need last entry inspection for AOS
    q(t["q_last_entry_lawful"], [Yes, No, NS], "last_entry_lawful",
      cond=lambda a: inside() and (has(t["opt_spouseUSC"]) or has(t["opt_child21USC"]) or has(t["opt_parentUSC"]))),
    # Bars/waivers – only when consular processing will likely be required
    q(t["q_unlawful_presence"], [Yes, No, NS], "unlawful_presence",
      cond=lambda a: outside() or (inside() and a.get("last_entry_lawful")==No)),
    q(t["q_time_out"], [t["Less6"], t["_6_12"], t["_12_36"], t["_3_10"], t["_10plus"]], "time_out",
      cond=lambda a: outside()),
    q(t["q_prior_removal"], [Yes, No], "prior_removal",
      cond=lambda a: outside() or (inside() and a.get("last_entry_lawful")==No)),
    q(t["q_illegal_reentry"], [t["Never"], t["Once"], t["MoreThanOnce"]], "illegal_reentry",
      cond=lambda a: a.get("prior_removal")==Yes or a.get("unlawful_presence")==Yes),
    q(t["q_crim_fraud"], [Yes, No], "crim_fraud",
      cond=lambda a: any_rel()),
    # Citizenship quick triage (optional, appears for minors or anyone claiming parent USC)
    q(t["q_under18"], [Yes, No], "under18",
      cond=lambda a: True),
    q(t["q_parent_citizen_birth"], [Yes, No], "parent_citizen_birth",
      cond=lambda a: True),
    q(t["q_parent_presence_met"], [Yes, No, NS], "parent_presence_met",
      cond=lambda a: a.get("parent_citizen_birth")==Yes),
    q(t["q_parent_natz_after"], [Yes, No], "parent_natz_after",
      cond=lambda a: True),
    q(t["q_child_LPR"], [Yes, No, "N/A"], "child_LPR",
      cond=lambda a: a.get("under18")==Yes),
]

# Visible questions now
VISIBLE = [qq for qq in Q if qq["cond"](A)]
TOTAL = len(VISIBLE)
if st.session_state.step > TOTAL: st.session_state.step = TOTAL + 1
cur = st.session_state.step

# Progress
if 1 <= cur <= TOTAL:
    st.write(t["progress"].format(cur=cur, total=TOTAL))
    st.progress((cur-1)/TOTAL if TOTAL else 1.0)

# One-at-a-time UI
if 1 <= cur <= TOTAL:
    qd = VISIBLE[cur-1]
    label, opts, key, widget = qd["label"], qd["opts"], qd["key"], qd["widget"]
    prev = A.get(key)

    if widget == "multiselect":
        default = prev if isinstance(prev, list) else ([] if prev is None else [prev])
        choice = st.multiselect(label, opts, default=default)
    else:
        idx = opts.index(prev) if prev in opts else 0
        choice = st.radio(label, opts, index=idx, key=f"q_{key}")

    c1,c2,c3 = st.columns(3)
    if c1.button(t["back"], disabled=(cur==1), use_container_width=True):
        A[key] = choice; st.session_state.step = cur-1; rerun()
    if c2.button(t["reset"], use_container_width=True):
        st.session_state.answers = {}; st.session_state.step = 0; rerun()
    if c3.button(t["next"], use_container_width=True):
        A[key] = choice; st.session_state.step = cur+1; rerun()

# ===== Results =====
if cur > TOTAL:
    routes, notes = [], []

    rels = A.get("relatives") or []
    has_spouse_USC   = t["opt_spouseUSC"] in rels
    has_spouse_LPR   = t["opt_spouseLPR"] in rels
    has_parent_USC   = t["opt_parentUSC"] in rels
    has_child21_USC  = t["opt_child21USC"] in rels   # IR-5 parent route
    has_sibling_USC  = t["opt_siblingUSC"] in rels
    no_relatives     = t["opt_none"] in rels or not rels

    # ---------- Citizenship quick checks (CRBA / N-600) ----------
    if A.get("parent_citizen_birth")==Yes and A.get("parent_presence_met")==Yes:
        if A.get("under18")==Yes and outside():
            routes.append("CRBA + first U.S. passport at post (citizenship at birth).")
        else:
            routes.append("N-600 / U.S. passport as proof of citizenship acquired at birth.")
    if A.get("parent_natz_after")==Yes and A.get("under18")==Yes and A.get("child_LPR")==Yes and inside():
        routes.append("N-600 (derivation under INA §320).")

    # ---------- Immediate relatives & family routes ----------
    # IR-1/CR-1 spouse of USC
    if has_spouse_USC:
        if inside() and A.get("last_entry_lawful")==Yes:
            routes.append("Adjustment of Status via I-130/I-485 (spouse of U.S. citizen, lawful entry).")
        else:
            routes.append("Consular processing (IR-1/CR-1). If unlawful presence applies, I-601 at consular stage; "
                          "I-601A possible only if applicant is IN the U.S. and has a USC/LPR spouse/parent as qualifying relative.")
    # F2A spouse of LPR
    if has_spouse_LPR:
        routes.append("I-130 (spouse of LPR). When PD current → AOS (with lawful entry) or consular processing.")
    # IR-5 parent of USC 21+ (your reported issue)
    if has_child21_USC:
        if inside() and A.get("last_entry_lawful")==Yes:
            routes.append("IR-5 Adjustment of Status via I-130/I-485 (parent of U.S. citizen 21+, lawful entry).")
        else:
            routes.append("IR-5 Consular processing via NVC. If unlawful presence applies, file I-601 at consular stage.")
            notes.append("For I-601 extreme-hardship, the qualifying relative must be the applicant’s USC/LPR **spouse or parent** — not the USC child.")
        # 601A notice
        if outside():
            notes.append("I-601A provisional waiver is **not available** outside the U.S.; abroad use Form I-601.")
    # F4 sibling of USC
    if has_sibling_USC:
        routes.append("F4 (sibling of USC): maintain petition; when PD current → NVC and consular processing.")

    # Generic family note
    if no_relatives:
        notes.append("No qualifying family relationship indicated; consider employment or humanitarian options.")

    # ---------- Bars / waivers ----------
    # Unlawful presence → I-601 at consular stage (never I-601A abroad)
    if (outside() or (inside() and A.get("last_entry_lawful")==No)) and A.get("unlawful_presence")==Yes:
        routes.append("I-601 waiver for unlawful presence (show extreme hardship to USC/LPR spouse or parent).")
    if outside():
        notes.append("I-601A provisional waiver unavailable abroad; only I-601 applies at consular stage.")

    # Prior removal → I-212
    if A.get("prior_removal")==Yes:
        routes.append("I-212 (permission to reapply) due to prior removal/deportation (can be filed with the I-601 package).")

    # Possible 9(C) permanent bar
    if A.get("illegal_reentry") in [t["Once"], t["MoreThanOnce"]]:
        notes.append("Possible INA 212(a)(9)(C) permanent bar (illegal reentry after removal or after >1yr unlawful presence). "
                     "Often requires 10 years outside then I-212; I-601A not available.")

    # Criminal/fraud flags
    if A.get("crim_fraud")==Yes:
        notes.append("Potential additional inadmissibility (criminal/fraud). Case-specific waivers may be required.")

    # Default path if nothing else hit
    if not routes:
        routes.append("Verify/finalize I-130 basis; if consular processing, prepare DS-260, fees, civil docs, and assess any required waivers (I-601 and/or I-212).")

    # ===== Render results =====
    st.subheader(t["results"])
    st.markdown(t["disclaimer"])
    st.success(t["routes_label"])
    for r in routes: st.write(f"- {r}")
    if notes:
        st.info(t["notes_label"])
        for n in notes: st.write(f"- {n}")

    # Export
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
