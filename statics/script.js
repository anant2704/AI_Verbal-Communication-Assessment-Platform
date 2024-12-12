const startButton = document.getElementById('start');
const nextButton = document.getElementById('next');
const finishButton = document.getElementById('finish');
const questionElem = document.getElementById('question');
const transcriptionElem = document.getElementById('transcription');
const webcamElem = document.getElementById('webcam');

let questionIndex = 0;
let questions = [
    "What motivates you to perform well?",
    "Can you describe a time when you faced a challenge and overcame it?",
    "How do you handle constructive criticism?"
];

let recognition;

function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            transcriptionElem.value = transcript;
        };
    } else {
        alert("Speech recognition is not supported in your browser.");
    }
}

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then((stream) => {
            webcamElem.srcObject = stream;
        })
        .catch((error) => {
            console.error("Error accessing webcam:", error);
        });
}

startButton.onclick = () => {
    startWebcam();
    initializeSpeechRecognition();
    questionElem.textContent = questions[questionIndex];
    recognition.start();
    nextButton.disabled = false;
    startButton.disabled = true;
};

nextButton.onclick = () => {
    questionIndex++;
    if (questionIndex < questions.length) {
        questionElem.textContent = questions[questionIndex];
        transcriptionElem.value = "";
    }
    if (questionIndex === questions.length - 1) {
        nextButton.disabled = true;
        finishButton.disabled = false;
    }
};

finishButton.onclick = () => {
    recognition.stop();
    alert("Test completed! Generating feedback...");
    fetch('/submit-feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: transcriptionElem.value })
    })
        .then(response => response.json())
        .then(data => {
            const feedback = data.feedback;
            alert(`Feedback: ${feedback}`);
        });
};
