import streamlit as st
import requests
import sseclient
import json
import os

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱"
)

st.title("🏛️ Sunedrion – LLM Council")

BACKEND = os.getenv("BACKEND_URL")

if not BACKEND:
    st.error("❌ BACKEND_URL is missing. Set it in Render → Environment Variables.")
    st.stop()

prompt = st.text_area("Enter your question:")

if st.button("Run Council"):

    if not prompt.strip():
        st.error("Please enter a prompt.")
        st.stop()

    url = f"{BACKEND}/sse"
    params = {"prompt": prompt}

    placeholder = st.empty()
    st.write("⏳ Running council…")

    messages = sseclient.SSEClient(url, params=params)

    models_output = {}
    final_answer = None
    scores = None

    for event in messages:

        event_type = event.event
        raw = event.data

        # MODEL OUTPUT EVENT
        if event_type == "model_output":
            if "|" in raw:
                model, output = raw.split("|", 1)
                models_output[model] = output

                with placeholder.container():
                    st.subheader("Delegate Outputs (Live)")
                    for m, o in models_output.items():
                        st.write(f"### {m.upper()}")
                        st.code(o)
            else:
                st.write(raw)

        # FINAL ANSWER
        elif event_type == "final_answer":
            final_answer = raw

        # SCORES (ONLY JSON)
        elif event_type == "scores":
            try:
                scores = json.loads(raw)
            except:
                scores = None
                st.error("⚠️ Invalid scores JSON received.")

        # DONE
        elif event_type == "done":
            break

    # OUTPUT FINAL RESULTS
    if final_answer:
        st.subheader("Final Answer")
        st.markdown(final_answer)

    if scores:
        st.subheader("Scores")
        score_rows = [{"Model": k, "Score": v} for k, v in scores.items()]
        st.table(score_rows)

    st.success("Council complete!")
