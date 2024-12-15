import os
from flask import Flask, abort, flash, request, jsonify, render_template, session, redirect, url_for, send_file
from groq import Groq
from werkzeug.utils import secure_filename
import time
from pymongo import MongoClient
import gridfs
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import secrets
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

app.secret_key = secrets.token_hex(32)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)
mongo_client = MongoClient(MONGO_URI)

db = mongo_client["feedback_data"]
collection = db["feedback_collection"]
# Initialize GridFS to store files in MongoDB
fs = gridfs.GridFS(db)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login if not authenticated
        return f(*args, **kwargs)
    return decorated_function







# Add user collection for authentication
auth_collection = db["user_auth"]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email and password are provided
        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for('login'))

        try:
            # Find user by email
            user = auth_collection.find_one({"email": email})

            # Check if user exists and password matches
            if not user or not check_password_hash(user['password'], password):
                flash("Invalid email or password.", "error")
                return redirect(url_for('login'))

            # Store user information in session
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            flash("Login successful!", "success")
            return redirect(url_for('home'))

        except PyMongoError as e:
            # Handle database errors
            flash( "invalide user id or password")
            
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template('register.html')

        # Check if user already exists
        if auth_collection.find_one({"email": email}):
            flash("Already registered Mail ID.", "error")
            return render_template('register.html')

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert user data into MongoDB
        auth_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Route for login page
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash
from pymongo.errors import PyMongoError




# Route for logging out
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/home')
@login_required
def home():
    return render_template('home.html')
# Route for index.html
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# Route to handle text input and question from the frontend
@app.route('/evaluate', methods=['POST'])
@login_required
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

Do not use ** symbols in the output.
Do not include unnecessary text such as "Evaluating the provided text for..." or "Chat History." Start the output directly with the structured feedback below:

1. Overall Score (out of 10):-
2. Grammatical Accuracy Score (out of 10) (ignore minor punctuation issues, focus on accuracy in grammar and sentence structure):-
3. Pronunciation Score (out of 10) (clarity and correctness of speech sounds):-
4. Vocabulary Usage Score (out of 10) (appropriateness and richness of word choice):-
5. Strengths (highlight areas where the user excelled in communication):-
6. Weaknesses (specific areas where the user struggled):-
7. Areas of Improvement (detailed guidance on how to improve, including specific examples):-
8. Ideal answer to the specific question: "{evaluation_question}"  
   (Display the question, then the user's spoken answer, followed by an ideal response as a model for improvement):-
9. Complusory give Personalized Improvement Plan (structured, measurable goals to enhance verbal communication, pronunciation, vocabulary, and confidence in English speaking).

Spoken response to evaluate:
"{user_speech}"

Ensure feedback is varied and fresh with each evaluation. Clear all prior chat history to maintain unique feedback.

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

        # Store evaluation result in session
        session['evaluation'] = formatted_result

        # Return the evaluation result to the frontend
        return render_template('feedback.html', evaluation=formatted_result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback')
@login_required
def feedback():
    # Use session or global variable to store the evaluation
    # For now, using a temporary solution to pass the evaluation
    evaluation = session.get('evaluation', 'No evaluation yet')
    return render_template('feedback.html', evaluation=evaluation)



@app.route('/upload', methods=['POST'])
@login_required
def upload_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Secure the filename
    filename = secure_filename(file.filename)

    # Create a unique filename
    unique_filename = f"{int(time.time())}_{filename}"

    # Read file data
    pdf_data = file.read()

    # Save the file in GridFS
    pdf_file = fs.put(pdf_data, filename=unique_filename, content_type='application/pdf')

    # Store the file metadata in the collection, associated with the user
    collection.insert_one({
        "filename": unique_filename,
        "file_id": pdf_file,
        "user_id": session['user_id']  # Link file to logged-in user
    })

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    # Find files associated with the logged-in user
    user_files = collection.find({"user_id": session['user_id']}, {"filename": 1, "_id": 0})
    pdf_links = [file["filename"] for file in user_files]

    return render_template("dashboard.html", pdf_links=pdf_links)

# Route to open the PDF in the browser
@app.route('/view/<filename>')
@login_required
def view(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    # Find the file in GridFS, ensuring it belongs to the logged-in user
    file_meta = collection.find_one({"filename": filename, "user_id": session['user_id']})
    if not file_meta:
        abort(403)  # Forbidden

    file = fs.find_one({"filename": filename})
    if file:
        return send_file(BytesIO(file.read()), mimetype='application/pdf')
    else:
        abort(404)  # File not found
# Route to download the PDF
@app.route('/download/<filename>')
@login_required
def download(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    # Find the file in GridFS, ensuring it belongs to the logged-in user
    file_meta = collection.find_one({"filename": filename, "user_id": session['user_id']})
    if not file_meta:
        abort(403)  # Forbidden

    file = fs.find_one({"filename": filename})
    if file:
        return send_file(BytesIO(file.read()), as_attachment=True, download_name=filename, mimetype='application/pdf')
    else:
        abort(404)  # File not found

# Run the Flask app on the dynamic port
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Use environment variable or default to 10000
    app.run(host='0.0.0.0', port=port, debug=True)