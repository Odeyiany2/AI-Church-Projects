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
def azure_text_to_speech(text, output_file="output.mp4", verbose = False):
    """Convert text to speech using Azure Cognitive Services."""
    # path = "speech_outputs"
    # os.makedirs(path, exist_ok=True)
    # output_file = os.path.join(path, output_file)

    output = open(output_file, 'w+')
    output.close()
    
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
        #st.info("Reading the content aloud...")
        result = synthesizer.speak_text_async(text).get()

        # Handle the result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            if verbose:
                print(f"Speech synthesized successfully for text: {text}")
            return True, "Speech synthesis completed successfully."
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Speech synthesis canceled: {cancellation_details.reason}"
            if verbose:
                print(error_message)
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error and cancellation_details.error_details:
                error_message += f" Error details: {cancellation_details.error_details}."
                if verbose:
                    print("Did you set the speech resource key and region values?")
            
            return False, error_message
    
    except Exception as e:
        error_message = f"An error occurred during speech synthesis: {str(e)}"
        if verbose:
            print(error_message)
        return False


def main():
    # Example usage
    try:
        # Transcribe audio
        #transcription = transcribe_audio("audio.wav")
        #print(f"Transcription: {transcription}")
        
        # Synthesize speech with verbose output
        sample_text = "I love the AI Hacktoberfest challenge by MLSA Nigeria!"
        success, message = azure_text_to_speech(sample_text, verbose=True)
        print(message)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
