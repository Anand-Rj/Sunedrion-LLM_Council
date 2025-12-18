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

# ---------------------------------------------------------
# LOAD BACKEND URL
# ---------------------------------------------------------
BACKEND = os.getenv("BACKEND_URL")

if not BACKEND:
    st.error("❌ BACKEND_URL is missing. Set it in Render → Environment Variables.")
    st.stop()

prompt = st.text_area("Enter your question:")

# Output placeholders
final_answer_box = st.empty()
scores_box = st.empty()
models_box = st.container()

# ---------------------------------------------------------
# STREAMING LOGIC
# ---------------------------------------------------------
if st.button("Run Council"):

    with st.spinner("Council is thinking..."):

        # 1️⃣ Build SSE URL
        url = f"{BACKEND}/sse"
        full_url = f"{url}?prompt={requests.utils.quote(prompt)}"

        # 2️⃣ Create SSE client (NO params argument)
        messages = sseclient.SSEClient(full_url)

        open_models = {}  # store outputs for display

        # 3️⃣ Listen to SSE events
        for event in messages:

            if not event.data:
                continue

            event_type = event.event
            raw = event.data

            # -----------------------------------------
            # Each delegate model output
            # -----------------------------------------
            if event_type == "model_output":
                # backend sends → "model_name|output text"
                try:
                    model, output = raw.split("|", 1)
                except:
                    continue  # malformed event

                open_models[model] = output

                with models_box:
                    st.markdown(f"### 🔹 {model.upper()}")
                    st.code(output)

            # -----------------------------------------
            # Final Answer (string, NOT json)
            # -----------------------------------------
            elif event_type == "final_answer":
                final_answer_box.subheader("Final Answer")
                final_answer_box.markdown(raw)

            # -----------------------------------------
            # Scores JSON (ONLY this is JSON)
            # -----------------------------------------
            elif event_type == "scores":
                try:
                    scores = json.loads(raw)
                    df = [{"Model": k, "Score": v} for k, v in scores.items()]
                    scores_box.subheader("Scores")
                    scores_box.write(df)
                except:
                    scores_box.error("Invalid scores JSON")

            # -----------------------------------------
            # Stream finished
            # -----------------------------------------
            elif event_type == "done":
                st.success("Council complete!")
                break

            # -----------------------------------------
            # Errors coming from backend
            # -----------------------------------------
            elif event_type == "error":
                st.error(f"Backend: {raw}")

