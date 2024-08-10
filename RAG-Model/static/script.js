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
let speakMode = false; // Track Speak Mode status
let listenMode = false; // Track Listening Mode status

// Fetch questions from the backend
fetch('/questions')
  .then(response => response.json())
  .then(data => {
    console.log(data); // Log the fetched data
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
  promptContainer.scrollTop = promptContainer.scrollHeight; // Scroll to the bottom
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
    textToSpeech(greetings[randomIndex]); // Convert greeting to speech
  }
}

function textToSpeech(text) {
  const speech = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(speech);
}

function populateCarousel() {
  categories.forEach((category, index) => {
    const carouselItem = document.createElement('div');
    carouselItem.className = 'carousel-item' + (index === 0 ? ' active' : '');

    const categoryHeader = document.createElement('h3');
    categoryHeader.textContent = category.category;
    categoryHeader.className = 'text-center'; // Center the header
    carouselItem.appendChild(categoryHeader);

    const questionContainer = document.createElement('div');
    questionContainer.id = `questions-${index}`;
    category.questions.forEach((question, questionIndex) => {
      const questionElement = document.createElement('p');
      questionElement.textContent = question;
      questionElement.style.display = 'none'; // Hide questions initially
      questionElement.dataset.imageUpload = category.imageUpload[questionIndex]; // Store image upload flag
      questionContainer.appendChild(questionElement);
    });
    carouselItem.appendChild(questionContainer);
    questionsContainer.appendChild(carouselItem);
  });
}

function askNextQuestion() {
  if (currentCategoryIndex < categories.length) {
    const questions = categories[currentCategoryIndex].questions;
    const imageUploadFlags = categories[currentCategoryIndex].imageUpload;

    if (currentQuestionIndex < questions.length) {
      const question = questions[currentQuestionIndex];
      const questionVariations = [
        `📝 Alright, let's move on to the next question. ${question}`,
        `📝 Great, now for the next one: ${question}`,
        `📝 Awesome, here's the next question: ${question}`
      ];
      const randomIndex = Math.floor(Math.random() * questionVariations.length);
      appendMessage(questionVariations[randomIndex], 'bot');
      if (speakMode) {
        textToSpeech(questionVariations[randomIndex]); // Convert question to speech if in speak mode
      }
      userInput.focus();

      // Show image upload section if needed
      if (imageUploadFlags[currentQuestionIndex]) {
        showImageUploadSection();
      } else {
        hideImageUploadSection();
      }
    } else {
      // Move to the next category
      currentCategoryIndex++;
      currentQuestionIndex = 0; // Reset question index for the new category
      if (currentCategoryIndex < categories.length) {
        // Move to the next carousel slide
        $('#inspectionCarousel').carousel(currentCategoryIndex);
        const categoryTransitions = [
          "➡️ Alright, let's move on to the next category!",
          "➡️ Great job! Now, let's take a look at the next section.",
          "➡️ Awesome, we're making progress. Time for the next category."
        ];
        const randomIndex = Math.floor(Math.random() * categoryTransitions.length);
        appendMessage(categoryTransitions[randomIndex], 'bot');
        if (speakMode) {
          textToSpeech(categoryTransitions[randomIndex]); // Convert transition to speech if in speak mode
        }
        askNextQuestion(); // Ask the next question in the new category
      } else {
        // All questions have been answered
        submitResponses(); // Submit all collected responses
      }
    }
  } else {
    // All questions have been answered
    submitResponses(); // Submit all collected responses
  }
}

// Previous and Next controls
$('.carousel-control-prev').on('click', function() {
  appendMessage("🔄 Did you miss something here?", 'bot');
});

$('.carousel-control-next').on('click', function() {
  appendMessage("🔄 Did you complete the previous section?", 'bot');
});

// Speech recognition setup
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.continuous = false; // Stop after one result
recognition.interimResults = false; // No interim results

// Start speech recognition when user clicks the record button
recordButton.addEventListener('click', () => {
  if (listenMode) {
    recognition.start();
    appendMessage("🎤 Listening for your voice input...", 'bot');
  } else {
    appendMessage("🔇 Listening mode is off. Please enable it to use voice input.", 'bot');
  }
});

// Handle the result from speech recognition
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  appendMessage(`🗣️ You said: ${transcript}`, 'user');
  processAnswer(transcript);
};

// Handle errors
recognition.onerror = (event) => {
  appendMessage(`❌ Error occurred in recognition: ${event.error}`, 'bot');
};

// Speak the current question when the speak button is clicked
speakButton.addEventListener('click', () => {
  const question = categories[currentCategoryIndex].questions[currentQuestionIndex];
  if (speakMode) {
    textToSpeech(question); // Speak the current question only if in speak mode
  } else {
    appendMessage("🔇 Speak mode is off. Please enable it to hear the questions.", 'bot');
  }
});

// Handle the submit button click
submitButton.addEventListener('click', () => {
  const answer = userInput.value.trim();
  if (answer) {
    processAnswer(answer);
  }
});

// Process the answer and move to the next question
function processAnswer(answer) {
  const userResponses = [
    "✅ Got it, thanks for your response.",
    "✅ Awesome, thanks for sharing your thoughts.",
    "✅ Great, I appreciate you taking the time to answer."
  ];
  const randomIndex = Math.floor(Math.random() * userResponses.length);
  appendMessage(userResponses[randomIndex], 'bot');
  appendMessage(`💬 Your answer: ${answer}`, 'user'); // Display user input in chat
  userInput.value = ''; // Clear input

  // Store the response
  const question = categories[currentCategoryIndex].questions[currentQuestionIndex];
  responses.push({ question, answer });

  currentQuestionIndex++; // Move to the next question
  askNextQuestion(); // Ask the next question
}

// Toggle Speak Mode
speakModeToggle.addEventListener('change', () => {
  speakMode = speakModeToggle.checked;
  const status = speakMode ? 'ON' : 'OFF';
  appendMessage(`🔊 Speak Mode is now ${status}`, 'bot');
});

// Toggle Listening Mode
listenModeToggle.addEventListener('change', () => {
  listenMode = listenModeToggle.checked;
  const status = listenMode ? 'ON' : 'OFF';
  appendMessage(`🎧 Listening Mode is now ${status}`, 'bot');
});

function showImageUploadSection() {
  imageUploadSection.style.display = 'block';
}

function hideImageUploadSection() {
  imageUploadSection.style.display = 'none';
}

// Submit all responses at once
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
      displaySummary(data.summary);
      // Disable input and button after submission
      userInput.disabled = true;
      submitButton.disabled = true;
    });
}

// Display the summary of responses
function displaySummary(summary) {
  summaryContainer.innerHTML = ''; // Clear previous summary

  const summaryHeader = document.createElement('h3');
  summaryHeader.textContent = "📋 Inspection Summary";
  summaryContainer.appendChild(summaryHeader);

  const summaryText = document.createElement('div'); // Use div to allow HTML content
  summaryText.innerHTML = marked.parse(summary); // Use marked.js to render Markdown
  summaryContainer.appendChild(summaryText);

  // Add confirmation buttons
  const buttonGroup = document.createElement('div');
  buttonGroup.className = 'btn-group mt-3';

  const confirmButton = document.createElement('button');
  confirmButton.textContent = "👍 Okay";
  confirmButton.className = "btn btn-success";
  confirmButton.addEventListener('click', () => {
    appendMessage("🙌 Thank you for confirming the inspection details.", 'bot');
    // Optionally, you can redirect or reset the form here
  });

  const modifyButton = document.createElement('button');
  modifyButton.textContent = "✏️ Not Okay";
  modifyButton.className = "btn btn-danger";
  modifyButton.addEventListener('click', () => {
    appendMessage("🛠️ Let's modify the responses. Please specify what needs to be changed.", 'bot');
    // Logic to modify responses can be implemented here
  });

  buttonGroup.appendChild(confirmButton);
  buttonGroup.appendChild(modifyButton);
  summaryContainer.appendChild(buttonGroup);
}
