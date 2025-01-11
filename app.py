
import os
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
    return transcription

def get_next_question(transcribed_text , prev_question , domain):
    prompt = f"""
    Based on the user's response to the previous question in this {domain} interview, generate a new follow-up question that shifts focus to a different yet relevant topic within the field. The next question should not repeat or overly revolve around the previous discussion but instead explore a fresh area that tests the candidate's breadth of knowledge in {domain}. Ensure the question is challenging and opens up a different aspect of {domain}, moving the conversation in a new direction while still maintaining relevance to the overall interview.
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

    return jsonify({"total_score" : average_score , "communication" : communication , "problem_solving" : problem_solving , "skills" : skills , "average_score" : average_score})

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
    thread = threading.Thread(target=run_in_background, args=(compute_results(prev_question, transcription),))
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

async def compute_results(question, candidate_answer):
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
          2. *Market Understanding:*
                i) *Key Focus:* Evaluate the candidate’s ability to identify market trends, competitive landscape, and customer needs.
                ii) *Scoring Process:*
                      a) *Level 10:* Deeply understands market trends, customer behavior, and competitive landscape; consistently predicts shifts in the market.
                      b) *Level 9:* Demonstrates advanced ability to analyze market data and identify emerging trends that guide product strategy.
                      c) *Level 8:* Strong ability to evaluate market needs and leverage insights for effective product differentiation.
                      d) *Level 7:* Proficient in understanding customer needs and competitive landscape but may require additional analysis for future trends.
                      e) *Level 6:* Solid understanding of the market but lacks experience in identifying disruptive trends or emerging competition.
                      f) *Level 5:* Basic awareness of market trends and customer needs, but limited ability to assess competitive dynamics.
                      g) *Level 4:* Minimal understanding of market trends, relies heavily on external inputs for direction.
                      h) *Level 3:* Limited market understanding, struggles to identify opportunities for product improvement based on market trends.
                      i) *Level 2:* Very little awareness of the market, product decisions made without a clear grasp of external factors.
                      j) *Level 0:* No meaningful understanding of the market or competitive landscape.
                iii) *Feedback Example:*
                      a) Level 10: “The candidate effectively analyzed the market, identifying a key gap in competitors' offerings.”
                      b) Level 5: “The response mentioned general trends but missed actionable insights.”
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
          5. *Leadership & Collaboration*
                i) *Key Focus:* Assess the candidate’s ability to lead teams, manage conflicts, and align diverse stakeholders.
                ii) *Scoring Process:*
                      a) *Level 10:* Inspires teams, creates a vision for success, drives cross-functional collaboration, and influences organizational culture.
                      b) *Level 9:* Demonstrates exceptional leadership in driving alignment, resolving conflicts, and maintaining motivation across teams.
                      c) *Level 8:* Effectively leads teams and maintains alignment across multiple stakeholders and departments.
                      d) *Level 7:* Strong leadership skills, able to manage teams effectively and resolve conflicts, ensuring smooth project execution.
                      e) *Level 6:* Good leader but occasionally struggles to keep teams aligned or handle interpersonal conflicts effectively.
                      f) *Level 5:* Solid collaborator but may require guidance in motivating teams or resolving conflicts in a timely manner.
                      g) *Level 4:* Limited leadership experience, often relies on others to lead or provide direction in team settings.
                      h) *Level 3:* Struggles with leading teams and fostering collaboration across departments.
                      i) *Level 2:* Rarely takes a leadership role, lacks experience in leading teams or motivating others.
                      j) *Level 0:*  Does not demonstrate leadership abilities; struggles to engage or direct teams in any capacity.
                iii) *Feedback Example:*
                      a) Level 10: “The candidate outlined a clear plan for aligning stakeholders and ensuring team buy-in.”
                      b) Level 5: “The response mentioned collaboration but lacked conflict resolution strategies.”
          6. *Coherence and Cohesion*
                i) *Key Focus:*  Evaluate the logical flow, structure, and connection of ideas within the response.
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
                      a) Level 10: “The response followed a clear and logical structure, making it easy to follow.”
                      b) Level 5: “The response was generally well-organized but had minor gaps in flow.”
      
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
          "Market Understanding": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to Market Understanding"
          }},
          "Problem-Solving Ability": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to Problem-Solving Ability"
          }},
          "Communication Skills": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to communication skills"
          }},
          "Leadership & Collaboration": {{
            "score": "score (1-10)",
            "feedback": "feedback specific to Leadership & Collaboration"
          }},
          "Coherence and Cohesion": {{
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

    # Generate completion
    response = get_completion(prompt)
    extracted_json = extract_json(response)
    if isinstance(extracted_json, str) and "{" in extracted_json:
        # Save only if valid JSON is extracted
        save_to_session(extracted_json, question, candidate_answer)
    else:
        print("Invalid JSON extracted. Skipping save.")

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()
