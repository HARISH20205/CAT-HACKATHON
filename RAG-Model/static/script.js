const questionsContainer = document.getElementById('questions-container');
const submitButton = document.getElementById('submit-button');
const summaryContainer = document.getElementById('summary-container');

fetch('/questions')
  .then(response => response.json())
  .then(questions => {
        questions.forEach(question => {
            const questionElement = document.createElement('p');
            questionElement.textContent = question;
            const inputElement = document.createElement('input');
            inputElement.type = 'text';
            inputElement.id = question;
            questionsContainer.appendChild(questionElement);
            questionsContainer.appendChild(inputElement);
        });
    });

submitButton.addEventListener('click', () => {
    const responses = {};
    const inputElements = document.querySelectorAll('input');
    inputElements.forEach(inputElement => {
        responses[inputElement.id] = inputElement.value;
    });

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(responses)
    })
   .then(response => response.json())
   .then(data => {
        const summaryElement = document.createElement('p');
        summaryElement.textContent = data.summary;
        summaryContainer.appendChild(summaryElement);
    });
});