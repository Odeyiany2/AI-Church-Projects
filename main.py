import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from docx import Document
import os 
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

#function to extract content from docx files
def extract_from_documents(files):
    """Extract text from a  files."""
    for file in files:
        filename = secure_filename(file.name)
        base, ext = os.path.splitext(filename)
        ext = ext.lower() 
        try:
            if ext == ".docx":
                doc = Document(file)
                text = []
                for paragraph in doc.paragraphs:
                    text.append(paragraph.text)
                return "\n".join(text)
            elif ext == ".pdf":
                pdf_reader = PdfReader(file)
                text = [page.extract_text() for page in pdf_reader.pages]
                return "\n".join(text)
            elif ext == ".txt":
                text = file.read().decode("utf-8")  # Streamlit's file_uploader returns a binary stream
                return text
        except Exception as e:
            st.error(f"Error reading document: {e}")
            return None
        

#function to convert text to speech
def azure_text_to_speech(text):
    """Convert text to speech using Azure Cognitive Services."""
    try: 
        SPEECH_REGION = os.getenv("REGION")
        SPEECH_KEY = os.getenv("API_KEY")
        # Configure Azure Speech SDK
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        speech_config.speech_synthesis_voice_name = "en-NG-EzinneNeural"  

        # Stream audio output directly to the user
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # Synthesize the speech
        st.info("Reading the content aloud...")
        result = synthesizer.speak_text_async(text).get()

        # Check for errors
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            st.success("Speech synthesis completed successfully!")
        else:
            st.error(f"Speech synthesis failed. Reason: {result.reason}")
    except Exception as e:
        st.error(f"Error converting to audio: {e}")
        return None


