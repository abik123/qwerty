import streamlit as st
import asyncio
import os
import yt_dlp
import nest_asyncio
from deepgram import Deepgram
from pydub import AudioSegment

nest_asyncio.apply()
st.set_page_config(page_title="🔈 Video to Transcript")
st.title("🎙️ Video-to-Text Transcriber")
st.markdown("Paste a video link – we'll extract the audio, transcribe it using Deepgram, and display it right here!")

API_KEY = st.secrets["DEEPGRAM_API_KEY"]

video_url = st.text_input("🔗 Paste Video URL:")
go = st.button("Transcribe ▶️")

def download_video(url):
    output_path = "/tmp/video"
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path + '.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.download([url])
    return output_path + '.mp4'

def convert_to_mp3(mp4_path):
    mp3_path = "/tmp/converted.mp3"
    video_audio = AudioSegment.from_file(mp4_path)
    video_audio.export(mp3_path, format="mp3")
    return mp3_path

async def transcribe(mp3_path):
    dg = Deepgram(API_KEY)
    with open(mp3_path, 'rb') as f:
        source = {'buffer': f, 'mimetype': 'audio/mp3'}
        res = await dg.transcription.prerecorded(source, {
            'punctuate': True,
            'smart_format': True,
        })
    return res["results"]["channels"][0]["alternatives"][0]["transcript"]

if go and video_url:
    with st.spinner("Processing... ⏳"):
        try:
            mp4 = download_video(video_url)
            mp3 = convert_to_mp3(mp4)
            transcript = asyncio.run(transcribe(mp3))
            st.success("✅ Transcript Complete!")
            st.text_area("📄 Transcript:", transcript, height=300)
        except Exception as e:
            st.error(f"Something went boom 💥: `{str(e)}`")
