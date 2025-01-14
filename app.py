import os
import re
from flask import Flask, request, jsonify, render_template, redirect, url_for , Response
from flask_cors import CORS
from pydub import AudioSegment
from groq import Groq
import json
import numpy as np
from flask import Flask, request, jsonify
import asyncio
import threading
import time

def run_in_background(coro):
    """Runs an asyncio coroutine in a background thread."""
    start_time = time.time()
    asyncio.run(coro)
    end_time = time.time()
    print("Task finished in the background thread.  -   " , end_time - start_time)


# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = './uploads'
# app.config["MONGO_URI"] = "mongodb+srv://jainmitesh2393:rWCYwbKfmqfHo1Xx@cluster0.embny.mongodb.net/twitter?retryWrites=true&w=majority&appName=Cluster0"  # Change this to your MongoDB URI
# app.config["SECRET_KEY"] = "your_secret_key"  # Use a strong secret key
# mongo = PyMongo(app)

# SESSION_FILE = "evaluation_results.json"

# # Helper function to generate JWT token
# def generate_token(user_id):
#     payload = {
#         'user_id': str(user_id),
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
#     }
#     token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
#     return token

# # Signup endpoint
# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({'message': 'Username and password are required'}), 400

#     # Check if user already exists
#     existing_user = mongo.db.users.find_one({'username': username})
#     if existing_user:
#         return jsonify({'message': 'Username already exists'}), 400

#     # Hash the password before storing it
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

#     # Save user to MongoDB
#     user = {
#         'username': username,
#         'password': hashed_password
#     }
#     result = mongo.db.users.insert_one(user)

#     return jsonify({'message': 'User created successfully'}), 201

# # Login endpoint
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({'message': 'Username and password are required'}), 400

#     # Check if user exists
#     user = mongo.db.users.find_one({'username': username})
#     if not user:
#         return jsonify({'message': 'User not found'}), 404

#     # Check if password is correct
#     if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
#         return jsonify({'message': 'Invalid password'}), 401

#     # Generate JWT token
#     token = generate_token(user['_id'])
    
#     return jsonify({'message': 'Login successful', 'token': token}), 200

# # Protected route to demonstrate token validation
# @app.route('/protected', methods=['GET'])
# def protected():
#     token = request.headers.get('Authorization')

#     if not token:
#         return jsonify({'message': 'Token is missing'}), 401

#     try:
#         # Remove 'Bearer ' from token if included
#         token = token.split(" ")[1]
        
#         # Decode the JWT token
#         payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#         user_id = payload['user_id']

#         # You can now use user_id to fetch data from MongoDB if needed
#         user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
#         if not user:
#             return jsonify({'message': 'User not found'}), 404

#         return jsonify({'message': 'Access granted', 'user': user['username']}), 200

#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token expired'}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}), 401

# Due to difference in tempreature.
def get_completion(prompt):
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
    
def get_completion_0(prompt):
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
    return transcription.text

def get_next_question(transcribed_text , prev_question , domain):
    prompt = f"""
You are acting as an interviewer in the domain of {domain}. Your role is to ask the next relevant question based on the flow of the interview. You already have the transcribed text of the candidate's answer and the previous question. Use this information to ensure the conversation feels natural and progressive.

  Inputs:
  - Domain: ``{domain}```
  - Previous Question: ```{prev_question}```
  - Candidate's Answer: ```{transcribed_text}``

  Instructions:
  1. Analyze the previous question and the candidate's response to identify key topics or gaps that can be explored further.
  2. Formulate a new question that naturally follows the discussion and delves deeper into the topic or transitions smoothly to another relevant topic in the domain.
  3. The question should be open-ended and encourage the candidate to elaborate or demonstrate their expertise.

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
        
def save_to_session(extracted_json, question, candidate_answer, session_file="evaluation_results.json"):
    try:
        # Load existing data if the file exists
        session_data = {}
        try:
            with open(session_file, "r") as file:
                session_data = json.load(file)
        except FileNotFoundError:
            session_data = {
                "Score": [],
            }
        if session_data == {}:
            session_data = {
                "Score": [],
            }

        # Append extracted JSON to the Score section
        session_data["Score"].append(extracted_json)

        # Save updated data back to the file
        with open(session_file, "w") as file:
            json.dump(session_data, file, indent=4)

    except Exception as e:
        print(f"Error saving to session: {e}")



# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/FirstQuestion' , methods=['POST' , 'GET'])
def first_question():
    domain = request.form.get("domain" , "")
    num = np.random.randint(0,9)
    with open('firstQuestion.json', 'r') as file:
        data = json.load(file)
    
    question = data[domain][num]
    return jsonify(question)


@app.route('/results' , methods=['GET'])
def results():
    total_score = 0
    communication = 0
    problem_solving = 0
    skills = {}    
    
    with open("evaluation_results.json" , "r") as f:
        data = json.load(f)
    with open("conversation.json" , "r") as file:
        conversation = json.load(file)
    
    # Process each evaluation text and extract the relevant values
    for score_text in data["Score"]:
        # Parse the JSON string
        evaluation = json.loads(score_text)
        
        # Extract the scores for relevant categories
        for skill, details in evaluation['evaluation']['criteria'].items():
            if skill not in skills:
                skills[skill] = 0  # Initialize the skill in the dictionary if not already present
            skills[skill] += details['score']  # Add the score to the existing skill score
            
            total_score += details['score']  # Add the score to the total score
            
            # For communication and problem-solving scores
            if skill == "Communication Skills":
                communication += details['score']
            elif skill == "Problem-Solving Ability":
                problem_solving += details['score']

        

    # Calculate the total score average
    average_score = round((total_score / 180) * 100 , 2)
    
    
    for i in skills:
        skills[i] = round((skills[i] / 30) * 100 , 2)
    communication = skills["Communication Skills"]
    problem_solving = skills["Problem-Solving Ability"]
    
    observation = get_feedback()

    return jsonify({"Conversation" : conversation , "total_score" : average_score , "communication" : communication , "problem_solving" : problem_solving , "skills" : skills , "average_score" : average_score , "observations" : observation})

@app.route('/clear' , methods=['GET'])
def clearData():
    with open("evaluation_results.json" , "w") as f:
        default_data = {}
        json.dump(default_data , f)
        f.close()
    with open("conversation.json" , "w") as f:
        default_data = {}
        json.dump(default_data , f)
        f.close()
    return jsonify({"message" : "Data Cleared"})
        

# Route: Analyze Speech
@app.route('/analyze', methods=['POST' , 'GET'])
def analyze_speech():
    if request.method == 'GET':
        return "Please use the POST method to send data"
    if 'audio' not in request.files:
        return "No File attached"

    audio_file = request.files['audio']
    prev_question = request.form.get("previous","")
    domain = request.form.get("domain" , "")
    # Save audio locally
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
    audio_file.save(audio_path)

    mp3_file = convert_webm_to_mp3(audio_path)
    # Convert to WAV
    wav_file = convert_to_wav(mp3_file)

    # Step 1: Transcribe audio
    transcription = str(transcribe_audio(wav_file))
      # Ensure transcription is a dictionary
    next_question = get_next_question(transcription , prev_question , domain)
    
    # Schedule compute_results to run in the background
    thread = threading.Thread(target=run_in_background, args=(compute_results(prev_question, transcription , domain),))
    thread.start()
    
    try:
        # Load existing data
        with open("conversation.json", "r") as f:
            file_data = json.load(f)
    except FileNotFoundError:
        # File doesn't exist; initialize a new structure
        file_data = {"conversation": []}
    except json.JSONDecodeError:
        # File exists but is empty or corrupt; initialize a new structure
        file_data = {"conversation": []}
    if file_data == {}:
        file_data = {"conversation": []}

    # Append new data to the conversation
    new_data = {
        "question": prev_question,
        "answer": transcription,
    }

    file_data["conversation"].append(new_data)

    # Save updated data back to the file
    with open("conversation.json", "w") as f:
        json.dump(file_data, f, indent=4)
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

async def compute_results(question, candidate_answer , domaim):
    
    delimiter = "###"
            
    guidelines_product=f"""
                Use the following parameters for evaluating the answer for the provided question:

        A] General Evaluation Guidelines:
            1. Understand the Rubrics: Assess responses against the predefined parameters specific to the Product Manager role.
            2. Match Criteria: Align responses with the corresponding levels in the rubrics (e.g., Level 10 to Level 1) based on the quality, depth, and relevance of the answer.
            3. Quantify Scores: Assign a score (1–10) for each parameter based on how closely the candidate’s response meets the level-specific criteria.
            4. Provide Feedback: Justify each score with a concise explanation, citing strengths, gaps, and areas for improvement in the response.

        B] Parameter-Specific Guidelines:
            1. *Technical Knowledge:*
                    i) *Key Focus:* Assess depth of understanding, ability to explain concepts, and knowledge of AI/ML frameworks and algorithms.
                    ii) *Scoring Process:*
                        a) *Level 10:* Demonstrates an in-depth mastery of technical aspects, driving product decisions aligned with both user needs and technical constraints.
                        b) *Level 9:* Exceptionally skilled in managing cross-functional technical teams and understanding the technical feasibility of complex projects.
                        c) *Level 8:* Strong understanding of technical concepts and processes, can lead technical teams with minimal guidance.
                        d) *Level 7:* Proficient in making data-driven technical decisions and managing product development cycles effectively.
                        e) *Level 6:* Solid understanding of the technical landscape, can collaborate effectively with technical teams on complex issues.
                        f) *Level 5:* Understands basic technical requirements, but needs support to manage complex technical decisions.
                        g) *Level 4:* Has general knowledge of technical processes, but lacks depth in implementing technical solutions.
                        h) *Level 3:* Limited technical knowledge, relies heavily on technical teams to handle implementation details.
                        i) *Level 2:* Basic understanding of the technical aspects, may struggle to manage technical aspects independently.
                        j) *Level 0:* Very limited technical understanding, unable to participate in technical discussions effectively.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate explained the technical trade-offs of the feature with clarity and accuracy.”
                        b) Level 5: “The response was correct but lacked depth or technical details.”
            2. Data-Driven Decision Making:
                    i) Key Focus: Assess the ability to analyze data, identify trends, and make informed decisions that align with organizational goals.
                    ii) *Scoring Process:*
                        a) *Level 10:* Exceptional ability to leverage data insights to influence strategic decisions and achieve measurable outcomes.
                        b) *Level 9:* Proficient in designing data pipelines and integrating advanced analytics into decision-making processes.
                        c) *Level 8:* Strong skills in interpreting complex datasets and aligning findings with business objectives.
                        d) *Level 7:* Effectively uses data tools to inform decisions and assess performance metrics regularly.
                        e) *Level 6:* Can apply data analysis techniques to solve common challenges and support decision-making.
                        f) *Level 5:* Adequate understanding of basic data tools, though interpretation may lack depth.
                        g) *Level 4:* Limited ability to independently derive actionable insights from data.
                        h) *Level 3:* Relies heavily on others to interpret data for decision-making.
                        i) *Level 2:* Basic understanding of data concepts but struggles to apply them effectively.
                        j) *Level 0:* Minimal to no engagement with data when making decisions.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate provided detailed insights using data, linking findings directly to strategic outcomes.”
                        b) Level 5: “Demonstrated an understanding of data tools but struggled to translate findings into actionable decisions.”
            3. *Problem-Solving Ability:*
                    i) *Key Focus:* Assess the candidate’s ability to identify issues, propose solutions, and anticipate challenges.
                    ii) *Scoring Process:*
                        a) *Level 10:* Exceptional at identifying root causes of complex issues and designing innovative, scalable solutions.
                        b) *Level 9:* Skilled at finding solutions to complex problems, with an emphasis on long-term impact and business strategy.
                        c) *Level 8:* Excellent at problem analysis and formulating actionable solutions to problems within the product lifecycle.
                        d) *Level 7:* Consistently solves medium- to high-complexity problems with effective solutions that align with business goals.
                        e) *Level 6:* Solves problems efficiently, although solutions may not always align perfectly with strategic objectives.
                        f) *Level 5:* Adequately solves problems but may struggle with complex or strategic issues.
                        g) *Level 4:* Solves basic problems but needs support when issues become more complex or strategic.
                        h) *Level 3:* Struggles to find solutions to problems and often relies on others for problem-solving.
                        i) *Level 2:* Rarely provides effective solutions, tends to approach problems without sufficient strategic insight.
                        j) *Level 0:* Unable to address problems in a constructive manner, struggles to provide meaningful solutions.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate proposed a scalable solution with clear steps for implementation.”
                        b) Level 5: “The response addressed the problem but overlooked potential risks.”
            4. *Communication Skills*
                    i) *Key Focus:* Assess the clarity, precision, and audience-appropriateness of explanations.
                    ii) *Scoring Process:*
                        a) *Level 10:* Exceptionally clear communication; explains complex ideas succinctly to technical and non-technical audiences.
                        b) *Level 9:* Very clear communication; effectively conveys ideas with minor simplifications.
                        c) *Level 8:* Good communication; generally clear but occasionally struggles with explaining complex ideas.
                        d) *Level 7:* Adequate communication; explains ideas well but may struggle with technical details.
                        e) *Level 6:* Basic communication; can explain basic concepts but struggles with complex ideas.
                        f) *Level 5:* Limited communication; frequently unclear or oversimplifies.
                        g) *Level 4:* Poor communication; struggles to convey ideas, causing confusion.
                        h) *Level 3:* Very poor communication; consistently unclear and difficult to understand.
                        i) *Level 2:* Minimal communication skills; rarely conveys ideas effectively.
                        j) *Level 0:* No communication skills; cannot articulate ideas at all.
                    iii) *Feedback Example:*
                        a) Level 8: “The explanation of overfitting was clear but lacked examples.”
                        b) Level 3: “The response was disorganized and difficult to follow.”
            5. User-Centric Design and Customer Empathy
                    i) *Key Focus:* Assess understanding of user needs, ability to design user-friendly solutions, and empathy toward customer experiences.
                    ii) *Scoring Process:*
                        a) *Level 10:* Consistently integrates deep user insights into design decisions, resulting in highly impactful and user-friendly solutions.
                        b) *Level 9:* Demonstrates exceptional empathy and can lead user research initiatives to refine product experiences.
                        c) *Level 8:* Strong understanding of user personas and consistently aligns design decisions with customer feedback.
                        d) *Level 7:* Effectively translates user insights into actionable design changes that improve usability.
                        e) *Level 6:* Shows a good understanding of user needs but may require guidance to fully incorporate feedback into designs.
                        f) *Level 5:* Understands basic principles of user-centered design but lacks depth in applying them consistently.
                        g) *Level 4:* Limited empathy for user challenges, often prioritizing technical solutions over user experience.
                        h) *Level 3:* Relies heavily on others for user research and design validation.
                        i) *Level 2:* Basic understanding of user-centric concepts but struggles to apply them effectively.
                        j) *Level 0:* Little to no focus on user needs in design or decision-making.
                    iii) *Feedback Example:*
                        a) Level 10:  “The candidate demonstrated a deep understanding of the user journey and made impactful, customer-focused suggestions.”
                        b) Level 5:  “Understood the importance of user needs but struggled to translate them into effective design changes.”
            6. Strategic Thinking and Roadmap Planning
                    i) *Key Focus:*  Assess the ability to think strategically, align goals with broader organizational objectives, and create actionable roadmaps that balance short-term and long-term priorities.
                    ii) *Scoring Process:*
                        a) *Level 10:* Demonstrates exceptional strategic vision, foreseeing long-term trends and their implications, and creating roadmaps that align perfectly with organizational goals and market demands.
                        b) *Level 9:* Expertly aligns strategic objectives with operational execution, effectively balancing innovative goals with realistic planning for cross-functional teams.
                        c) *Level 8:* Strong strategic thinker who can identify key opportunities and risks, creating roadmaps that address both short-term and long-term needs with minimal input.
                        d) *Level 7:* Proficient in identifying priorities, setting milestones, and communicating the strategic value of decisions to stakeholders effectively.
                        e) *Level 6:* Capable of creating actionable roadmaps that balance immediate deliverables with broader strategic goals.
                        f) *Level 5:* Understands strategic goals and can create a roadmap with guidance, but struggles to balance competing priorities independently.
                        g) *Level 4:* Has basic knowledge of roadmap planning but struggles to integrate strategic thinking into actionable plans.
                        h) *Level 3:* Limited ability to think beyond immediate tasks, resulting in roadmaps that lack alignment with broader goals.
                        i) *Level 2:* Struggles with roadmap planning, often failing to incorporate strategic alignment or anticipate future needs.
                        j) *Level 0:* Lacks understanding of strategic thinking and roadmap planning, unable to contribute meaningfully to these processes.
                    iii) *Feedback Example:*
                        a) Level 10: "The candidate demonstrated a clear vision, providing a roadmap that anticipates future trends while addressing current challenges."
                        b) Level 5: "The roadmap addressed immediate priorities but lacked integration with long-term objectives."
        
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
        
    prompt_product = f"""
        You are an AI evaluator tasked with evaluating a candidate’s answer to an product manager interview question. The evaluation involves comparing the candidate’s answer to the ideal answer based on predefined rubrics. You must assess how well the candidate’s answer aligns with the ideal answer and score it accordingly.

        Inputs:
            1. Question: {question}
            2. Candidate's Answer: {candidate_answer}

        Evaluation Process:
            1. Analyze the candidate’s response based on the question provided.
            2. For each parameter:
                    i) Assign a score (1–10) based on how closely the candidate’s answer aligns with the question provided.
            3. Calculate the average score across all parameters and summarize the evaluation.

        Evaluation Parameters:
        {guidelines_product}

        {delimiter}

        The output must strictly follow this JSON format:
        {{
        "evaluation": {{
            "criteria": {{
            "Technical Knowledge": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to technical knowledge"
            }},
            "Data-Driven Decision Making": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Data-Driven Decision Making"
            }},
            "Problem-Solving Ability": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Problem-Solving Ability"
            }},
            "Communication Skills": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to communication skills"
            }},
            "User-Centric Design and Customer Empathy": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to User-Centric Design and Customer Empathy"
            }},
            "Strategic Thinking and Roadmap Planning": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Strategic Thinking and Roadmap Planning"
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

    guidelines_aiml=f"""
        Use the following parameters for evaluating the answer for the provided question:

        A] General Evaluation Guidelines:
            1. Understand the Rubrics: The LLM must assess responses against the predefined parameters: Technical Knowledge, Mathematical Foundations, Problem-Solving Ability, and Communication Skills.
            2. Match Criteria: Align responses with the corresponding levels in the rubrics (e.g., Level 10 to Level 1) based on the quality, depth, and relevance of the answer.
            3. Quantify Scores: Assign a score (1–10) for each parameter based on how closely the candidate’s response meets the level-specific criteria.
            4. Provide Feedback: Justify each score with a concise explanation, citing strengths, gaps, and areas for improvement in the response.

        B] Parameter-Specific Guidelines:
            1. *Technical Knowledge:*
                    i) *Key Focus:* Assess depth of understanding, ability to explain concepts, and knowledge of AI/ML frameworks and algorithms.
                    ii) *Scoring Process:*
                        a) *Level 10:* Deep understanding of AI/ML concepts, including advanced algorithms, frameworks, and mathematical foundations. Can explain and apply complex models effortlessly.
                        b) *Level 9:* Strong understanding with minor gaps. Can explain most advanced concepts and demonstrate knowledge of current research trends.
                        c) *Level 8:* Good understanding with some gaps in advanced areas. Can explain key ML algorithms and concepts but struggles with cutting-edge research.
                        d) *Level 7:* Adequate understanding of core ML concepts. Can discuss standard algorithms like linear regression, decision trees, etc., but limited knowledge of advanced models.
                        e) *Level 6:* Basic understanding with several gaps. Familiar with key concepts but lacks depth in understanding and application.
                        f) *Level 5:* Limited understanding; can discuss only basic concepts. Lacks familiarity with most AI/ML frameworks and advanced topics.
                        g) *Level 4:* Poor understanding; major gaps in basic knowledge. Unable to explain or apply fundamental algorithms.
                        h) *Level 3:* Very poor understanding; unable to discuss basic concepts. Lacks any significant knowledge of the field.
                        i) *Level 2:* Minimal understanding; can barely mention basic AI/ML terms. No practical or theoretical knowledge.
                        j) *Level 0:* No understanding of AI/ML concepts. Completely unaware of foundational principles.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate demonstrated a deep understanding of GANs and transformers with precise explanations.”
                        b) Level 6: “The candidate knows basic concepts but struggles with advanced models like CNNs.”
            2. *Coherence and Cohesion:*
                    i) *Key Focus:* Evaluate the logical flow, clarity, and structural organization of the response.
                    ii) *Scoring Process:*
                        a) *Level 10:* Deep understanding of AI/ML concepts, including advanced algorithms, frameworks, and mathematical foundations. Can explain and apply complex models effortlessly.
                        b) *Level 9:* Strong understanding with minor gaps. Can explain most advanced concepts and demonstrate knowledge of current research trends.
                        c) *Level 8:* Good understanding with some gaps in advanced areas. Can explain key ML algorithms and concepts but struggles with cutting-edge research.
                        d) *Level 7:* Adequate understanding of core ML concepts. Can discuss standard algorithms like linear regression, decision trees, etc., but limited knowledge of advanced models.
                        e) *Level 6:* Basic understanding with several gaps. Familiar with key concepts but lacks depth in understanding and application.
                        f) *Level 5:* Limited understanding; can discuss only basic concepts. Lacks familiarity with most AI/ML frameworks and advanced topics.
                        g) *Level 4:* Poor understanding; major gaps in basic knowledge. Unable to explain or apply fundamental algorithms.
                        h) *Level 3:* Very poor understanding; unable to discuss basic concepts. Lacks any significant knowledge of the field.
                        i) *Level 2:* Minimal understanding; can barely mention basic AI/ML terms. No practical or theoretical knowledge.
                        j) *Level 0:* No understanding
                    iii) *Feedback Example:*
                        a) Level 9: “The candidate applied Bayes' theorem and matrix factorization accurately.”
                        b) Level 4: “The explanation of gradient descent was incomplete and contained errors.”
            3. *Problem-Solving Ability:*
                    i) *Key Focus:* Assess how effectively the candidate formulates, analyzes, and solves problems.
                    ii) *Scoring Process:*
                        a) *Level 10:* Highly coherent; excellent flow between ideas. Logical progression of ideas with smooth transitions.
                        b) *Level 9:* Very coherent; minor lapses in flow. Generally clear, with a few abrupt transitions.
                        c) *Level 8:* Generally coherent; some choppy transitions. Ideas mostly flow well, but some sections feel disconnected.
                        d) *Level 7:* Moderately coherent; noticeable breaks in flow. Some sections feel disconnected, requiring clarification.
                        e) *Level 6:* Somewhat coherent; frequent breaks in flow. Readers may struggle to follow the progression of ideas.
                        f) *Level 5:* Limited coherence; ideas often disjointed. Difficult to understand due to frequent breaks in logical progression.
                        g) *Level 4:* Poor coherence; ideas rarely connected. Appears in random order, making the text confusing.
                        h) *Level 3:* Very poor coherence; almost no logical flow. Text is a collection of unrelated ideas, challenging to follow.
                        i) *Level 2:* Barely any coherence; incomprehensible flow. Text fails to form a cohesive narrative or argument.
                        j) *Level 0:* No coherence; entirely disjointed. Text is a series of unrelated sentences with no discernible structure.
                    iii) *Feedback Example:*
                        a) Level 9: “The response is logically structured with clear transitions but slightly verbose.”
                        b) Level 4: “The explanation lacked clear connections between points, making it confusing.”
            4. *Communication Skills*
                    i) *Key Focus:* Assess the clarity, precision, and audience-appropriateness of explanations.
                    ii) *Scoring Process:*
                        a) *Level 10:* Exceptionally clear communication; explains complex ideas succinctly to technical and non-technical audiences.
                        b) *Level 9:* Very clear communication; effectively conveys ideas with minor simplifications.
                        c) *Level 8:* Good communication; generally clear but occasionally struggles with explaining complex ideas.
                        d) *Level 7:* Adequate communication; explains ideas well but may struggle with technical details.
                        e) *Level 6:* Basic communication; can explain basic concepts but struggles with complex ideas.
                        f) *Level 5:* Limited communication; frequently unclear or oversimplifies.
                        g) *Level 4:* Poor communication; struggles to convey ideas, causing confusion.
                        h) *Level 3:* Very poor communication; consistently unclear and difficult to understand.
                        i) *Level 2:* Minimal communication skills; rarely conveys ideas effectively.
                        j) *Level 0:* No communication skills; cannot articulate ideas at all.
                    iii) *Feedback Example:*
                        a) Level 8: “The explanation of overfitting was clear but lacked examples.”
                        b) Level 3: “The response was disorganized and difficult to follow.”
            5. *Ethics and Bias Awareness*
                    i) *Key Focus:* Evaluate the candidate's ability to identify, address, and mitigate ethical concerns, biases, or unfair outcomes in AI/ML solutions.
                    ii) *Scoring Process:*
                        a) *Level 10:* Expert in understanding AI/ML ethics, fairness, and bias mitigation strategies. Can address issues like fairness, accountability, and transparency effectively.
                        b) *Level 9:* Strong awareness of ethics and bias mitigation, with minor gaps in advanced topics like explainability or compliance.
                        c) *Level 8:* Good understanding of AI/ML ethics; familiar with fairness and bias but struggles with advanced strategies.
                        d) *Level 7:* Adequate awareness of ethical issues but lacks depth in addressing practical challenges or compliance requirements.
                        e) *Level 6:* Basic understanding of AI/ML ethics; knows general principles but lacks practical experience.
                        f) *Level 5:* Limited awareness of ethics; unable to identify or address key ethical concerns.
                        g) *Level 4:* Poor understanding of AI/ML ethics; overlooks potential ethical or fairness issues.
                        h) *Level 3:* Very poor ethics awareness; lacks understanding of the importance of fairness or accountability.
                        i) *Level 2:* Minimal knowledge of ethics in AI/ML; can mention terms but lacks understanding.
                        j) *Level 0:* No awareness of AI/ML ethics; completely oblivious to fairness, bias, or accountability concerns.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate identified multiple sources of bias, including dataset imbalance and model interpretability, and proposed robust mitigation strategies.”
                        b) Level 6: “The candidate mentioned fairness but failed to recognize key biases in the problem.”
                        c) Level 3: “The response lacked any consideration of ethical implications or bias mitigation.”
            6.  Adaptability
                    i) Key Focus: Evaluate the candidate’s ability to learn new AI/ML techniques, adapt to changing technologies, and solve novel problems.
                    ii) Scoring Process:
                        a) Level 10: Highly adaptable; quickly learns new concepts and applies them in practice with excellent results.
                        b) Level 9: Very adaptable; comfortable learning new techniques and integrating them into their workflow.
                        c) Level 8: Good adaptability; learns new techniques with some guidance and applies them effectively.
                        d) Level 7: Adequate adaptability; struggles a bit with new technologies but eventually picks them up.
                        e) Level 6: Basic adaptability; learns new concepts but may require significant time and effort to apply them.
                        f) Level 5: Limited adaptability; struggles to learn and apply new techniques effectively.
                        g) Level 4: Poor adaptability; resistant to learning new techniques and integrating them into their work.
                        h) Level 3: Very poor adaptability; unable to learn or apply new techniques.
                        i) Level 2: Minimal adaptability; resists learning new concepts or struggles significantly.
                        j) Level 0: No adaptability; unable to learn or apply new concepts at all.
                    iii) *Feedback Example:*
                        a) Level 10: "The candidate demonstrated exceptional adaptability by quickly adjusting to new tools and frameworks, successfully implementing solutions to real-time problems during the project. They also proactively sought feedback and iterated on their approach to improve performance."
                        b) Level 6: "The candidate showed a basic understanding of new tools and frameworks but struggled to adapt to complex challenges. While they made some adjustments, they did not fully capitalize on opportunities to improve their approach."
                        c) Level 3: "The candidate exhibited limited adaptability, struggling to adjust to new tools or changing requirements. Their approach to solving problems remained static, even when presented with new challenges."

        
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
        
    prompt_aiml = f"""
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
        {guidelines_aiml}

        {delimiter}

        The output must strictly follow this JSON format:
        {{
        "evaluation": {{
            "criteria": {{
            "Technical Knowledge": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to technical knowledge"
            }},
            "Coherence and Cohesion": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Coherence and Cohesion"
            }},
            "Problem-Solving Ability": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to problem-solving ability"
            }},
            "Communication Skills": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to communication skills"
            }},
            "Adaptability": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Adaptability"
            }},
            "Ethics and Bias Awareness": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Ethics and Bias Awareness"
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
        
    delimiter = "###"
        
    guidelines_system=f"""
        Use the following parameters for evaluating the answer for the provided question:

        A] General Evaluation Guidelines:
            1. Understand the Rubrics: Assess responses against the predefined parameters: System Architecture Design, Scalability & Performance Optimization, Distributed Systems Knowledge, Trade-Off Analysis, Communication Skills, Problem-Solving Ability and Coherence & Cohesion.
            2. Match Criteria: Align responses with the corresponding levels in the rubrics (e.g., Level 10 to Level 1) based on the quality, depth, and relevance of the answer.
            3. Quantify Scores: Assign a score (1–10) for each parameter based on how closely the candidate’s response meets the level-specific criteria.
            4. Provide Feedback: Justify each score with a concise explanation, citing strengths, gaps, and areas for improvement in the response.

        B] Parameter-Specific Guidelines:
            1. *System Architecture Design:*
                    i) *Key Focus:* Evaluate the candidate’s ability to design efficient, robust, and modular system architectures.
                    ii) *Scoring Process:*
                        a) *Level 10:* Designs highly scalable, fault-tolerant, and cost-efficient architectures with innovative approaches.
                        b) *Level 9:* Demonstrates strong expertise in creating complex, distributed architectures with a clear focus on performance and scalability.
                        c) *Level 8:* Proficient in designing robust architectures considering trade-offs between scalability, performance, and maintainability.
                        d) *Level 7:* Creates efficient and scalable architectures for moderately complex systems with minimal guidance.
                        e) *Level 6:* Solid understanding of architecture design principles, capable of handling standard system requirements.
                        f) *Level 5:* Designs functional architectures for basic systems but struggles with advanced scalability or fault tolerance needs.
                        g) *Level 4:* Limited understanding of architectural principles; designs are functional but lack scalability or robustness.
                        h) *Level 3:* Struggles to design coherent system architectures; frequently misses critical design components.
                        i) *Level 2:* Poor understanding of system architecture; designs lack scalability, efficiency, or fault tolerance.
                        j) *Level 0:* Unable to design effective system architectures.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate designed a well-structured system with clear component interactions.”
                        b) Level 5: “The architecture was functional but lacked modularity.”
            2. *Scalability & Performance Optimization:*
                    i) *Key Focus:* Assess the ability to plan for scalability, performance tuning, and handling of high-traffic scenarios.
                    ii) *Scoring Process:*
                        a) *Level 10:* Implements advanced optimizations to handle high-scale traffic with minimal latency and resource consumption.
                        b) *Level 9:* Excellent in identifying bottlenecks and optimizing system performance at scale for real-world workloads.
                        c) *Level 8:* Proficient in designing scalable systems and resolving performance issues in large, distributed environments.
                        d) *Level 7:* Strong ability to improve system scalability and performance in moderately complex environments.
                        e) *Level 6:* Solid understanding of scalability and performance optimization; handles common scenarios effectively.
                        f) *Level 5:* Resolves basic scalability or performance issues but struggles with complex or high-scale challenges.
                        g) *Level 4:* Limited ability to identify or resolve performance bottlenecks in larger systems.
                        h) *Level 3:* Struggles with scaling systems or ensuring acceptable performance under load.
                        i) *Level 2:* Lacks the ability to address scalability or performance challenges effectively.
                        j) *Level 0:* Unable to identify or resolve scalability and performance issues.
                    iii) *Feedback Example:*
                        a) Level 10: “The response included horizontal scaling and caching strategies to optimize performance.”
                        b) Level 5: “The scalability approach was sufficient but lacked detail in handling bottlenecks.”
            3. *Distributed Systems Knowledge:*
                    i) *Key Focus:* Evaluate the understanding of distributed system principles, including consistency, availability, and partitioning.
                    ii) *Scoring Process:*
                        a) *Level 10:* Deep understanding of distributed systems principles, able to design and optimize highly complex solutions.
                        b) *Level 9:* Expert in distributed systems, including consensus algorithms, replication, partitioning, and sharding.
                        c) *Level 8:* Proficient in implementing distributed system patterns like leader election, load balancing, and failover.
                        d) *Level 7:* Strong knowledge of distributed systems and applies concepts effectively to moderately complex use cases.
                        e) *Level 6:* Solid understanding of distributed systems; implements basic patterns like caching and replication.
                        f) *Level 5:* Basic knowledge of distributed systems; struggles with advanced techniques like consistency or partitioning.
                        g) *Level 4:* Limited understanding of distributed systems; solutions often miss critical elements like reliability or availability.
                        h) *Level 3:* Struggles to apply distributed systems principles effectively; solutions often fail in high-scale scenarios.
                        i) *Level 2:* Lacks understanding of distributed systems concepts, resulting in poor or inefficient designs.
                        j) *Level 0:* No meaningful knowledge of distributed systems principles or techniques.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate leveraged eventual consistency principles effectively in the design.”
                        b) Level 5: “The response mentioned distributed systems but lacked depth in implementation.”
            4. *Trade-Off Analysis:*
                    i) *Key Focus:* Assess the ability to analyze trade-offs between different design choices (e.g., cost vs. performance, consistency vs. availability).
                    ii) *Scoring Process:*
                        a) *Level 10:* Consistently evaluates and justifies trade-offs in scalability, consistency, latency, and resource utilization.
                        b) *Level 9:* Excellent ability to prioritize and explain trade-offs across multiple dimensions (e.g., CAP theorem, cost).
                        c) *Level 8:* Proficient in analyzing trade-offs and balancing competing priorities in system design decisions.
                        d) *Level 7:* Strong ability to consider and explain trade-offs, though may occasionally miss some minor aspects.
                        e) *Level 6:* Solid understanding of trade-offs, capable of making informed design decisions with minor gaps.
                        f) *Level 5:* Understands basic trade-offs but struggles with balancing multiple dimensions in complex systems.
                        g) *Level 4:* Limited ability to analyze trade-offs; decisions often lead to suboptimal designs.
                        h) *Level 3:* Frequently misses critical trade-offs, resulting in inefficient or unbalanced solutions.
                        i) *Level 2:* Rarely performs meaningful trade-off analysis; decisions are often poorly justified.
                        j) *Level 0:* Unable to identify or evaluate trade-offs, leading to flawed system designs.
                    iii) *Feedback Example:*
                        a) Level 10: “The candidate evaluated trade-offs between read performance and write consistency effectively.”
                        b) Level 5: “The trade-off analysis was superficial and missed key factors.”
            5. Communication Skills
                    i) Key Focus: Assess the clarity, precision, and audience-appropriateness of explanations.
                    ii) Scoring Process:
                        a) Level 10: Exceptionally clear communication; explains complex ideas succinctly to technical and non-technical audiences.
                        b) Level 9: Very clear communication; effectively conveys ideas with minor simplifications.
                        c) Level 8: Good communication; generally clear but occasionally struggles with explaining complex ideas.
                        d) Level 7: Adequate communication; explains ideas well but may struggle with technical details.
                        e) Level 6: Basic communication; can explain basic concepts but struggles with complex ideas.
                        f) Level 5: Limited communication; frequently unclear or oversimplifies.
                        g) Level 4: Poor communication; struggles to convey ideas, causing confusion.
                        h) Level 3: Very poor communication; consistently unclear and difficult to understand.
                        i) Level 2: Minimal communication skills; rarely conveys ideas effectively.
                        j) Level 0: No communication skills; cannot articulate ideas at all.
                    iii) Feedback Example:
                        a) Level 8: “The explanation of overfitting was clear but lacked examples.”
                        b) Level 3: “The response was disorganized and difficult to follow.”
            6. Problem-Solving Ability
                    i) Key Focus: Evaluate the candidate’s ability to identify and resolve key challenges within the design process.
                    ii) Scoring Process:
                        a) Level 10: Consistently develops creative, efficient, and scalable solutions for highly complex design challenges.
                        b) Level 9: Demonstrates excellent problem-solving ability, identifying and resolving advanced design challenges.
                        c) Level 8: Proficient in identifying root causes and implementing practical solutions for challenging system issues.
                        d) Level 7: Strong ability to solve moderately complex problems with a focus on clarity and efficiency.
                        e) Level 6: Solid problem-solving skills; capable of resolving common design challenges effectively.
                        f) Level 5: Resolves basic system challenges but struggles with moderately complex or ambiguous problems.
                        g) Level 4: Limited ability to solve complex problems; solutions often require significant refinement.
                        h) Level 3: Frequently struggles to develop practical or efficient solutions to system problems.
                        i) Level 2: Rarely produces effective solutions for even basic challenges.
                        j) Level 0: Unable to demonstrate problem-solving ability in system design contexts.
                    iii) Feedback Example:
                        a) Level 10: “The candidate tackled system bottlenecks with creative solutions and backed them with sound reasoning.”
                        b) Level 5: “The problem-solving approach was adequate but lacked depth in addressing edge cases.”
        
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
        
    prompt_system = f"""
        You are an AI evaluator tasked with evaluating a candidate’s answer to a system design interview question. The evaluation involves comparing the candidate’s answer to the ideal answer based on predefined rubrics. You must assess how well the candidate’s answer aligns with the ideal answer and score it accordingly.

        Inputs:
            1. Question: {question}
            2. Candidate's Answer: {candidate_answer}

        Evaluation Process:
            1. Analyze the candidate’s response based on the question provided.
            2. For each parameter:
                    i) Assign a score (1–10) based on how closely the candidate’s answer aligns with the question provided.
            3. Calculate the average score across all parameters and summarize the evaluation.

        Evaluation Parameters:
        {guidelines_system}

        {delimiter}

        The output must strictly follow this JSON format:
        {{
        "evaluation": {{
            "criteria": {{
            "System Architecture Design": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to System Architecture Design"
            }},
            "Scalability & Performance Optimization": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Scalability & Performance Optimization"
            }},
            "Problem-Solving Ability": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to problem-solving ability"
            }},
            "Communication Skills": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to communication skills"
            }},
            "Distributed Systems Knowledge": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Distributed Systems Knowledge"
            }},
            "Trade-Off Analysis": {{
                "score": "score (1-10)",
                "feedback": "feedback specific to Coherence and Cohesion"
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
    
    if domaim == "AI-ML":
        prompt = prompt_aiml
    if domaim == "Product-Manager":
        prompt = prompt_product
    else:
        prompt = prompt_system

    # Generate completion
    response = get_completion(prompt)
    extracted_json = extract_json(response)
    if isinstance(extracted_json, str) and "{" in extracted_json:
        # Save only if valid JSON is extracted
        save_to_session(extracted_json, question, candidate_answer)
        print(extracted_json)
    else:
        print("Invalid JSON extracted. Skipping save.")
        
def get_feedback():
    with open("conversation.json" , "r") as f:
        data = json.load(f)
    prompt = f"""
        Generate a JSON object based on the interview conversation - {data}. The JSON should contain the following topics:

Overall Summary: A concise summary of the candidate's performance during the interview, covering the major highlights, strengths, and any key observations.
Feedback: Specific feedback on the candidate's responses, focusing on their strengths, weaknesses, and overall performance in various skills.
Areas for Improvement: Identifying specific areas where the candidate needs to improve, such as technical skills, problem-solving abilities, communication, or other relevant factors.


The output must follow following JSON structure:
{{
    "Overall Summary": "Brief summary here",
    "Feedback": {{
        "Strengths": "Strengths identified here",
        "Weaknesses": "Weaknesses identified here"
    }},
    "Areas for Improvement": [
        "Area for improvement 1",
        "Area for improvement 2",
        "Area for improvement 3"
    ]
}}
    """
    
    result = get_completion(prompt)
    pattern = r'```(.*?)```'

        # Extract content using re.findall
    matches = re.findall(pattern, result, re.DOTALL)
    return json.loads(matches[0])


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()

