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

    # Build SSE URL with encoded query param
    base_url = f"{BACKEND}/sse"
    full_url = f"{base_url}?prompt={requests.utils.quote(prompt)}"

    placeholder = st.empty()
    st.write("⏳ Running council…")

    try:
        messages = sseclient.SSEClient(full_url)
    except Exception as e:
        st.error(f"❌ Could not connect to SSE endpoint: {e}")
        st.stop()

    models_output = {}
    final_answer = None
    scores = None

    for event in messages:

        event_type = event.event or ""   # sometimes None
        raw = event.data or ""

        # MODEL OUTPUT
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

        # SCORES JSON
        elif event_type == "scores":
            try:
                scores = json.loads(raw)
            except:
                st.error("⚠️ Invalid score JSON received.")

        # DONE
        elif event_type == "done":
            break

    # === FINAL SUMMARY ===
    if final_answer:
        st.subheader("Final Answer")
        st.markdown(final_answer)

    if scores:
        st.subheader("Scores")
        score_rows = [{"Model": k, "Score": v} for k, v in scores.items()]
        st.table(score_rows)

    st.success("Council complete!")
