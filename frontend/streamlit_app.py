import streamlit as st
import requests
import sseclient
import json
import os

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱"
)

st.title("🏛️ Sunedrion – LLM Council (Streaming Mode)")

BACKEND = os.getenv("BACKEND_URL")

if not BACKEND:
    st.error("❌ BACKEND_URL missing in Render environment variables.")
    st.stop()

prompt = st.text_area("Enter your prompt")

final_answer_box = st.empty()
scores_box = st.empty()
models_box = st.container()

if st.button("Run Council"):

    with st.spinner("Council is thinking..."):

        # Build SSE URL
        url = f"{BACKEND}/sse"
        full_url = f"{url}?prompt={requests.utils.quote(prompt)}"

        # -----------------------------------------
        # ⭐ CORRECT WAY → Use requests.get(stream=True)
        # -----------------------------------------
        try:
            response = requests.get(full_url, stream=True)
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
            st.stop()

        if response.status_code != 200:
            st.error(f"SSE connection failed: {response.text}")
            st.stop()

        # Feed raw HTTP stream → SSEClient
        client = sseclient.SSEClient(response)

        # Accumulate delegate outputs
        model_outputs = {}

        # -----------------------------------------
        # Listen to SSE messages
        # -----------------------------------------
        for event in client.events():

            event_type = event.event
            raw = event.data

            if not raw:
                continue

            # -----------------------------
            # Delegate model output
            # -----------------------------
            if event_type == "model_output":
                try:
                    model, output = raw.split("|", 1)
                except:
                    continue

                model_outputs[model] = output

                with models_box:
                    st.markdown(f"### 🔹 {model.upper()}")
                    st.code(output)

            # -----------------------------
            # Final answer
            # -----------------------------
            elif event_type == "final_answer":
                final_answer_box.subheader("Final Answer")
                final_answer_box.markdown(raw)

            # -----------------------------
            # Scores (this IS JSON)
            # -----------------------------
            elif event_type == "scores":
                try:
                    scores = json.loads(raw)
                    scores_box.subheader("Scores")
                    scores_box.write(scores)
                except:
                    scores_box.error("Invalid scores JSON")

            # -----------------------------
            # Done event → stop stream
            # -----------------------------
            elif event_type == "done":
                st.success("Council complete!")
                break

            # -----------------------------
            # Error event
            # -----------------------------
            elif event_type == "error":
                st.error(f"Backend Error: {raw}")

