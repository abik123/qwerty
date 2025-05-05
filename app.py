import streamlit as st
import asyncio
import nest_asyncio
from deepgram import Deepgram

nest_asyncio.apply()

st.set_page_config(page_title="Audio-to-Text 🎧")
st.title("📝 Upload & Transcribe Audio")
st.markdown("Upload an `.mp3`, `.wav`, or `.m4a` file to auto-transcribe speech using Deepgram.")

API_KEY = st.secrets["DEEPGRAM_API_KEY"]

uploaded_file = st.file_uploader("📁 Upload Audio File:", type=["mp3", "wav", "m4a"])
go = st.button("Transcribe 🔍")

async def transcribe(buffer, mimetype):
    dg = Deepgram(API_KEY)
    source = {'buffer': buffer, 'mimetype': mimetype}
    response = await dg.transcription.prerecorded(source, {
        'punctuate': True,
        'smart_format': True,
    })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

if go and uploaded_file:
    mime = f"audio/{uploaded_file.type.split('/')[-1]}"
    with st.spinner("Transcribing... ⏳"):
        try:
            transcript = asyncio.run(transcribe(uploaded_file, mime))
            st.success("✅ Transcription Complete!")
            st.text_area("👂 Detected Speech", transcript, height=300)
        except Exception as e:
            st.error(f"🚨 Error: {e}")
