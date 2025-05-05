import streamlit as st
import yt_dlp
import asyncio
import nest_asyncio
from deepgram import Deepgram
import os
os.environ['PATH'] += os.pathsep + '/usr/bin'

nest_asyncio.apply()

# 👋 Title Area
st.set_page_config(page_title="🎤 Video Transcriber")
st.title("🎙 Simple Video-to-Text App")
st.info("Paste a video link (TikTok, YouTube, etc.) and get the transcript below.")

# 🔐 API Key - pulled securely from Streamlit secrets
API_KEY = st.secrets["DEEPGRAM_API_KEY"]

# 📥 User Input
video_input = st.text_input("🎬 Paste video URL here:")
go_button = st.button("Run Transcription ▶️")

# 🎧 Download and process video
def handle_media(url):
    temp_path = "/tmp/audio"
    ffmpeg_binary = '/usr/bin/ffmpeg'
    ffprobe_binary = '/usr/bin/ffprobe'

    options = {
        'format': 'bestaudio/best',
        'ffmpeg_location': ffmpeg_binary,
        'postprocessor_args': [
        '-loglevel', 'panic'
        ],
        'outtmpl': temp_path + '.%(ext)s',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])
    return temp_path + '.mp3'

# 🎙 Transcribe Function
async def run_ai(audio_path):
    dg = Deepgram(API_KEY)
    with open(audio_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/mp3'}
        response = await dg.transcription.prerecorded(source, {'punctuate': True})
    return response["results"]["channels"][0]["alternatives"][0]["transcript"]

# 🧠 Trigger on button click
if go_button and video_input:
    with st.spinner("Transcribing... Hold on ⏳"):
        try:
            audio = handle_media(video_input)
            text = asyncio.run(run_ai(audio))
            st.success("✅ Done!")
            st.text_area("📜 Transcript:", text, height=300)
        except Exception as err:
            st.error(f"Something broke 🧨: {err}")
