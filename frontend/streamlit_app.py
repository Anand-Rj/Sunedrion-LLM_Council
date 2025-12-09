import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱"
)

st.title("🏛️ Sunedrion – LLM Council")

prompt = st.text_area("Enter your question:")

if st.button("Run Council"):
    res = requests.post(
        "http://localhost:8000/council",
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

    # Convert dict → DataFrame for table display
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

        # collapsible section
        with st.expander(f"🔽 {model_name.upper()}"):

            # if it's dictionary JSON
            if isinstance(output, dict):
                st.json(output)

            # if it's text
            elif isinstance(output, str):
                st.code(output, language="markdown")

            else:
                st.write(output)
