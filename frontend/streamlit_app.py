import streamlit as st
import requests
import pandas as pd
import os   # <-- added for environment variable support

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱"
)

st.title("🏛️ Sunedrion – LLM Council")

# --------------------------------------------
# USE BACKEND URL FROM RENDER ENVIRONMENT
# --------------------------------------------
BACKEND = os.getenv("BACKEND_URL")
# Example value in Render:
# BACKEND_URL = https://llm-council-backend.onrender.com

prompt = st.text_area("Enter your question:")

if st.button("Run Council"):

    res = requests.post(
        f"{BACKEND}/council",
        json={"prompt": prompt}
    ).json()

    # -----------------------------------
    # FINAL ANSWER (Nicely Rendered)
    # -----------------------------------
    st.subheader("Final Answer")
    st.markdown(res["final"])   # keep existing variable name

    # -----------------------------------
    # SCORES AS NICE TABLE
    # -----------------------------------
    st.subheader("Scores")

    scores_dict = res["scores"]  # same variable

    df_scores = pd.DataFrame(
        [{"Model": k, "Score": v} for k, v in scores_dict.items()]
    ).sort_values(by="Score", ascending=False)

    st.table(df_scores)

    # -----------------------------------
    # RAW DELEGATE OUTPUTS (Per Model)
    # -----------------------------------
    st.subheader("Raw Delegate Outputs")

    outputs = res["outputs"]  # same variable

    for model_name, output in outputs.items():
        with st.expander(f"🔽 {model_name.upper()}"):

            if isinstance(output, dict):
                st.json(output)
            elif isinstance(output, str):
                st.code(output, language="markdown")
            else:
                st.write(output)
