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

# 🎧 OPTIONAL: Preview uploaded audio
if uploaded_file:
    st.audio(uploaded_file, format=f"audio/{uploaded_file.type.split('/')[-1]}")
    st.caption("▶️ Click play to preview your uploaded audio.")

# 🧠 Transcribe logic
async def transcribe(buffer, mimetype):
    dg = Deepgram(API_KEY)
    source = {'buffer': buffer, 'mimetype': mimetype}
    response = await dg.transcription.prerecorded(source, {
        'punctuate': True,
        'smart_format': True,
    })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# 🚀 On Click
if go and uploaded_file:
    mime = f"audio/{uploaded_file.type.split('/')[-1]}"
    with st.spinner("Transcribing... ⏳"):
        try:
            transcript = asyncio.run(transcribe(upload
