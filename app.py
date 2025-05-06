import streamlit as st
import asyncio
import nest_asyncio
from deepgram import Deepgram

nest_asyncio.apply()

st.set_page_config(page_title="Audio-to-Text 🎧")
st.title("📝 Upload & Transcribe Audio")
st.markdown("Upload an `.mp3`, `.wav`, or `.m4a` file below. We'll transcribe the speech using Deepgram AI.")

API_KEY = st.secrets["DEEPGRAM_API_KEY"]

uploaded_file = st.file_uploader("📁 Upload Audio File:", type=["mp3", "wav", "m4a"])
go = st.button("Transcribe 🔍")

if uploaded_file:
    st.audio(uploaded_file, format=uploaded_file.type)
    st.caption("🎧 Click play to preview the uploaded file.")

async def transcribe_audio(file_data, mimetype):
    dg = Deepgram(API_KEY)
    source = {'buffer': file_data, 'mimetype': mimetype}
    response = await dg.transcription.prerecorded(source, {
        "punctuate": True,
        "smart_format": True
    })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

if go and uploaded_file:
    with st.spinner("⏳ Transcribing..."):
        try:
            mimetype = uploaded_file.type
            transcript = asyncio.run(transcribe_audio(uploaded_file, mimetype))
            st.success("✅ Transcription complete!")
            st.text_area("📄 Transcript:", transcript, height=300)
        except Exception as e:
            st.error(f"🚨 Error: {e}")
