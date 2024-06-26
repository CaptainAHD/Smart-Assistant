import streamlit as st
from openai import OpenAI
import streamlit as st
import os
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore
from openai import OpenAI
import json
from google.cloud import texttospeech
from langdetect import detect
import base64
import requests
from google.oauth2 import service_account
from deep_translator import GoogleTranslator
from deepgram import (DeepgramClient, PrerecordedOptions,FileSource,)

st.set_page_config(layout="wide")

st.title('Smart Field Assistant')
client = OpenAI()
def stt(file_path):
  try:
    audio_file = open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file, 
      response_format="text"
        )

    return transcription

  except Exception as e:
    return f"Exception: {e}"

audio_file = st.file_uploader("Upload an audio file", type=["mp3"])
def save_uploaded_file(uploaded_file):
  with open("temp_audio.mp3", "wb") as f:
    f.write(uploaded_file.getbuffer())
  return "temp_audio.mp3"


if audio_file is not None:
  st.audio(audio_file, format="mp3")
    # Save uploaded audio file
  file_path = save_uploaded_file(audio_file)
    # Transcribe audio and update query input field
  st.write("Transcribing audio...")
  notes = stt(file_path)
  st.write(notes)


response = client.chat.completions.create(
  model="gpt-4-1106-preview", 
  messages=[{
                    "role": "system",
                    "content": f"""Act as Dr. Frida L. Friedman, a report writer who uses a bunch of audio notes transcription and field notes to write detailed reports. These reports are of a very high quality and are cited by academics, think tanks, and even governments.Now I will be giving you a bunch of audio notes transcription and field notes to make detailed reports out of. But remember these points when analyzing the notes:

                                  First, audio notes transcription and field notes work as descriptions: you write them as notes and details of time, date, activities, settings, observations, behavior and conversations in the field. According to Thomas Schwandt, descriptive information is your “attempt to accurately document factual data [e.g., date and time] and the settings, actions, behaviors, and conversations that you observe.”

                                  Second, these will help you with interpretations. Based on the noted explain what you observed and ruminate on why your observations are relevant and important. Answer the “so-what” question as well.""",
                                                  },
                {
                    "role": "user",
                    "content": f"""Hello, Dr. Friedman, use your expertise to write a detailed report using the following notes:

                                    {notes}

                                    When writing take your time, contextualize it well, it. Think step-by-step in the following XML tags before you start writing:

                                    <thinking>
                                    </thinking>
                                    Give the report in the following XML tags, use relevant markdown tags for headings:
                                    <report>
                                    </report>

                                    NOTE: You must only use the XML tags I have asked you to, do not use any additional ones. Also, do not put any content outside XML tags."""


                },
            ],)

def extract_report_from_variable(content):
    start_tag = '<report>'
    end_tag = '</report>'
    start_index = content.find(start_tag)
    end_index = content.find(end_tag)

    if start_index != -1 and end_index != -1:
        report_content = content[start_index + len(start_tag):end_index]
        return report_content
    else:
        return "Report tags not found."

extracted_report = extract_report_from_variable(response.choices[0].message.content)
st.write(extracted_report)

