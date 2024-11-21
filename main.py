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
def azure_text_to_speech(text, selected_voice, output_file="output.wav", verbose = False):
    """Convert text to speech using Azure Cognitive Services."""
    path = "speech_outputs"
    os.makedirs(path, exist_ok=True)
    output_file = os.path.join(path, output_file)

    output = open(output_file, 'w+')
    output.close()
    
    try: 
        path = "speech_outputs"
        os.makedirs(path, exist_ok=True)
        output_file = os.path.join(path, output_file)

        output = open(output_file, 'w+')
        output.close()

        SPEECH_REGION = os.getenv("REGION")
        SPEECH_KEY = os.getenv("API_KEY")
        # Configure Azure Speech SDK
        speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)

        #configuring for the voice selected by users
        if selected_voice == "Both":
            # Use SSML for alternating voices
            text_segments = text.split(".")  # Split text by sentences
            ssml_string = generate_ssml(text_segments)
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_ssml_async(ssml_string).get()
        
        else:
            # Single voice (male or female)
                    # Create SSML string for smoother speech
            ssml_string = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-NG">
                <voice name="{selected_voice}">
                    <prosody rate="0%" pitch="0%">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            speech_config.speech_synthesis_voice_name = selected_voice
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_ssml_async(ssml_string).get()
        
        # Handle the result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            if verbose:
                print(f"Speech synthesized successfully. Saved to {output_file}")
                st.audio(output_file, format="audio/wav")
            return output_file 
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            error_message = f"Speech synthesis canceled: {cancellation_details.reason}"
            if verbose:
                print(error_message)
            
            if cancellation_details.reason == speechsdk.CancellationReason.Error and cancellation_details.error_details:
                error_message += f" Error details: {cancellation_details.error_details}."
                if verbose:
                    print("Did you set the speech resource key and region values?")
            
            return None
    
    except Exception as e:
        error_message = f"An error occurred during speech synthesis: {str(e)}"
        if verbose:
            print(error_message)
        return None

def generate_ssml(text_segments):
    """Generate SSML string with alternating voices."""
    ssml_parts = []
    voices = ["en-NG-EzinneNeural", "en-NG-AbeoNeural"]  # Female and Male voices
    for i, segment in enumerate(text_segments):
        voice = voices[i % len(voices)]  # Alternate between voices
        ssml_parts.append(f'<voice name="{voice}">{segment.strip()}.</voice>')
    return f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-NG">{" ".join(ssml_parts)}</speak>'


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


# #speech_config.speech_synthesis_voice_name = "en-NG-AbeoNeural" 

        # # Create SSML string for smoother speech
        # ssml_string = f"""
        # <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-NG">
        #     <voice name="en-NG-EzinneNeural">
        #         <prosody rate="0.001%" pitch="0.001%">
        #             {text}
        #         </prosody>
        #     </voice>
        # </speak>
        # """ 

        # # Stream audio output directly to the user
        # audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        # synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        # # Synthesize the speech
        # #st.info("Reading the content aloud...")
        # result = synthesizer.speak_ssml_async(ssml_string).get()
