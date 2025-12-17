import streamlit as st
import asyncio
import websockets
import os
import pandas as pd

st.set_page_config(
    page_title="🏛️ Sunedrion – LLM Council",
    page_icon="🔱",
    layout="wide"
)

st.title("🏛️ Sunedrion – LLM Council (Streaming Mode)")

# -------------------------------------------------------------------
# BACKEND WEBSOCKET URL
# -------------------------------------------------------------------
BACKEND = os.getenv("BACKEND_URL")

if not BACKEND:
    st.error("❌ BACKEND_URL is missing. Set it in Render → Environment Variables.")
    st.stop()

WS_URL = f"{BACKEND.replace('https://', 'wss://')}/ws"

prompt = st.text_area("Enter your question:")

run_button = st.button("Run Council")

# Hold streaming output
stream_placeholders = {
    "openai": st.empty(),
    "claude": st.empty(),
    "perplexity": st.empty(),
    "kimi": st.empty(),
    "deepseek": st.empty(),
    "final": st.empty()
}

# A nice divider
st.markdown("---")

# Final score table
scores_placeholder = st.empty()


# -------------------------------------------------------------------
# ASYNC STREAM HANDLER
# -------------------------------------------------------------------
async def run_stream():
    async with websockets.connect(WS_URL) as ws:
        # Send user prompt
        await ws.send(prompt)

        async for msg in ws:
            msg = msg.strip()

            # SAFELY PARSE ANY MESSAGE FORMAT
            parts = msg.split(":", 2)

            if len(parts) == 3:
                model, msg_type, data = parts
            elif len(parts) == 2:
                model, data = parts
                msg_type = "info"
            else:
                st.write(f"⚠️ Unrecognized message format: {msg}")
                continue

            model = model.lower().strip()

            # ----------------------------------------------------------
            # MODEL-SPECIFIC STREAMING OUTPUT
            # ----------------------------------------------------------
            if model in stream_placeholders:
                stream_placeholders[model].markdown(f"### 🔹 {model.upper()}\n{data}")

            # ----------------------------------------------------------
            # FINAL JSON SUMMARY FROM CHAIRMAN
            # ----------------------------------------------------------
            if model == "finaljson":
                try:
                    import json
                    result = json.loads(data)

                    # Display final answer
                    stream_placeholders["final"].markdown(
                        f"## 🟦 Final Answer\n{result['final_answer']}"
                    )

                    # Show score table
                    df = pd.DataFrame(
                        [{"Model": k, "Score": v} for k, v in result["scores"].items()]
                    ).sort_values(by="Score", ascending=False)

                    scores_placeholder.table(df)

                except Exception as e:
                    stream_placeholders["final"].markdown(
                        f"❌ Error parsing final JSON: {e}\n\nRaw data:\n```\n{data}\n```"
                    )


# -------------------------------------------------------------------
# RUN BUTTON
# -------------------------------------------------------------------
if run_button:
    if not prompt.strip():
        st.error("Please enter a prompt.")
        st.stop()

    st.info("🔄 Running council… Streaming results below...")

    # Run async WebSocket client
    try:
        asyncio.run(run_stream())
    except Exception as e:
        st.error(f"❌ WebSocket error: {e}")
