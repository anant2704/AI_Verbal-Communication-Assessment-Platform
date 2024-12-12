import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
from groq import Groq
from werkzeug.utils import secure_filename
import time
#mahesh new
# Initialize Flask app
app = Flask(__name__)

app.secret_key = 'bkjdfbldiujbgslefjbv'

# Initialize Groq client
client = Groq(api_key='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')

# Set up the directory to save PDFs
FEEDBACK_DIR = 'static/feedbacks'

# Ensure the feedbacks directory exists
if not os.path.exists(FEEDBACK_DIR):
    os.makedirs(FEEDBACK_DIR)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')
# Route for index.html
@app.route('/index')
def index():
    return render_template('index.html')

# Route to handle text input and question from the frontend
@app.route('/evaluate', methods=['POST'])
def evaluate_speech():
    try:
        # Get data from the POST request
        data = request.form
        user_speech = data.get("speech_text", "")
        evaluation_question = data.get("question", "")

        if not user_speech:
            return jsonify({"error": "No speech text provided"}), 400

        if not evaluation_question:
            return jsonify({"error": "No evaluation question provided"}), 400

        # Define a unique prompt for each request
        prompt = f"""
       

        You are an industrial expert verbal communication assessment evaluator. Analyze the following text for grammatical accuracy, coherence, fluency, and overall effectiveness. Provide:
        A  Personalized Improvement Plan Offer structured, actionable feedback based on industry standards. Provide specific, measurable improvement goals to guide the user’s progress.with the things given below:-

        don't give ** symbol in output anywhere.
        and also  don't give unncessary text like:-Evaluating the provided text for grammatical accuracy, coherence, fluency, and overall effectiveness. and Chat History in the output just start with the things below:-

        1. Overall Score (out of 10):-
        2. Grammatical Accuracy Score (out of 10)(ignore punctuation errors, focus on wording accuracy):-
        3. Strengths
        4. Weaknesses
        5. Areas of Improvement
        6. Ideal answer to the specific question: "{evaluation_question}" (Display the question, then the user answer, and then an ideal answer)
        7. Personalized Improvement Plan which was mentioned above for imporvement in verbal communication .
        Text to evaluate:
        "{user_speech}"

        Give different feedback every time and clear the previous chat history.
        """

        # Send the prompt to Groq for evaluation
        completion = client.chat.completions.create(
            model="llama-3.2-3b-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Extract the model's response
        evaluation_result = completion.choices[0].message.content

        # Format the result for HTML output (line breaks for readability)
        formatted_result = evaluation_result.replace('\n', '<br>')

        # Store evaluation result in session
        session['evaluation'] = formatted_result

        # Return the evaluation result to the frontend
        return render_template('feedback.html', evaluation=formatted_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback')
def feedback():
    # Use session or global variable to store the evaluation
    # For now, using a temporary solution to pass the evaluation
    evaluation = session.get('evaluation', 'No evaluation yet')
    return render_template('feedback.html', evaluation=evaluation)

# Endpoint to display all the feedbacks
@app.route('/dashboard')
def dashboard():
    # Get a list of all PDF files in the feedback directory
    feedback_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith('.pdf')]
    
    # Sort the files by their creation date, so the most recent is shown first (optional)
    feedback_files.sort(key=lambda x: os.path.getmtime(os.path.join(FEEDBACK_DIR, x)), reverse=True)

    # Pass the list of files to the template
    return render_template('dashboard.html', feedback_files=feedback_files)

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Secure the filename to prevent directory traversal issues
    filename = secure_filename(file.filename)
    
    # Create a unique filename by appending a timestamp or random string to it
    unique_filename = f"{int(time.time())}_{filename}"  # Using timestamp for uniqueness
    
    # Define the path where the file will be saved
    file_path = os.path.join(FEEDBACK_DIR, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # After saving, redirect to the dashboard to show the updated list of PDFs
    return redirect(url_for('dashboard'))

# Endpoint to download the PDF feedback
@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory(FEEDBACK_DIR, filename)

# Run the Flask app on the dynamic port
if _name_ == '_main_':
    port = int(os.environ.get('PORT', 10000))  # Use environment variable or default to 10000
    app.run(host='0.0.0.0', port=port, debug=True)
