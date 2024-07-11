from flask import Flask, request, render_template, send_file
import fitz  # PyMuPDF
from google.cloud import texttospeech
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


# Inizializza il client di Google Text-to-Speech
# client = texttospeech.TextToSpeechClient()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return 'No file part'
        file = request.files['pdf']
        if file.filename == '':
            return 'No selected file'
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            audio_filepath = convert_text_to_speech(text, file.filename)
            return send_file(audio_filepath, as_attachment=True)
    return render_template('index.html')

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def convert_text_to_speech(text, filename):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    audio_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.mp3")
    with open(audio_filepath, "wb") as out:
        out.write(response.audio_content)
    return audio_filepath

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
