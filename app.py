import streamlit as st
import asyncio
import nest_asyncio
from deepgram import Deepgram
import yt_dlp
import os

nest_asyncio.apply()

# Setup
st.set_page_config(page_title="🎧 Audio & Video Transcriber")
st.title("📝 Audio/Video-to-Text Transcriber")
st.markdown("Upload an audio file **OR** paste a YouTube/TikTok video link for automatic transcription via Deepgram AI.")

API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# Layout
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📁 Upload Audio File", type=["mp3", "m4a", "wav"])
with col2:
    video_url = st.text_input("🔗 OR Paste Video URL (TikTok/YouTube)")

go = st.button("Transcribe Now 🔍")

# Function: Transcribe using Deepgram
async def transcribe(buffer, mimetype):
    dg = Deepgram(API_KEY)
    source = {'buffer': buffer, 'mimetype': mimetype}
    response = await dg.transcription.prerecorded(source, {
        'punctuate': True,
        'smart_format': True,
        'filler_words': True
    })
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# Function: Download + Convert video to MP3 (using your Colab/PDF logic!)
def download_audio_from_url(video_url):
    base_path = "/tmp/audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': '/usr/bin',  # Stays here just in case local test uses ffmpeg
        'outtmpl': base_path + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    mp3_path = base_path + '.mp3'
    return mp3_path

# Execute after clicking "Transcribe Now"
if go:
    with st.spinner("Processing and transcribing... please wait ⏳"):

        # ============================ FILE UPLOAD ============================ #
        if uploaded_file:
            try:
                filetype = uploaded_file.type.split('/')[-1]
                st.audio(uploaded_file, format=f"audio/{filetype}")
                transcript = asyncio.run(transcribe(uploaded_file, f'audio/{filetype}'))
                st.success("✅ Upload transcription complete!")
                st.text_area("📜 Transcript:", transcript, height=300)
            except Exception as e:
                st.error(f"⚠️ Error with uploaded file: {e}")

        # ============================ VIDEO LINK ============================ #
        elif video_url:
            try:
                mp3_path = download_audio_from_url(video_url)
                with open(mp3_path, 'rb') as audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    transcript = asyncio.run(transcribe(audio_file, "audio/mp3"))
                    st.success("✅ Video link transcription complete!")
                    st.text_area("📜 Transcript:", transcript, height=300)
            except Exception as e:
                st.error(f"⚠️ Error with video link: {e}")

        else:
            st.warning("😅 Please upload a file OR paste a video link to start.")

