import streamlit as st

st.set_page_config(page_title="Immigration Consultation Screener", layout="centered")

# ----- DISCLAIMER (ALWAYS SHOW) -----
st.title("Immigration Consultation Screener")
st.markdown(
"""
**Important Disclaimer (Read First)**  
This tool is for **informational purposes only**. It does **not** provide legal advice, does **not** create an attorney-client relationship, and should **not** be relied on as a substitute for advice from a licensed immigration attorney. Results are **general guidance** based solely on your inputs and may be incomplete or inaccurate for your situation.
"""
)

st.markdown("---")

# ----- BASIC FACTS -----
st.subheader("Basic Facts")
in_us = st.radio("Where are you now?", ["Inside the U.S.", "Outside the U.S."])
born_abroad = st.radio("Were you born outside the United States?", ["Yes", "No"])
age_under_18 = st.radio("Are you under 18 years old?", ["Yes", "No"])

st.markdown("---")

# ----- FAMILY RELATIONSHIPS -----
st.subheader("Family Relationships")
usc_spouse = st.radio("Do you have a U.S. citizen spouse?", ["Yes", "No"])
lpr_spouse = st.radio("Do you have a lawful permanent resident (green card holder) spouse?", ["Yes", "No"])
usc_parent = st.radio("Do you have a U.S. citizen parent?", ["Yes", "No"])
usc_child_over21 = st.radio("Do you have a U.S. citizen son/daughter age 21 or older?", ["Yes", "No"])

st.markdown("---")

# ----- CITIZENSHIP AT/AFTER BIRTH (for CRBA / N-600 paths) -----
st.subheader("Citizenship At or After Birth")
parent_citizen_at_birth = st.radio("Was at least one of your parents a U.S. citizen **at the time of your birth**?", ["Yes", "No", "Not sure"])
parent_pres_req = st.radio("If yes/not sure: did that U.S. citizen parent likely meet U.S. physical presence/residence requirements **before** your birth?", ["Yes", "No", "Not sure"])
parent_natz_after_birth = st.radio("Did a parent become a U.S. citizen **after** your birth?", ["Yes", "No"])

st.markdown("---")

# ----- ENTRY / STATUS / BARS (very high level) -----
st.subheader("Entry / Status (High-Level)")
lawful_entry = st.radio("Was your most recent U.S. entry inspected by an officer (visa, parole, or wave-through)?", ["Yes", "No", "N/A (outside U.S.)"])
current_status = st.radio("Current U.S. status (if inside U.S.)", ["USC/LPR", "Nonimmigrant (e.g., F-1, H-1B, etc.)", "No valid status", "N/A (outside U.S.)"])
inadmissibility_flags = st.multiselect(
    "Any of the following apply? (select none if none apply)",
    [
        "Overstay/Unlawful presence",
        "Prior removal/deportation",
        "Certain criminal history",
        "Fraud/misrepresentation issues"
    ]
)

st.markdown("---")

# ----- DERIVATION CONDITIONS (INA §320) -----
st.subheader("If you are under 18 and inside the U.S.")
is_LPR = st.radio("Do you have lawful permanent resident (green card) status?", ["Yes", "No", "N/A"])
living_with_citizen_parent = st.radio("Are you living in the legal and physical custody of your U.S. citizen parent?", ["Yes", "No", "N/A"])

st.markdown("---")

# ----- DETERMINE POSSIBLE ROUTES -----
if st.button("Show Possible Routes (Informational Only)"):
    routes = []
    notes = []

    # U.S.-born -> already citizen
    if born_abroad == "No":
        routes.append("Likely already a U.S. citizen by birth (14th Amendment). Obtain/state birth certificate and U.S. passport as proof.")
    else:
        # CRBA/N-600 by citizenship at birth
        if parent_citizen_at_birth == "Yes" and parent_pres_req == "Yes":
            if in_us == "Outside the U.S." and age_under_18 == "Yes":
                routes.append("CRBA + first U.S. passport at the U.S. Embassy/Consulate (citizenship at birth).")
            elif in_us == "Inside the U.S.":
                routes.append("N-600 (proof of citizenship) if citizenship was acquired at birth.")
            else:
                routes.append("Outside the U.S. and age 18+: apply for a U.S. passport abroad with evidence of citizenship at birth; CRBA not available after 18.")
        elif parent_citizen_at_birth in ["Yes", "Not sure"] and parent_pres_req == "Not sure":
            notes.append("If the U.S. citizen parent satisfied pre-birth presence requirements, citizenship at birth may apply (CRBA if <18 and abroad, or N-600/passport if in the U.S.). Gather parent’s presence evidence.")

        # Derivation after birth (INA §320)
        if parent_natz_after_birth == "Yes":
            if in_us == "Inside the U.S." and age_under_18 == "Yes" and is_LPR == "Yes" and living_with_citizen_parent == "Yes":
                routes.append("N-600 (derivation under INA §320).")
            elif in_us == "Inside the U.S." and age_under_18 == "Yes":
                notes.append("To derive under INA §320, child must be an LPR and in legal/physical custody of the U.S. citizen parent while under 18. If not LPR yet, pursue an immigrant petition first.")
            elif in_us == "Outside the U.S.":
                notes.append("Derivation under INA §320 requires residence in the U.S. as an LPR while under 18 and in citizen parent’s custody. Consider immigrating first (I-130), then N-600 after living in the U.S. under §320 conditions.")

        # Family-based immigration (I-130) if no citizenship path
        if not routes:
            if usc_spouse == "Yes" or usc_parent == "Yes" or usc_child_over21 == "Yes" or lpr_spouse == "Yes":
                routes.append("I-130 family petition (immigrant visa/consular processing or adjustment, as applicable).")
            else:
                notes.append("If no qualifying U.S. citizen/LPR relative, family-based I-130 may not be available. Consider other categories (employment, humanitarian, etc.).")

        # Adjustment vs. consular – very high level
        if "I-130 family petition (immigrant visa/consular processing or adjustment, as applicable)." in routes:
            if in_us == "Inside the U.S.":
                if lawful_entry == "Yes":
                    routes.append("Adjustment of Status (I-485) may be possible if otherwise eligible.")
                elif lawful_entry == "No":
                    notes.append("Without a lawful admission/parole, AOS is limited; many must consular process. Waivers (e.g., I-601A) may be required if unlawful presence or other grounds apply.")
            else:
                routes.append("Consular Processing via NVC once the I-130 is approved and priority date is current.")

        # Flags
        if inadmissibility_flags:
            notes.append("Potential inadmissibility issues were indicated. Waivers (e.g., I-601/I-601A) or other remedies may be required depending on facts.")

    # ----- OUTPUT -----
    st.subheader("Informational Results")
    if routes:
        st.success("Possible routes to explore:")
        for r in routes:
            st.write(f"- {r}")
    else:
        st.warning("No clear route identified based on inputs. Further review with counsel is recommended.")

    if notes:
        st.info("Notes:")
        for n in notes:
            st.write(f"- {n}")

    st.caption(
        "This output is educational only and not legal advice. Final eligibility depends on statute/regulations in effect at birth, "
        "proof of parental physical presence, admissibility, bars/waivers, and other case-specific facts."
    )
