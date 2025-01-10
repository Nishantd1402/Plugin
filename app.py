import os
from flask import Flask, request, jsonify, render_template, redirect, url_for , Response
from flask_cors import CORS
import openai
import librosa
from pydub import AudioSegment
from groq import Groq
import json
import re
import numpy as np

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './uploads'

def get_completion( prompt):
    try:
            client = Groq(api_key="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")
            # Generate the completion using the OpenAI client
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.1  # Adjust randomness
            )
            response = chat_completion.choices[0].message.content
            return response
    except Exception as e:
        return "An error occurred while generating the response."

def convert_to_wav(audio_file):
    sound = AudioSegment.from_file(audio_file)
    wav_file = os.path.join(app.config['UPLOAD_FOLDER'], "processed_audio.wav")
    sound.export(wav_file, format="wav")
    return wav_file

def transcribe_audio(filename, model="distil-whisper-large-v3-en", prompt=None, language="en", temperature=0.1):
    client = Groq(api_key="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")

    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model=model,
            prompt="An audio sample for reviewing the technical skill of an Indian person.",
            response_format="verbose_json",
            language=language,
            temperature=temperature,
        )
    return transcription

def get_next_question(transcribed_text , prev_question):
    prompt = f"""
    Based on the user's response to the previous question in this AI/ML interview, generate a new follow-up question that shifts focus to a different yet relevant topic within the field. The next question should not repeat or overly revolve around the previous discussion but instead explore a fresh area that tests the candidate's breadth of knowledge in AI/ML. Ensure the question is challenging and opens up a different aspect of AI/ML, moving the conversation in a new direction while still maintaining relevance to the overall interview.
    Transcribed Text: "{transcribed_text}"
    Previous Question: "{prev_question}"
    Just give the next question without any other text
"""
    return get_completion(prompt)

def convert_webm_to_mp3(input_path):
    try:
        # Load the .webm file (requires FFmpeg installed)
        audio = AudioSegment.from_file(input_path, format="webm")
        
        # Export the audio as MP3
        return audio.export(input_path, format="mp3")
    except Exception as e:
        print(f"Error during conversion: {e}")


# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/FirstQuestion' , methods=['POST' , 'GET'])
def first_question():
    domain = request.form.get("domain" , "")
    print(domain)
    num = np.random.randint(0,9)
    with open('firstQuestion.json', 'r') as file:
        data = json.load(file)
    
    question = data[domain][num]
    print(get_next_question("i dont know" , "How do you think the concept of explainability in machine learning models can be balanced with the need for model complexity and accuracy, especially in high-stakes applications such as healthcare or finance?"))
    return jsonify(question)

# Route: Analyze Speech
@app.route('/analyze', methods=['POST' , 'GET'])
def analyze_speech():
    if request.method == 'GET':
        return "Please use the POST method to send data"
    if 'audio' not in request.files:
        return "No File attached"

    audio_file = request.files['audio']
    prev_question = request.form.get("previous","")
    # Save audio locally
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    audio_file.save(audio_path)

   
    # Convert to WAV
    wav_file = convert_to_wav(audio_path)

    # Step 1: Transcribe audio
    transcription = transcribe_audio(audio_path)
      # Ensure transcription is a dictionary
    next_question = get_next_question(transcription , prev_question)
    results = compute_results()
    return jsonify(next_question)

def compute_results():
    return 4

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
