from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import uuid  # Import uuid for unique identifiers

app = Flask(__name__)

# MongoDB setup with your connection string
client = MongoClient('mongodb+srv://mantissa6789:Mantis2510@cluster0.9ramotn.mongodb.net/caterpillar-hackathon?retryWrites=true&w=majority')
db = client['caterpillar-hackathon']  # Database name
responses_collection = db['responses']  # Collection for storing responses
concerning_responses_collection = db['concerning_responses']  # Collection for concerning responses

# Load the inspection data
with open('inspection_data.json', 'r') as f:
    inspection_data = json.load(f)

# Flatten the data into a list of questions, categorized by type
questions_by_category = {}
for category in inspection_data:
    questions_by_category[category['category']] = category['questions']

# Define the sequence of categories and the questions to be asked
question_sequence = [
    "Header",
    "Tire Information",
    "Battery Information",
    "Exterior Information",
    "Brakes Information",
    "Engine Information",
    "Voice of Customer"
]

# Define conditions for concerning responses
concerning_conditions = ["needs replacement", "bad", "low", "issue", "leak", "rust", "damage"]

def is_concerning(response):
    """Check if the response indicates a concerning condition."""
    response_lower = response.lower()
    return any(condition in response_lower for condition in concerning_conditions)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions', methods=['GET'])
def get_questions():
    questions = []
    for category in question_sequence:
        questions.append({
            'category': category,
            'questions': questions_by_category.get(category, [])
        })
    return jsonify(questions)

@app.route('/submit', methods=['POST'])
def submit_responses():
    responses = request.get_json()  # Expecting an array of objects
    concerning_responses = {}
    all_responses_summary = []

    # Generate a unique identifier for this inspection session
    inspection_id = str(uuid.uuid4())

    # Process each response
    for response in responses:
        question = response['question']
        answer = response['answer']
        
        # Check if the response is concerning
        if is_concerning(answer):
            category = next((cat for cat in question_sequence if question in questions_by_category.get(cat, [])), None)
            if category:
                if category not in concerning_responses:
                    concerning_responses[category] = {}
                concerning_responses[category][question] = answer
        
        # Add to the complete summary
        all_responses_summary.append((question, answer))

    # Save all responses to MongoDB with the inspection ID
    for response in responses:
        response['inspection_id'] = inspection_id  # Add the inspection ID to each response
    responses_collection.insert_many(responses)

    # Save concerning responses to MongoDB
    concerning_responses_collection.insert_one({'inspection_id': inspection_id, 'concerning_responses': concerning_responses})

    # Prepare text for summarization
    summary_text = ""
    
    # Include concerning responses in the summary
    for category, questions in concerning_responses.items():
        summary_text += f"## {category} - Concerning Responses\n\n"
        for question, answer in questions.items():
            summary_text += f"### **Question:** {question}\n\n"
            summary_text += f"**Concerning Response:** {answer}\n\n"
            summary_text += f"This response indicates a potential issue that requires further investigation or action. Please review the details and take appropriate measures to address the concern.\n\n"

    # Add all responses to the summary
    summary_text += "## All Responses\n\n"
    for question, answer in all_responses_summary:
        # Check if the question was concerning
        is_concerning_response = any(question in questions for questions in concerning_responses.values())
        if is_concerning_response:
            summary_text += f"### **Question:** {question}\n\n"
            summary_text += f"**Response:** {answer} *(Concerning)*\n\n"
            summary_text += f"This response suggests a potential problem that should be examined more closely. Please ensure that necessary steps are taken to rectify the situation.\n\n"
        else:
            summary_text += f"### **Question:** {question}\n\n"
            summary_text += f"**Response:** {answer}\n\n"
            summary_text += f"The provided response appears satisfactory. No immediate action is required for this item.\n\n"

    return jsonify({'summary': summary_text})

@app.route('/responses', methods=['GET'])
def get_responses():
    """Retrieve all responses from the database."""
    responses = list(responses_collection.find({}, {'_id': 0}))  # Exclude the MongoDB ObjectId
    return jsonify(responses)

@app.route('/concerning-responses', methods=['GET'])
def get_concerning_responses():
    """Retrieve concerning responses from the database."""
    concerning_responses = list(concerning_responses_collection.find({}, {'_id': 0}))  # Exclude the MongoDB ObjectId
    return jsonify(concerning_responses)

if __name__ == '__main__':
    app.run(debug=True)
