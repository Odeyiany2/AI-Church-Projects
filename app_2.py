# Streamlit App Interface
import streamlit as st
import os
import base64
from main import azure_text_to_speech, extract_from_documents

# Function to generate a download link for the audio file
def generate_download_link(file_path):
    """Generate a download link for the audio file."""
    with open(file_path, "rb") as file:
        audio_bytes = file.read()
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="synthesized_audio.wav">Download Audio</a>'
    return href

st.title("📢 Victory House Announcement Assistant")

#sidebar for voice settings 
st.sidebar.subheader("Voice Settings")
voice_choice = st.sidebar.selectbox(
    "Choose Voice Type",
    ["en-NG-EzinneNeural (Female)", "(Male)"]
)

# Map user-friendly labels to Azure voice names
voice_mapping = {
    "en-NG-EzinneNeural (Female)": "en-NG-EzinneNeural",
    "en-NG-AbeoNeural (Male)": "en-NG-AbeoNeural"
}
selected_voice = voice_mapping[voice_choice]

#sidebar for inputs
with st.sidebar:
    option = st.selectbox(
        'What would you like to convert?',
        ('A text', 'A document'))

    # Text Input
    if option == "A text":
        st.subheader("Enter Text")
        text_input = st.text_area("Type your text here")
        if st.button('Convert Text to Speech'):
            if text_input.strip():
                with st.spinner(f"Synthesizing..."):
                    audio_file =  "text_speech_output" + ".wav"
                    #audio_file = os.path.join(SPEECH_OUTPUT_DIR, "text_speech_output.mp3")
                    output = azure_text_to_speech(text_input, selected_voice, output_file=audio_file)
                    if output:
                        st.session_state.audio_file = output
            else:
                st.warning("Please enter some text!")

    # File Upload
    elif option == "A document":
        st.subheader("Upload a Document")
        uploaded_file = st.file_uploader("Choose a file (.docx, .pdf, .txt)", type=["docx", "pdf", "txt"])
        if st.button("Convert Document to Speech"):
            if uploaded_file:
                with st.spinner(f"Synthesizing..."):
                    doc_text = extract_from_documents(uploaded_file)
                    if doc_text:
                        audio_file = f"{uploaded_file.name}_speech_output" + ".wav"
                        output = azure_text_to_speech(doc_text, selected_voice, output_file=audio_file)
                        if output:
                            st.session_state.audio_file = output
                        else:
                            st.error("Audio synthesis failed!")
                    else:
                        st.warning("No text found in the document!")
            else:
                st.warning("Please upload a document!")

# Display speech outputs if available
st.subheader("Speech Output Responses")
if 'audio_file' in st.session_state:
    audio_path = st.session_state.audio_file
    st.audio(audio_path, format="audio/wav")
    st.markdown(generate_download_link(audio_path), unsafe_allow_html=True)