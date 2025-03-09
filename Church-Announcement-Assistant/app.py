# Streamlit App Interface
import streamlit as st
import os
import base64
from main import azure_text_to_speech, extract_from_documents

st.title("📢 Victory House Announcement Assistant")
#st.write("Upload a document (.docx, .pdf, .txt) or type text to hear it read aloud.")
# Directory to store synthesized audio
SPEECH_OUTPUT_DIR = "speech_outputs"
os.makedirs(SPEECH_OUTPUT_DIR, exist_ok=True)

# Function to generate a download link for the audio file
def generate_download_link(file_path):
    """Generate a download link for the audio file."""
    with open(file_path, "rb") as file:
        audio_bytes = file.read()
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="synthesized_audio.mp4">Download Audio</a>'
    return href
    

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
                    audio_file = os.path.join(SPEECH_OUTPUT_DIR, "text_speech_output.mp4")
                    output = azure_text_to_speech(text_input, output_file=audio_file)
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
                        audio_file = os.path.join(SPEECH_OUTPUT_DIR, f"{uploaded_file.name}_speech_output.mp4")
                        output = azure_text_to_speech(doc_text, output_file=audio_file)
                        if output:
                            st.session_state.audio_file = output  # Save the file path for future use
                        else:
                            st.error("Audio synthesis failed!")
                    else:
                        st.warning("No text found in the document!")
            else:
                st.warning("Please upload a document!")
    

# Display speech outputs if available
st.subheader("Speech Output Responses")
if os.listdir(SPEECH_OUTPUT_DIR):
    for audio in os.listdir(SPEECH_OUTPUT_DIR):
        audio_path = os.path.join(SPEECH_OUTPUT_DIR, audio)
        st.audio(audio_path, format="audio/mp4", start_time=0)
        st.markdown(generate_download_link(audio_path), unsafe_allow_html=True)

# if 'audio_file' in st.session_state:
#         st.subheader("Speech Output")
#         for speech_output in st.session_state.speech_outputs:
#             st.audio(os.path.join('speech_outputs', speech_output), format="audio/mp4", start_time=0)
#             st.markdown(generate_download_link(st.session_state.audio_file), unsafe_allow_html=True)
    
#     # st.subheader("Speech output responses")
#     # if 'speech_outputs' in st.session_state:
    #     for speech_output in st.session_state.speech_outputs:
    #         st.audio(os.path.join('speech_outputs', speech_output), format="audio/mp4", start_time=0)



































st.divider()
st.markdown("##### Built by Miriam Odeyiany [Victory House Annoucement Assistant](https://github.com/Odeyiany2/Church-Announcement--Assistant) repository")
st.write("Copyright © Miriam Odeyiany, Victory House 2024")

# if __name__ == "__main__":
#     main()
