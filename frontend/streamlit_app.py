import streamlit as st
import requests
import os

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱",
    layout="wide"
)

st.title("🏛️ Sunedrion – LLM Council")

BACKEND = os.getenv("BACKEND_URL")

if not BACKEND:
    st.error("❌ BACKEND_URL is not set in environment variables.")
    st.stop()

prompt = st.text_area("Enter your prompt:", height=200)

col1, col2 = st.columns([1, 4])

with col1:
    run = st.button("Run Council", type="primary")

final_answer_box = st.empty()
delegate_container = st.container()
score_container = st.container()

if run:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    with st.spinner("Council is deliberating..."):
        try:
            response = requests.post(
                f"{BACKEND}/council/run",
                params={"prompt": prompt},
                timeout=600
            )
        except Exception as e:
            st.error(f"Backend connection failed: {e}")
            st.stop()

        if response.status_code != 200:
            st.error(f"Backend Error: {response.text}")
            st.stop()

        data = response.json()

        delegates = data["delegate_outputs"]
        final_answer = data["final_answer"]

        # -------------------------
        # Display Final Answer
        # -------------------------
        final_answer_box.subheader("🏆 Final Chairman Verdict")
        final_answer_box.markdown(final_answer)

        # -------------------------
        # Delegates Output
        # -------------------------
        st.subheader("🧠 Delegate Model Outputs")

        for model, output in delegates.items():
            st.markdown(f"### 🔹 {model.upper()}")
            st.code(output, language="markdown")

        # -------------------------
        # Score Table (text similarity)
        # -------------------------
        st.subheader("📊 Delegate Agreement Score")

        # Compute simple matching score for display
        scores = {}
        for model, output in delegates.items():
            overlap = len(set(final_answer.split()) & set(output.split()))
            scores[model] = overlap

        st.table(scores)
