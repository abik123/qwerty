import streamlit as st
import asyncio
import nest_asyncio
from deepgram import Deepgram

# Allow nested async loops (for Streamlit)
nest_asyncio.apply()

# App UI setup
st.set_page_config(page_title="Audio-to-Text 🎧")
st.title("📝 Upload & Transcribe Audio")
st.markdown("Upload an `.mp3`, `.wav`, or `.m4a` file and we'll transcribe it using Deepgram AI.")

# Load your Deepgram API Key securely from Streamlit secrets
API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# Step 1: Upload audio file
uploaded_file = st.file_uploader("📁 Upload your audio file", type=["mp3", "wav", "m4a"])
go = st.button("Transcribe 🔍")

# Step 2: Preview the uploaded audio
if uploaded_file:
    try:
        audio_ext = uploaded_file.type.split('/')[-1]  # e.g., "mp3"
        audio_format = f"audio/{audio_ext}"
        st.audio(uploaded_file, format=audio_format)
        st.caption("🎧 Click play to preview your uploaded audio.")
    except Exception as preview_error:
        st.warning(f"⚠️ Could not preview audio: {preview_error}")

# Step 3: Deepgram transcription logic
async def transcribe(buffer, mimetype):
    dg = Deepgram(API_KEY)
    source = {'buffer': buffer, 'mimetype': mimetype}

    response = await dg.transcription.prerecorded(source, {
        'punctuate': True,
        'smart_format': True,
    })

    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# Step 4: Trigger transcription after button press
if go and uploaded_file:
    with st.spinner("🧠 Transcribing with Deepgram... Please wait."):
        try:
            mime = f"audio/{uploaded_file.type.split('/')[-1]}"
            transcript = asyncio.run(transcribe(uploaded_file, mime))

            # Display result
            st.success("✅ Transcription complete!")
            st.text_area("📜 Transcript Output", transcript, height=300)

        except Exception as e:
            st.error(f"🚨 Something went wrong: {e}")
