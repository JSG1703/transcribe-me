import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from fpdf import FPDF
import textstat
from spellchecker import SpellChecker
import io

def identify_misspelled_words(sentence):
    """
    Identifies misspelled words in the given sentence.

    :param sentence: The sentence to be analyzed.
    :return: A set of misspelled words.
    """
    spell = SpellChecker()
    words = sentence.split()
    misspelled = spell.unknown(words)
    return misspelled

def convert_audio_to_wav(audio_file):
    audio = AudioSegment.from_file(audio_file)
    wav_file = audio_file.name.split(".")[0] + ".wav"
    audio.export(wav_file, format="wav")
    return wav_file

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError as e:
            return f"Error: {str(e)}"


def analyze_complexity(text):

    if not isinstance(text, str):
        return "Input to analyze_complexity must be a string."

    readability_score = textstat.flesch_reading_ease(text)
    return readability_score


def export_to_pdf(text):
    if not isinstance(text, str):
        text = str(text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)

    pdf_buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    return pdf_buffer

def main():
    st.title("Speech-to-Text Converter with Grammar Check")
    st.write("Upload an audio file to convert it to text.")

    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3"])

    if uploaded_file is not None:
        file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type}
        st.write(file_details)

        if uploaded_file.type == "audio/mp3":
            uploaded_file = convert_audio_to_wav(uploaded_file)

        text = speech_to_text(uploaded_file)
        st.write("**Original Text:**")
        st.write(text)

        # Correct grammatical errors
        corrected_text = identify_misspelled_words(text)
        st.write("**Incorrectly Spelled Words:**")
        st.write(corrected_text)

        # Analyze text complexity
        complexity_score = analyze_complexity(text)
        st.write(f"**Readability Score:** {complexity_score}")

        # Export to PDF
        pdf_buffer = export_to_pdf(corrected_text)

        # Add a download button
        if st.button("Generate PDF"):
            pdf_buffer = export_to_pdf(text)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="output.pdf",
                mime="application/pdf"
        )
if __name__ == "__main__":
    main()
