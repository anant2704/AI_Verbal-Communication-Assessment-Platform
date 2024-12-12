# AI Verbal Communication Assessment Platform

## Overview
The AI Verbal Communication Assessment Platform is a web-based application designed to evaluate and improve verbal communication skills. Users can record videos, receive detailed assessments, and download comprehensive feedback reports. The prototype was built using free and open-source tools to ensure accessibility and cost-efficiency.

Website: [AI Verbal Communication Assessment Platform](https://ai-verbal-communication-assessment.onrender.com/)

---

## Features
- *Video Recording and Playback*: Allows users to record videos and review them before submission.
- *Speech-to-Text Conversion*: Transcribes spoken content into text using open-source tools.
- *Grammatical Error Highlighting*: Identifies and scores grammatical errors with contextual feedback.
- *Pronunciation and Fluency Analysis*:
  - Pronunciation clarity scoring.
  - Fluency evaluation based on pauses, speech rate, and continuity.
- *Comprehensive Scoring*: Provides an aggregated score based on grammar, pronunciation, and fluency.
- *Feedback and Report Generation*: Offers actionable tips for improvement and generates downloadable assessment reports.

---

## Technology Stack
- *Frontend*:
  - HTML, CSS, JavaScript
  - React.js (for responsive UI)
- *Backend*:
  - Python (Flask/Django)
  - REST API integration
- *AI Models*:
  - Llama.ai (free-tier services for NLP)
  - Open-source speech-to-text tools
- *Hosting*:
  - Render.com (free tier for prototyping)

---

## Installation
### Prerequisites
- Python 3.8+
- Node.js 14+

### Steps
1. *Clone the Repository*:
   bash
   git clone https://github.com/your-repository/ai-verbal-assessment.git
   cd ai-verbal-assessment
   
2. *Install Backend Dependencies*:
   bash
   pip install -r requirements.txt
   
3. *Install Frontend Dependencies*:
   bash
   cd frontend
   npm install
   
4. *Run the Application*:
   - Start the backend server:
     bash
     python app.py
     
   - Start the frontend development server:
     bash
     cd frontend
     npm start
     

---

## Usage
1. Visit the platform URL: [AI Verbal Communication Assessment Platform](https://ai-verbal-communication-assessment.onrender.com/)
2. Record and submit a video for analysis.
3. View feedback, download the assessment report, and improve your communication skills.

---

## Future Enhancements
- Offline capabilities for areas with limited connectivity.
- Advanced pronunciation analysis using localized datasets.
- Integration of additional free and open-source tools for further cost-efficiency.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
- **Llama model 3.2-3b: **: For providing free-tier NLP services.
- *Open-source Speech-to-Text Tools*: Ensuring accurate transcription.
- *Render.com*: Free hosting for the prototype.
