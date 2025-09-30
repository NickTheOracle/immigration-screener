import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io, datetime, urllib.parse

# ================= TRANSLATIONS (EN/ES/PT) =================
T = {
    "en": {
        "title": "Immigration Consultation Screener",
        "disclaimer": "**Disclaimer:** Informational only. Not legal advice. No attorney–client relationship is created.",
        "start": "Start","next": "Next","back": "Back","reset": "Reset","restart":"Start Over",
        "progress": "Step {cur} of {total}","results": "Informational Results",
        "answers_hdr": "Answers:","routes_label": "Possible routes to explore",
        "notes_label": "Notes","no_route": "No clear route identified. Further review recommended.",
        "pdf_btn": "Download PDF summary","mailto_btn": "Open email to send summary",
        "admin_note": "Please send this summary to the administrator or the person who gave you this form.",
        "mail_subject": "Screener Results",
        "Yes":"Yes","No":"No","Not sure":"Not sure",
        "InsideUS":"Inside the U.S.","OutsideUS":"Outside the U.S.",
        "Never":"Never","Once":"Once","MoreThanOnce":"More than once",
        "Less6":"<6 months","_6_12":"6–12 months","_12_36":"1–3 years","_3_10":"3–10 years","_10plus":"10+ years",
        # Questions
        "q_lang":"Choose language / Elija idioma / Escolha idioma",
        "q_where":"Where are you now?","q_lpr":"Are you a lawful permanent resident (green card holder)?",
        "q_lpr_years":"How long have you been an LPR?","q_married_usc":"Married to U.S. citizen and lived in union 3+ years?",
        "q_continuous":"Continuous residence (no 6+ month trips)?","q_trips6":"Any single trip outside 6+ months?",
        "q_good_moral":"Any arrests/convictions in last 5 yrs?","q_selective":"If male 18–26 in U.S., registered Selective Service?",
        "q_under_18":"Are you under 18?","q_parent_citizen_birth":"Was a parent a U.S. citizen at your birth?",
        "q_parent_presence_met":"Did that parent meet U.S. physical presence?","q_parent_natz_after":"Did a parent naturalize after your birth?",
        "q_live_with_usc_parent":"Did/Do you live with USC parent?","q_is_LPR_child":"Is the child an LPR?",
        "q_family_heads":"Which U.S. relatives? (select all)","opt_spouseUSC":"Spouse USC","opt_spouseLPR":"Spouse LPR",
        "opt_parentUSC":"Parent USC","opt_child21USC":"Child USC 21+","opt_siblingUSC":"Sibling USC","opt_none":"None",
        "q_pd_current":"If approved petition, is PD current on Visa Bulletin?","q_time_out":"Time outside U.S.?",
        "q_prior_removal":"Ever removed/deported?","q_illegal_reentry":"After removal or >1yr UP, reentered illegally?",
        "q_unlawful_presence":"Before last departure, 180+ days unlawful presence?","q_lawful_entry_last":"Last entry inspected/paroled?",
        "q_crim_fraud":"Any crime/fraud in immigration?","q_fear":"Fear harm if returned / past persecution?",
        "q_one_year":"If inside, entered <1yr ago (or exception)?","q_u_victim":"Victim of crime in U.S.?",
        "q_u_harm":"Substantial harm from that crime?","q_u_report":"Reported & helped authorities?",
    },
    "es": {
        "title":"Evaluador de Consulta de Inmigración",
        "disclaimer":"**Aviso:** Solo informativo. No es asesoría legal. No crea relación abogado-cliente.",
        "start":"Iniciar","next":"Siguiente","back":"Atrás","reset":"Reiniciar","restart":"Comenzar de nuevo",
        "progress":"Paso {cur} de {total}","results":"Resultados informativos",
        "answers_hdr":"Respuestas:","routes_label":"Rutas posibles para explorar",
        "notes_label":"Notas","no_route":"No hay ruta clara. Se recomienda revisión adicional.",
        "pdf_btn":"Descargar PDF","mailto_btn":"Abrir correo para enviar resumen",
        "admin_note":"Por favor envíe este resumen al administrador o a la persona que le dio este formulario.",
        "mail_subject":"Resultados del evaluador",
        "Yes":"Sí","No":"No","Not sure":"No seguro",
        "InsideUS":"Dentro de EE. UU.","OutsideUS":"Fuera de EE. UU.",
        "Never":"Nunca","Once":"Una vez","MoreThanOnce":"Más de una vez",
        "Less6":"<6 meses","_6_12":"6–12 meses","_12_36":"1–3 años","_3_10":"3–10 años","_10plus":"10+ años",
        "q_lang":"Elija idioma / Choose language / Escolha idioma","q_where":"¿Dónde se encuentra ahora?",
        "q_lpr":"¿Es residente permanente (green card)?","q_lpr_years":"¿Cuánto tiempo lleva como residente?",
        "q_married_usc":"¿Casado(a) con ciudadano(a) 3+ años?","q_continuous":"¿Residencia continua (sin viajes 6+ meses)?",
        "q_trips6":"¿Algún viaje único de 6+ meses?","q_good_moral":"¿Arrestos/condenas últimos 5 años?",
        "q_selective":"Si hombre 18–26 en EE. UU., ¿registrado en Servicio Selectivo?","q_under_18":"¿Menor de 18?",
        "q_parent_citizen_birth":"¿Algún padre era ciudadano al nacer usted?","q_parent_presence_met":"¿Ese padre cumplió presencia física?",
        "q_parent_natz_after":"¿Algún padre naturalizó después de su nacimiento?","q_live_with_usc_parent":"¿Vivió/vive con padre ciudadano?",
        "q_is_LPR_child":"¿El menor es residente permanente?","q_family_heads":"¿Qué familiares tiene en EE. UU.?",
        "opt_spouseUSC":"Cónyuge ciudadano","opt_spouseLPR":"Cónyuge residente","opt_parentUSC":"Padre/madre ciudadano",
        "opt_child21USC":"Hijo(a) ciudadano 21+","opt_siblingUSC":"Hermano(a) ciudadano","opt_none":"Ninguno",
        "q_pd_current":"¿Fecha vigente en Boletín de Visas?","q_time_out":"Tiempo fuera de EE. UU.?","q_prior_removal":"¿Fue removido/deportado?",
        "q_illegal_reentry":"Tras remoción o >1 año, ¿reingresó ilegalmente?","q_unlawful_presence":"¿180+ días presencia ilegal?",
        "q_lawful_entry_last":"¿Última entrada inspeccionada/parole?","q_crim_fraud":"¿Problema penal/fraude?",
        "q_fear":"¿Teme daño si regresa / persecución pasada?","q_one_year":"Si dentro, ¿entró hace <1 año (o excepción)?",
        "q_u_victim":"¿Víctima de delito en EE. UU.?","q_u_harm":"¿Daño físico/mental sustancial?","q_u_report":"¿Reportó y cooperó?",
    },
    "pt": {
        "title":"Triagem de Consulta de Imigração",
        "disclaimer":"**Aviso:** Apenas informativo. Não é aconselhamento jurídico. Não cria relação advogado-cliente.",
        "start":"Iniciar","next":"Avançar","back":"Voltar","reset":"Reiniciar","restart":"Recomeçar",
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
        "q_lang":"Escolha idioma / Choose language / Elija idioma","q_where":"Onde você está agora?",
        "q_lpr":"É residente permanente (green card)?","q_lpr_years":"Há quanto tempo é residente?",
        "q_married_usc":"Casado(a) com cidadão(ã) 3+ anos?","q_continuous":"Residência contínua (sem viagens 6+ meses)?",
        "q_trips6":"Alguma viagem única 6+ meses?","q_good_moral":"Prendeu/condenações últimos 5 anos?",
        "q_selective":"Se homem 18–26 nos EUA, registrou no Serviço Militar?","q_under_18":"Menor de 18?",
        "q_parent_citizen_birth":"Algum dos pais era cidadão ao nascer?","q_parent_presence_met":"Esse pai cumpriu presença física?",
        "q_parent_natz_after":"Algum dos pais naturalizou após nascimento?","q_live_with_usc_parent":"Reside(u) com pai/mãe cidadão?",
        "q_is_LPR_child":"A criança é residente permanente?","q_family_heads":"Quais parentes tem nos EUA?",
        "opt_spouseUSC":"Cônjuge cidadão","opt_spouseLPR":"Cônjuge residente","opt_parentUSC":"Pai/mãe cidadão",
        "opt_child21USC":"Filho(a) cidadão 21+","opt_siblingUSC":"Irmão(ã) cidadão","opt_none":"Nenhum",
        "q_pd_current":"Data de prioridade atual?","q_time_out":"Tempo fora dos EUA?","q_prior_removal":"Já foi removido/deportado?",
        "q_illegal_reentry":"Após remoção ou >1 ano, reentrou ilegalmente?","q_unlawful_presence":"180+ dias presença ilegal?",
        "q_lawful_entry_last":"Última entrada inspecionada/parole?","q_crim_fraud":"Problema penal/fraude?",
        "q_fear":"Tem medo se retornar / perseguição passada?","q_one_year":"Se dentro, entrou <1 ano atrás (ou exceção)?",
        "q_u_victim":"Vítima de crime nos EUA?","q_u_harm":"Dano físico/mental substancial?","q_u_report":"Reportou e cooperou?",
    }
}

# ================ HELPERS =================
def rerun():
    if hasattr(st,"rerun"): st.rerun()
    else: st.experimental_rerun()

def make_pdf(answers,routes,notes,lang):
    buf=io.BytesIO();doc=SimpleDocTemplate(buf,pagesize=letter)
    styles=getSampleStyleSheet()
    story=[Paragraph(T[lang]["title"],styles["Title"]),Spacer(1,12)]
    story+=[Paragraph(T[lang]["disclaimer"],styles["Italic"]),Spacer(1,12)]
    story+=[Paragraph(T[lang]["answers_hdr"],styles["Heading2"])]
    for k,v in answers.items(): story.append(Paragraph(f"- {k}: {v}",styles["Normal"]))
    story.append(Spacer(1,12));story.append(Paragraph(T[lang]["routes_label"],styles["Heading2"]))
    for r in routes: story.append(Paragraph(f"- {r}",styles["Normal"]))
    if notes: story.append(Spacer(1,12));story.append(Paragraph(T[lang]["notes_label"],styles["Heading2"]))
    for n in notes: story.append(Paragraph(f"- {n}",styles["Normal"]))
    story.append(Spacer(1,12));story.append(Paragraph(T[lang]["admin_note"],styles["Italic"]))
    doc.build(story);return buf.getvalue()

# ================ APP =================
st.set_page_config(page_title="Screener",layout="centered")
if "step" not in st.session_state: st.session_state.step=0
if "answers" not in st.session_state: st.session_state.answers={}
if "lang" not in st.session_state: st.session_state.lang="en"

# Step 0: language
if st.session_state.step==0:
    lang_choice=st.selectbox(T["en"]["q_lang"],["English","Español","Português"])
    st.session_state.lang={"English":"en","Español":"es","Português":"pt"}[lang_choice]
    if st.button(T[st.session_state.lang]["start"]): st.session_state.step=1;rerun()

lang=st.session_state.lang;t=T[lang];A=st.session_state.answers
Yes,No,NS=t["Yes"],t["No"],t["Not sure"]

def q(label,opts,key,cond=lambda a:True): return {"label":label,"opts":opts,"key":key,"cond":cond}

Q=[
    q(t["q_where"],[t["InsideUS"],t["OutsideUS"]],"where"),
    q(t["q_lpr"],[Yes,No],"is_lpr"),
    {"label":t["q_family_heads"],"opts":[t["opt_spouseUSC"],t["opt_spouseLPR"],t["opt_parentUSC"],t["opt_child21USC"],t["opt_siblingUSC"],t["opt_none"]],"key":"relatives","cond":lambda a:True},
]

VISIBLE=[qq for qq in Q if qq["cond"](A)];TOTAL=len(VISIBLE)
if st.session_state.step>TOTAL: st.session_state.step=TOTAL+1
cur=st.session_state.step

# Show disclaimer always
st.markdown(t["disclaimer"]);st.markdown("---")

# Questions
if 1<=cur<=TOTAL:
    qd=VISIBLE[cur-1];label,opts,key=qd["label"],qd["opts"],qd["key"]
    prev=A.get(key)
    if key=="relatives":
        choice=st.multiselect(label,opts,default=prev if isinstance(prev,list) else [])
    else:
        idx=opts.index(prev) if prev in opts else 0
        choice=st.radio(label,opts,index=idx,key=f"q_{key}")
    cols=st.columns(3)
    if cols[0].button(t["back"],disabled=(cur==1)): A[key]=choice;st.session_state.step=cur-1;rerun()
    if cols[1].button(t["reset"]): st.session_state.answers={};st.session_state.step=0;rerun()
    if cols[2].button(t["next"]): A[key]=choice;st.session_state.step=cur+1;rerun()

# Final results
if cur>TOTAL:
    routes=["Example route: I-130 family petition.","Example route: N-400 naturalization"]
    notes=["Disclaimer repeated here. Add logic for I-601/I-212/N-600/CRBA/Asylum/U-Visa."]
    st.subheader(t["results"]);st.markdown(t["disclaimer"])
    for r in routes: st.write("- "+r)
    for n in notes: st.write("Note: "+n)
    pdf=make_pdf(A,routes,notes,lang)
    st.download_button(label=t["pdf_btn"],data=pdf,file_name="screener_summary.pdf",mime="application/pdf")
    st.markdown(f"[{t['mailto_btn']}]({'mailto:?subject='+urllib.parse.quote(t['mail_subject'])+'&body='+urllib.parse.quote(str(routes+notes))})")
    cols=st.columns(2)
    if cols[0].button(t["restart"]): st.session_state.answers={};st.session_state.step=0;rerun()
    if cols[1].button(t["reset"]): st.session_state.answers={};st.session_state.step=1;rerun()
