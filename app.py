import os
from flask import Flask, request, jsonify, render_template, redirect, url_for , Response
from flask_cors import CORS
import openai
import librosa
from pydub import AudioSegment
from groq import Groq
import threading
import json
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './uploads'

# Configure OpenAI with Azure
openai.api_type = "azure"
openai.api_key = "3b71db40640d499bb8a337e63009e367"
openai.api_base = "https://imopenaiswedencentral.openai.azure.com/"
openai.api_version = "2023-10-01-preview"

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
        # Handle exceptions and return an error message
        return "An error occurred while generating the response."
'''
# Function to interact with Azure OpenAI
def get_completion(prompt, engine="GPT432KTechnicalCheck"):
    response = openai.ChatCompletion.create(
        engine=engine,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4  # Adjust randomness
    )
    return response['choices'][0]['message']['content']'''

# Function: Convert audio to WAV format
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
            prompt="An audio sample for reviewing the communication skill of an Indian person.",
            response_format="verbose_json",
            language=language,
            temperature=temperature,
        )
    return transcription
def extract_score(text , kind):
    if kind == 'grammer':
        # Regular expression to find a score in the format "X out of Y"
        match = re.search(r'(\d+)\s*out\s*of\s*\d+', text)
        if match:
            return int(match.group(1))  # Extract and return the score as an integer
        return None  # Return None if no score is found
    if kind == 'pronunciation':
        try:
            return int(text.split("Score:")[1].split()[0])
        except (IndexError, ValueError):
            return None  # Return None if the extraction fails

# Function: Grammar Analysis
def grammar_analysis(text , prompt = None):
    prompt = f"""
    You are given a text transcription from an audio file of an indian student.
    Analyze the text for grammar mistakes to help the user in enhancing their communication skill.Keep it consizeda and Highlight errors and provide corrections:
    "{text}".
    Start with only a score between 0-10. and all remarks in next sentences.
    """
    return get_completion(prompt)

# Function: Pronunciation Assessment
def pronunciation_assessment(expected_text, transcribed_text):
    prompt = f"""
    Evaluate the pronunciation clarity based on the following:
    Expected Text: "{expected_text}"
    Transcribed Text: "{transcribed_text}"
    Also analyze the wrongly pronounced words.
    Provide a score out of 10 for clarity and suggestions for improvement.
    Start with only a score between 0-10. and all remarks in next sentences.
    """
    return get_completion(prompt)

# Function: Fluency Analysis
def fluency_analysis(audio_file, transcribed_text):
    y, sr = librosa.load(audio_file, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)

    word_count = len(transcribed_text.split())
    speaking_rate = word_count / (duration / 60)  # Words per minute

    fillers = ["uh", "um"]
    filler_count = sum(transcribed_text.lower().count(fw) for fw in fillers)

    fluency_data = {
        "duration": duration,
        "speaking_rate_wpm": speaking_rate,
        "filler_count": filler_count
    }

    return fluency_data

# Function: Generate Report
def generate_report(transcription, grammar_feedback, pronunciation_feedback, fluency_data):
    return {
        "transcription": transcription,
        "grammar_feedback": grammar_feedback,
        "pronunciation_feedback": pronunciation_feedback,
        "fluency_data": fluency_data
    }
def extract_json_from_backticks(text):
    print(text)
    # Regex to capture content between triple backticks
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    result = jsonify(json.loads(matches[0]))


    return result

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

@app.route('/prompts' , methods=['POST' , 'GET'])
def get_prompt():
    
    topics = request.form.get("topics", "")
    prompt = f"""
    This are some topics chosen by the user - {topics}. Give 20 generated test paragraphs for communication assesment for 20 levels. 5 at easy level, 10 as medium and 5 as hard.
    The level should grow hard on the basis of word selection, grammer used and comprehensiveness.
    Provide the response in JSON format.
"""

    return extract_json_from_backticks(get_completion(prompt = prompt))

# Route: Analyze Speech
@app.route('/analyze', methods=['POST' , 'GET'])
def analyze_speech():
    if request.method == 'GET':
        return "Please use the POST method to send data"
    if 'audio' not in request.files:
        return "No File attached"

    audio_file = request.files['audio']
    expected_text = request.form.get("expected_text", "")

    # Save audio locally
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    audio_file.save(audio_path)

    mp3_file = convert_webm_to_mp3(audio_path)
    # Convert to WAV
    wav_file = convert_to_wav(mp3_file)

    # Step 1: Transcribe audio
    transcription = transcribe_audio(audio_path)
      # Ensure transcription is a dictionary
    
    # Analyze each segment
    def analyze_segment(segment, results):
        text = segment['text']
        feedback = grammar_analysis(text)
        score = extract_score(feedback , kind='grammer')
        results['grammar'] = [score , feedback]
        feedback = pronunciation_assessment(expected_text, text)
        score = extract_score(feedback , kind='pronunciation')
        results['pronunciation'] = [score , feedback]
        results['fluency'] = [fluency_analysis(wav_file, text)]

    # Add analysis scores to each segment
    for segment in transcription.segments:
        results = {}
        analyze_segment(segment, results)
        segment['scores'] = results  # Add the scores directly to the segment

    # Generate the updated JSON with scores
    transcription_with_scores = {
        "text": transcription.text,
        "task": transcription.task,
        "language": transcription.language,
        "duration": transcription.duration,
        "segments": transcription.segments,
        "x_groq": transcription.x_groq  # Retain additional metadata
    }

    grammer_feedback = grammar_analysis(transcription.text)
    pronunciation_feedback = pronunciation_assessment(transcription.text , transcription.text)
    fluency_data = fluency_analysis(wav_file , transcription.text)

    # Step 5: Generate Report
    report = generate_report(transcription.text , grammer_feedback , pronunciation_feedback , fluency_data)
    transcription_with_scores['report'] = report
    # Serialize Python object to JSON string
    json_data = json.dumps(transcription_with_scores)
        
        # Return Response with correct mimetype
    return Response(json_data, mimetype='application/json')


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
