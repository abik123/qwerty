import streamlit as st
import asyncio
import nest_asyncio
import os
from deepgram import Deepgram
import yt_dlp
from pydub import AudioSegment

nest_asyncio.apply()

# UI Settings
st.set_page_config(page_title="🎧 Audio & Video Transcriber")
st.title("📝 Upload OR Paste Video Link to Transcribe")
st.markdown("Upload an audio file **or** paste a video URL (TikTok, YouTube, etc). We'll extract the audio, transcribe it using Deepgram, and show you the text.")

# Load Deepgram API key securely
DG_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# Inputs
col1, col2 = st.columns(2)
with col1:
    uploaded_audio = st.file_uploader("📁 Upload Audio File:", type=["mp3", "m4a", "wav"])
with col2:
    video_link = st.text_input("🔗 OR Paste a Video URL:")

go = st.button("Transcribe Now 🔍")

# 🔁 Deepgram transcription logic
async def transcribe_audio(file_data, mimetype):
    dg = Deepgram(DG_API_KEY)
    source = {'buffer': file_data, 'mimetype': mimetype}
    response = await dg.transcription.prerecorded(source, {
        "punctuate": True,
        "smart_format": True
    })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# ⬇️ Download + convert video (PDF logic, Streamlit-safe)
def extract_audio_from_url(url):
    output_video = "/tmp/video.mp4"
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_video
    }

    # Download video using yt_dlp (no ffmpeg postprocessor!)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Convert using pydub instead of ffmpeg CLI
    audio = AudioSegment.from_file(output_video)
    mp3_path = "/tmp/audio.mp3"
    audio.export(mp3_path, format="mp3")
    return mp3_path

# 🔥 ACTUAL FLOW
if go:
    with st.spinner("⏳ Working..."):

        try:
            if uploaded_audio:
                # Handle audio upload
                filetype = uploaded_audio.type.split("/")[-1]
                st.audio(uploaded_audio, format=uploaded_audio.type)
                transcribed = asyncio.run(transcribe_audio(uploaded_audio, uploaded_audio.type))
                st.success("✅ Upload transcription complete!")
                st.text_area("📜 Transcript:", transcribed, height=300)

            elif video_link:
                # Handle video link flow
                mp3_path = extract_audio_from_url(video_link)
                with open(mp3_path, 'rb') as f:
                    st.audio(f, format="audio/mp3")
                    transcribed = asyncio.run(transcribe_audio(f, "audio/mp3"))
                    st.success("✅ Video link transcription complete!")
                    st.text_area("📜 Transcript:", transcribed, height=300)

            else:
                st.warning("⚠️ Please either upload an audio file or paste a video URL.")

        except Exception as e:
            st.error(f"🚨 Something went wrong: {e}")
