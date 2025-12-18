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
    st.error("❌ BACKEND_URL missing")
    st.stop()

prompt = st.text_area("Enter your question:")

if st.button("Run Council"):

    if not prompt:
        st.warning("Please enter a prompt.")
        st.stop()

    st.write("⏳ Starting council...")

    # Create SSE request
    try:
        response = requests.get(
            f"{BACKEND}/sse",
            params={"prompt": prompt},
            stream=True,
            timeout=300
        )
    except Exception as e:
        st.error(f"❌ Failed to connect to backend: {e}")
        st.stop()

    # Initialize SSE client properly
    messages = sseclient.SSEClient(response)

    # UI holders
    final_box = st.empty()
    scores_box = st.empty()
    logs_box = st.empty()

    logs = []

    # ------------------------------------------------------
    # FIX: THE CORRECT ITERATION METHOD → messages.events()
    # ------------------------------------------------------
    for event in messages.events():

        if event.event == "log":
            logs.append(event.data)
            logs_box.write("\n".join(logs))

        elif event.event == "model_start":
            logs.append(f"🚀 {event.data} started")
            logs_box.write("\n".join(logs))

        elif event.event == "model_output":
            out = json.loads(event.data)
            logs.append(f"✅ {out['model']} finished")
            logs_box.write("\n".join(logs))

        elif event.event == "model_error":
            err = json.loads(event.data)
            logs.append(f"❌ {err['model']} ERROR: {err['error']}")
            logs_box.write("\n".join(logs))

        elif event.event == "final_answer":
            final_box.markdown("### 🧠 Final Answer\n" + event.data)

        elif event.event == "scores":
            scores_box.json(json.loads(event.data))

        elif event.event == "done":
            st.success("Council completed!")
            break
