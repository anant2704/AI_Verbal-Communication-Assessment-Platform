import os
import io
import time
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from groq import Groq
from pymongo import MongoClient
import gridfs
from flask_cors import CORS
import secrets
# Initialize Flask app
app = Flask(__name__)

app.secret_key = 'bkjdfbldiujbgslefjbv'

# Initialize Groq client
client = Groq(api_key='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')

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://prachi:Prachi_29@cluster0.qed64.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB Atlas connection string
client = MongoClient(MONGO_URI)

# Database and GridFS initialization
db = client['feedback']  # Replace with your database name
fs = gridfs.GridFS(db)  # Initialize GridFS for file storage
CORS(app)

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
        You are an industrial expert in verbal communication and English proficiency assessment. Evaluate the user's spoken response for grammatical accuracy, coherence, fluency, pronunciation, vocabulary usage, and overall communication effectiveness. Provide detailed feedback and actionable suggestions for improvement based on industry and professional communication standards. Include the following:

        1. Overall Score (out of 10):
        2. Grammatical Accuracy Score (out of 10) (ignore minor punctuation issues, focus on accuracy in grammar and sentence structure):
        3. Pronunciation Score (out of 10) (clarity and correctness of speech sounds):
        4. Vocabulary Usage Score (out of 10) (appropriateness and richness of word choice):
        5. Strengths (highlight areas where the user excelled in communication):
        6. Weaknesses (specific areas where the user struggled):
        7. Areas of Improvement (detailed guidance on how to improve, including specific examples):
        8. Ideal answer to the specific question: "{evaluation_question}"  
           (Display the question, then the user's spoken answer, followed by an ideal response as a model for improvement):
        9. Compulsory give Personalized Improvement Plan (structured, measurable goals to enhance verbal communication, pronunciation, vocabulary, and confidence in English speaking).

        Spoken response to evaluate:
        "{user_speech}"
        """

        # Send the prompt to Groq for evaluation
        completion = client.chat.completions.create(
            model="llama-3.2-3b-preview",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Extract the model's response
        evaluation_result = completion.choices[0].message.content

        # Format the result for HTML output (line breaks for readability)
        formatted_result = evaluation_result.replace('\n', '<br>')

        # Store the evaluation result as a PDF in MongoDB using GridFS
        # Convert the formatted result to PDF (pseudo-code, adjust as per your PDF generation method)
        pdf_data = io.BytesIO(generate_pdf_from_text(formatted_result))  # Replace with actual PDF generation logic
        
        # Save the PDF to MongoDB
        file_id = fs.put(pdf_data, filename="feedback.pdf")

        # Store the generated PDF file ID in session
        session['pdf_file_id'] = str(file_id)

        # Return the evaluation result to the frontend
        return render_template('feedback.html', evaluation=formatted_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback')
def feedback():
    # Use session or global variable to store the evaluation
    evaluation = session.get('evaluation', 'No evaluation yet')
    return render_template('feedback.html', evaluation=evaluation)

# Endpoint to display all the feedback PDFs stored in MongoDB
@app.route('/dashboard')
def dashboard():
    # Retrieve all files from MongoDB
    feedback_files = []
    for file in fs.find():
        feedback_files.append({"id": str(file._id), "filename": file.filename})

    # Pass the files to the template
    return render_template('dashboard.html', feedback_files=feedback_files)

# Endpoint to download the PDF feedback
@app.route('/download/<file_id>')
def download_pdf(file_id):
    try:
        # Retrieve the file by its ID
        file = fs.get(file_id)
        return send_file(
            io.BytesIO(file.read()),
            download_name=file.filename,
            as_attachment=True
        )
    except Exception as e:
        return str(e), 500

# Run the Flask app on the dynamic port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Use environment variable or default to 10000
    app.run(host='0.0.0.0', port=port, debug=True)
