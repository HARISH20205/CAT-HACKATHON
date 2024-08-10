const questionsContainer = document.getElementById('questions-carousel-inner');
const userInput = document.getElementById('user-input');
const submitButton = document.getElementById('submit-button');
const speakButton = document.getElementById('speak-button');
const recordButton = document.getElementById('record-button');
const summaryContainer = document.getElementById('summary-container');
const promptContainer = document.getElementById('prompt-container').querySelector('.card-body');
const speakModeToggle = document.getElementById('speak-mode-toggle');
const listenModeToggle = document.getElementById('listen-mode-toggle');
const imageUploadSection = document.getElementById('image-upload-section');

let currentCategoryIndex = 0;
let currentQuestionIndex = 0;
let responses = [];
let categories = [];
let speakMode = false;
let listenMode = false;
let mediaRecorder;
let audioChunks = [];

// Fetch questions from the backend
fetch('/questions')
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (!Array.isArray(data)) {
      throw new Error('Expected an array of categories');
    }
    categories = data;
    populateCarousel();
    askGreeting();
  })
  .catch(error => {
    console.error('Error fetching questions:', error);
    appendMessage('Oops, there seems to be an issue fetching the questions. Please try again later.', 'bot');
  });

function appendMessage(message, sender) {
  const messageElement = document.createElement('div');
  messageElement.className = sender === 'bot' ? 'bot-message' : 'user-message';
  messageElement.innerHTML = sender === 'bot' ? `<i class="fas fa-robot"></i> ${message}` : `${message} <i class="fas fa-user"></i>`;
  promptContainer.appendChild(messageElement);
  promptContainer.scrollTop = promptContainer.scrollHeight;
}

function askGreeting() {
  const greetings = [
    "👋 Hi there! Let's start the inspection. Please respond with 'Hi' or 'Hello' to proceed.",
    "👋 Hey, thanks for joining! Let's get started. Respond with 'Hi' or 'Hello'.",
    "👋 Greetings! I'm excited to assist you with the inspection. Say 'Hi' or 'Hello' to begin."
  ];
  const randomIndex = Math.floor(Math.random() * greetings.length);
  appendMessage(greetings[randomIndex], 'bot');
  if (speakMode) {
    speakQuestion(greetings[randomIndex]);
  }
}

function populateCarousel() {
  categories.forEach((category, index) => {
    const carouselItem = document.createElement('div');
    carouselItem.className = 'carousel-item' + (index === 0 ? ' active' : '');

    const categoryHeader = document.createElement('h3');
    categoryHeader.textContent = category.category;
    categoryHeader.className = 'text-center';
    carouselItem.appendChild(categoryHeader);

    const questionContainer = document.createElement('div');
    questionContainer.id = `questions-${index}`;
    
    if (category.questions && Array.isArray(category.questions)) {
      category.questions.forEach((question, questionIndex) => {
        const questionElement = document.createElement('p');
        questionElement.textContent = question;
        questionElement.style.display = 'none';
        questionElement.dataset.imageUpload = category.imageUpload ? category.imageUpload[questionIndex] : false;
        questionContainer.appendChild(questionElement);
      });
    } else {
      console.warn(`No questions found for category: ${category.category}`);
    }
    
    carouselItem.appendChild(questionContainer);
    questionsContainer.appendChild(carouselItem);
  });
}

function askNextQuestion() {
  if (currentCategoryIndex < categories.length) {
    const questions = categories[currentCategoryIndex].questions;
    const imageUploadFlags = categories[currentCategoryIndex].imageUpload || [];

    if (currentQuestionIndex < questions.length) {
      const question = questions[currentQuestionIndex];
      const questionVariations = [
        `📝 Alright, let's move on to the next question. ${question}`,
        `📝 Great, now for the next one: ${question}`,
        `📝 Awesome, here's the next question: ${question}`
      ];
      const randomIndex = Math.floor(Math.random() * questionVariations.length);
      const questionText = questionVariations[randomIndex];
      
      appendMessage(questionText, 'bot');
      
      if (speakMode) {
        speakQuestion(questionText);
      }
      
      userInput.focus();

      if (imageUploadFlags[currentQuestionIndex]) {
        showImageUploadSection();
      } else {
        hideImageUploadSection();
      }
    } else {
      currentCategoryIndex++;
      currentQuestionIndex = 0;
      if (currentCategoryIndex < categories.length) {
        $('#inspectionCarousel').carousel(currentCategoryIndex);
        const categoryTransitions = [
          "➡️ Alright, let's move on to the next category!",
          "➡️ Great job! Now, let's take a look at the next section.",
          "➡️ Awesome, we're making progress. Time for the next category."
        ];
        const randomIndex = Math.floor(Math.random() * categoryTransitions.length);
        appendMessage(categoryTransitions[randomIndex], 'bot');
        if (speakMode) {
          speakQuestion(categoryTransitions[randomIndex]);
        }
        askNextQuestion();
      } else {
        submitResponses();
      }
    }
  } else {
    submitResponses();
  }
}

function speakQuestion(questionText) {
  fetch('/text-to-speech', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      text: questionText,
      is_question: true
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.audio) {
      const audio = new Audio(data.audio);
      audio.play();
    } else if (data.message) {
      console.log(data.message); // Log if it's not a question
    }
  })
  .catch(error => {
    console.error('Error in text-to-speech:', error);
    appendMessage('🔇 Sorry, I couldn\'t speak that out loud. There was an error with the text-to-speech service.', 'bot');
  });
}

function processAnswer(answer) {
  const userResponses = [
    "✅ Got it, thanks for your response.",
    "✅ Awesome, thanks for sharing your thoughts.",
    "✅ Great, I appreciate you taking the time to answer."
  ];
  const randomIndex = Math.floor(Math.random() * userResponses.length);
  appendMessage(userResponses[randomIndex], 'bot');
  appendMessage(`💬 Your answer: ${answer}`, 'user');
  userInput.value = '';

  const question = categories[currentCategoryIndex].questions[currentQuestionIndex];
  responses.push({ question, answer });

  currentQuestionIndex++;
  askNextQuestion();
}

function submitResponses() {
  fetch('/submit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(responses)
  })
  .then(response => response.json())
  .then(data => {
    appendMessage("✅ All questions have been answered! Thank you.", 'bot');
    if (speakMode) {
      speakQuestion("All questions have been answered! Thank you.");
    }
    displaySummary(data.summary);
  })
  .catch(error => {
    console.error('Error submitting responses:', error);
    appendMessage('❌ Oops, something went wrong while submitting your responses. Please try again.', 'bot');
  });
}

function showImageUploadSection() {
  imageUploadSection.style.display = 'block';
}

function hideImageUploadSection() {
  imageUploadSection.style.display = 'none';
}

function displaySummary(summary) {
  summaryContainer.innerHTML = marked.parse(summary);
}

// Event Listeners
submitButton.addEventListener('click', () => {
  const answer = userInput.value.trim();
  if (answer) {
    processAnswer(answer);
  }
});

speakButton.addEventListener('click', () => {
  if (currentCategoryIndex < categories.length && currentQuestionIndex < categories[currentCategoryIndex].questions.length) {
    const question = categories[currentCategoryIndex].questions[currentQuestionIndex];
    if (speakMode) {
      speakQuestion(question);
    } else {
      appendMessage("🔇 Speak mode is off. Please enable it to hear the questions.", 'bot');
    }
  } else {
    appendMessage("❗ No current question to speak.", 'bot');
  }
});

recordButton.addEventListener('click', () => {
  if (listenMode) {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      appendMessage("🎤 Processing your voice input...", 'bot');
    } else {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          mediaRecorder = new MediaRecorder(stream);
          audioChunks = [];

          mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
          });

          mediaRecorder.addEventListener("stop", () => {
            const audioBlob = new Blob(audioChunks);
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = function() {
              const base64Audio = reader.result;
              speechToText(base64Audio);
            }
          });

          mediaRecorder.start();
          appendMessage("🎤 Listening for your voice input...", 'bot');
        });
    }
  } else {
    appendMessage("🔇 Listening mode is off. Please enable it to use voice input.", 'bot');
  }
});

speakModeToggle.addEventListener('change', () => {
  speakMode = speakModeToggle.checked;
  if (speakMode) {
    appendMessage("🔊 Speak mode enabled. I will read the questions aloud.", 'bot');
  } else {
    appendMessage("🔇 Speak mode disabled.", 'bot');
  }
});

listenModeToggle.addEventListener('change', () => {
  listenMode = listenModeToggle.checked;
  if (listenMode) {
    appendMessage("🎧 Listen mode enabled. I will listen for your voice input.", 'bot');
  } else {
    appendMessage("🔇 Listen mode disabled.", 'bot');
  }
});

$('.carousel-control-prev').on('click', function() {
  appendMessage("🔄 Did you miss something here?", 'bot');
});

$('.carousel-control-next').on('click', function() {
  appendMessage("🔄 Did you complete the previous section?", 'bot');
});

function speechToText(audioData) {
  fetch('/speech-to-text', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ audio: audioData })
  })
  .then(response => response.json())
  .then(data => {
    appendMessage(`🗣️ You said: ${data.text}`, 'user');
    processAnswer(data.text);
  })
  .catch(error => {
    console.error('Error in speech recognition:', error);
    appendMessage('❌ Sorry, I couldn\'t understand that. Could you please try again?', 'bot');
  });
}

// Initialize the chatbot
document.addEventListener('DOMContentLoaded', () => {
  appendMessage("Welcome to the Inspection Chatbot! How can I assist you today?", 'bot');
  if (speakMode) {
    speakQuestion("Welcome to the Inspection Chatbot! How can I assist you today?");
  }
});