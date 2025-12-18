import streamlit as st
import requests
from sseclient import SSEClient
import json

st.title("🏛️ Sunedrion LLM Council — Streaming Mode (SSE)")

backend_url = "https://llm-council-backend-m7fw.onrender.com/council-sse"

prompt = st.text_area("Enter your research prompt:", height=200)

if st.button("Run Council"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    st.write("### 🔄 Council Running…")
    progress = st.empty()
    final_box = st.empty()

    # SSE Stream
    url = f"{backend_url}?prompt={prompt}"
    messages = SSEClient(url)

    for event in messages:
        if not event.data:
            continue

        msg = event.data

        # FINAL JSON
        if msg.startswith("🏁 FINAL"):
            clean = msg.replace("🏁 FINAL → ", "")
            try:
                obj = json.loads(clean)
                final_box.markdown(f"### 🏁 **Final Answer:**\n{obj['final']}")
            except:
                final_box.markdown(clean)
            continue

        # Live updates
        progress.markdown(f"**{msg}**")
