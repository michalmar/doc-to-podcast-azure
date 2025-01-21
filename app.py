# filename: app.py

import streamlit as st
import os
# import fitz  # PyMuPDF
import time
# from gtts import gTTS

from doctopodcast import GeneratePodcastFromUrl


# Set the title of the Streamlit app
st.title("Podcast Generator")

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

def callback(text = "Processing...", empty=st.empty()):
        empty.caption(text)

# Check if a file has been uploaded
if uploaded_file is not None:
    with st.spinner('Generating podcast from the file - it might take a while...'):
        # Save the uploaded PDF to the file system
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        pdf_path = os.path.join("tmp", uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Indicate processing progress
        empty = st.empty()
        wav_path = GeneratePodcastFromUrl(uploaded_file.name, callback=lambda status: callback(status, empty=empty))

        st.success(f"File processed. WAV saved to {wav_path}")

        if wav_path is not None:
            # Display the MP3 for playback
            st.audio(wav_path)
        else:
            st.error("Failed to generate podcast from file 😢")