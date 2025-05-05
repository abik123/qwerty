import streamlit as st
import asyncio
import os
import yt_dlp
import nest_asyncio
from deepgram import Deepgram

# Fix event loop (just like Colab)
nest_asyncio.apply()

# Streamlit config
st.set_page_config(page_title="🎙️ Video-to-Text")
st.title("🎧 Video Transcript Generator")
st.markdown("Paste a TikTok or YouTube video link to transcribe its speech ➡️ powered by Deepgram!")

# Load Deepgram API key (from secrets.toml in Streamlit Cloud)
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# Input field
video_url = st.text_input("🔗 Enter Video URL here:")

if st.button("🎬 Transcribe Now") and video_url:

    with st.spinner("⏳ Downloading audio... please wait"):
        try:
            # Step 1: Download audio
            def download_audio(video_url):
                output_path = "/tmp/audio"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'ffmpeg_location': '/usr/bin',
                    'outtmpl': output_path + '.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                    }]
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                return output_path + '.mp3'

            mp3_path = download_audio(video_url)

            # Step 2: Transcribe using Deepgram (async)
            async def transcribe(mp3_path):
                dg = Deepgram(DEEPGRAM_API_KEY)
                with open(mp3_path, 'rb') as f:
                    source = {
                        'buffer': f,
                        'mimetype': 'audio/mp3'
                    }
                    response = await dg.transcription.prerecorded(source, {
                        'punctuate': True,
                        'smart_format': True,
                        'filler_words': True
                    })

                result = response["results"]["channels"][0]["alternatives"][0]["transcript"]
                return result

            transcript = asyncio.run(transcribe(mp3_path))

            # Step 3: Show results
            st.success("✅ Transcript ready!")
            st.text_area("📝 Transcript Output", transcript, height=300)

        except Exception as e:
            st.error(f"Something went wrong 🤕\n{e}")
