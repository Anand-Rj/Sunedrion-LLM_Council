import streamlit as st
import asyncio
import websockets
import json
import os

st.set_page_config(page_title="🏛️ Sunedrion – LLM Council", page_icon="🔱")
st.title("🏛️ Sunedrion – LLM Council (Streaming Mode)")

BACKEND = os.getenv("BACKEND_URL").replace("https://", "wss://")

prompt = st.text_area("Enter your question:")

if st.button("Run Council"):

    placeholder = st.empty()
    result_box = st.empty()
    scores_box = st.empty()

    async def run_stream():
        async with websockets.connect(f"{BACKEND}/council-stream") as ws:

            await ws.send(prompt)

            final_answer = None
            scores = None

            async for msg in ws:

                if msg.startswith("STATUS:START"):
                    placeholder.write("🚀 Running council...")

                elif "STARTED" in msg:
                    model = msg.split(":")[0]
                    placeholder.write(f"⚙️ {model} started...")

                elif "FINISHED" in msg:
                    model, _, data = msg.split(":", 2)
                    placeholder.write(f"✅ {model} finished")
                
                elif msg.startswith("CHAIRMAN:FINAL"):
                    final_answer = msg.split(":", 2)[2]
                    result_box.markdown(f"### 🏛 Final Answer\n{final_answer}")

                elif msg.startswith("CHAIRMAN:SCORES"):
                    scores = json.loads(msg.split(":", 2)[2])
                    scores_list = [{"Model": k, "Score": v} for k, v in scores.items()]
                    import pandas as pd
                    scores_box.table(pd.DataFrame(scores_list))

                elif msg == "STATUS:COMPLETE":
                    placeholder.write("🎉 Completed!")
                    break

    asyncio.run(run_stream())
