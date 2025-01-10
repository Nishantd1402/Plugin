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
    
def get_completion_0( prompt):
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

    mp3_file = convert_webm_to_mp3(audio_path)
    # Convert to WAV
    wav_file = convert_to_wav(mp3_file)

    # Step 1: Transcribe audio
    transcription = transcribe_audio(wav_file)
      # Ensure transcription is a dictionary
    next_question = get_next_question(transcription , prev_question)
    results = compute_results(prev_question,transcription)
    return jsonify(next_question)

def extract_json(input_text):
    try:
        start = input_text.find('{')
        end = input_text.rfind('}')
        if start != -1 and end != -1:
            return input_text[start:end + 1]
        else:
            return "No JSON-like structure found."
    except Exception as e:
        return f"An error occurred: {e}"

def compute_results(question, candidate_answer):
    delimiter = "###"
    guidelines=f"""
      Use the following parameters for evaluating the answer for the provided question:

      A] General Evaluation Guidelines:
          1. Understand the Rubrics: The LLM must assess responses against the predefined parameters: Technical Knowledge, Mathematical Foundations, Problem-Solving Ability, and Communication Skills.
          2. Match Criteria: Align responses with the corresponding levels in the rubrics (e.g., Level 10 to Level 1) based on the quality, depth, and relevance of the answer.
          3. Quantify Scores: Assign a score (1–10) for each parameter based on how closely the candidate’s response meets the level-specific criteria.
          4. Provide Feedback: Justify each score with a concise explanation, citing strengths, gaps, and areas for improvement in the response.


      B] Parameter-Specific Guidelines:
          1. Technical Knowledge:
                i) Key Focus: Assess depth of understanding, ability to explain concepts, and knowledge of AI/ML frameworks and algorithms.
                ii) Scoring Process:
                      a) Analyze whether the candidate discusses foundational, intermediate, or advanced concepts.
                      b) Evaluate clarity, correctness, and ability to apply the knowledge practically.
                      c) Consider whether the candidate mentions cutting-edge topics or research trends.
                iii) Feedback Example:
                      a) Level 10: “The candidate demonstrated a deep understanding of GANs and transformers with precise explanations.”
                      b) Level 6: “The candidate knows basic concepts but struggles with advanced models like CNNs.”
          2. Mathematical Foundations
                i) Key Focus: Evaluate proficiency in applying linear algebra, calculus, probability, and statistics to AI/ML tasks.
                ii) Scoring Process:
                      a) Identify mathematical techniques referenced in responses and their accuracy.
                      b) Check for errors in understanding or application of mathematical concepts.
                      c) Assess whether the candidate integrates theory into practical AI/ML scenarios.
                iii) Feedback Example:
                      a) Level 9: “The candidate applied Bayes' theorem and matrix factorization accurately.”
                      b) Level 4: “The explanation of gradient descent was incomplete and contained errors.”
          3. Problem-Solving Ability
                i) Key Focus: Assess how effectively the candidate formulates, analyzes, and solves problems.
                ii) Scoring Process:
                      a) Review the approach for logical structure, innovation, and efficiency.
                      b) Check for the ability to solve standard and novel problems independently.
                      c) Evaluate whether the solution is practical and relevant.
                iii) Feedback Example:
                      a) Level 10: “Provided an optimal solution with an innovative use of reinforcement learning.”
                      b) Level 5: “Attempted the problem but required significant guidance to reach a partial solution.”
          4. Communication Skills
                i) Key Focus: Assess the clarity, precision, and audience-appropriateness of explanations.
                ii) Scoring Process:
                      a) Determine how effectively the candidate explains concepts and ideas.
                      b) Identify any oversimplifications or unnecessary technical jargon.
                      c) Evaluate whether explanations are audience-appropriate (technical or non-technical).
                iii) Feedback Example:
                      a) Level 8: “The explanation of overfitting was clear but lacked examples.”
                      b) Level 3: “The response was disorganized and difficult to follow.”

      C] Output Expectations
          1. For each parameter:
                i) Provide a numeric score (1–10).
                ii) Include a brief rationale for the score.
          2. Generate an overall summary highlighting:
                i) Key strengths.
                ii) Major gaps or areas of improvement.
                iii) Recommendations for next steps.
      D] Evaluation Constraints
          1. Avoid bias by focusing strictly on the content of the response.
          2. Handle incomplete answers by scoring only the provided parts and noting gaps.
          3. Use context provided in the question to ensure fairness and relevance.
"""
    
    prompt = f"""
    You are an AI evaluator tasked with evaluating a candidate’s answer to an AI/ML interview question. The evaluation involves comparing the candidate’s answer to the ideal answer based on predefined rubrics. You must assess how well the candidate’s answer aligns with the ideal answer and score it accordingly.

    Inputs:
        1. Question: {question}
        2. Candidate's Answer: {candidate_answer}

    Evaluation Process:
          1. Analyze the candidate’s response based on the question provided.
          2. For each parameter:
                i) Assign a score (1–10) based on how closely the candidate’s answer aligns with the question provided.
          3. Calculate the average score across all parameters and summarize the evaluation.

    Evaluation Parameters:
    {guidelines}

    {delimiter}

    The output must strictly follow this JSON format:
    {{
      "evaluation": {{
        "criteria": {{
          "Technical Knowledge": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to technical knowledge"
          }},
          "Mathematical Foundations": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to mathematical foundations"
          }},
          "Problem-Solving Ability": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to problem-solving ability"
          }},
          "Communication Skills": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to communication skills"
          }}
        }},
        "summary": {{
          "strengths": "highlight key strengths",
          "gaps": "identify gaps in the answer",
          "areas_for_improvement": "suggest specific improvements"
        }}
      }}
    }}
    """

    # Generate completion
    response = get_completion(prompt)
    extracted_json = extract_json(response)
    print(extracted_json) 
    return extracted_json

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
