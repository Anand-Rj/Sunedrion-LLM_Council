import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱"
)

st.title("🏛️ Sunedrion – LLM Council")

# ---------------------------------------------------------
# LOAD BACKEND URL (from Render Environment Variable)
# ---------------------------------------------------------
BACKEND = os.getenv("BACKEND_URL")

# Debug print - remove later
#st.write("🔧 BACKEND URL detected:", BACKEND)

if not BACKEND:
    st.error("❌ BACKEND_URL is missing. Set it in Render → Environment Variables.")
    st.stop()

prompt = st.text_area("Enter your question:")

# ---------------------------------------------------------
# RUN COUNCIL
# ---------------------------------------------------------
if st.button("Run Council"):

    try:
        response = requests.post(
            f"{BACKEND}/council",
            json={"prompt": prompt},
            timeout=90  # free backend wakes up slowly
        )
    except Exception as e:
        st.error(f"❌ Could not reach backend: {e}")
        st.stop()

    # ---------------------------------------------------------
    # BACKEND ERROR HANDLING
    # ---------------------------------------------------------
    if response.status_code != 200:
        st.error("❌ Backend returned an error:")
        st.code(response.text)
        st.stop()

    # Convert to JSON safely
    try:
        res = response.json()
    except:
        st.error("❌ Backend did not return valid JSON.")
        st.code(response.text)
        st.stop()

    #st.write("📬 Raw response from backend:", res)

    # ---------------------------------------------------------
    # VALIDATION FOR REQUIRED KEYS
    # ---------------------------------------------------------
    required_keys = ["final", "scores", "outputs"]
    for key in required_keys:
        if key not in res:
            st.error(f"❌ Backend response missing field: '{key}'")
            st.write("Full response:", res)
            st.stop()

    # ---------------------------------------------------------
    # FINAL ANSWER
    # ---------------------------------------------------------
    st.subheader("Final Answer")
    st.markdown(res["final"])

    # ---------------------------------------------------------
    # SCORES TABLE
    # ---------------------------------------------------------
    st.subheader("Scores")
    df_scores = pd.DataFrame(
        [{"Model": k, "Score": v} for k, v in res["scores"].items()]
    ).sort_values(by="Score", ascending=False)
    st.table(df_scores)

    # ---------------------------------------------------------
    # RAW OUTPUTS FROM EACH DELEGATE
    # ---------------------------------------------------------
    st.subheader("Raw Delegate Outputs")

    for model_name, output in res["outputs"].items():
        with st.expander(f"🔽 {model_name.upper()}"):

            if isinstance(output, dict):
                st.json(output)
            elif isinstance(output, str):
                st.code(output, language="markdown")
            else:
                st.write(output)
