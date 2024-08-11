from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import json
import uuid
from urllib.parse import quote_plus
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
import json
import os
import tempfile
import base64
import pyttsx3



app = Flask(__name__)

engine = pyttsx3.init()


# Encode your username and password
username = quote_plus('harishkb20205')
password = quote_plus('Harish@20205')

# Create the connection string with the encoded username and password
client = MongoClient(f'mongodb+srv://{username}:{password}@cat.agry6vb.mongodb.net/Service?retryWrites=true&w=majority')

db = client['Service']  # Database name
responses_collection = db['Data']  # Collection for storing responses
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

        # Create a PDF document
    print(responses)
    data = responses
    pdf_file = "inspection_report.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()

    # Modify the existing Title style
    styles['Title'].fontSize = 24
    styles['Title'].alignment = TA_CENTER
    styles['Title'].spaceAfter = 30

    # Create a list to hold the content
    content = []

    # Add the title
    content.append(Paragraph("Inspection Report", styles['Title']))

    categories = {
        "Header": [
            "Truck Serial Number", "Truck Model", "Inspection ID", "Inspector Name", "Employee ID", 
            "Inspection Date", "Inspection Location", "Geo Coordinates", "Service Meter Hours", 
            "Inspector Signature", "Customer Name", "CAT Customer ID"
        ],
        "Tire Information": [
            "Left Front Pressure", "Right Front Pressure", "Left Front Condition", "Right Front Condition", 
            "Left Rear Pressure", "Right Rear Pressure", "Left Rear Condition", "Right Rear Condition", 
            "Tire Overview", "Tire Images"
        ],
        "Battery Information": [
            "Battery Brand", "Last Replaced", "Battery Voltage", "Water Level", "Visible Damage", 
            "Leakage Signs", "Battery Summary", "Battery Images"
        ],
        "Exterior Information": [
            "Exterior Damage", "Oil Leak", "Exterior Summary", "Exterior Images"
        ],
        "Brakes Information": [
            "Brake Fluid Level", "Front Brakes Condition", "Rear Brakes Condition", "Emergency Brake Status", 
            "Brake System Summary", "Brake Images"
        ],
        "Engine Information": [
            "Engine Damage", "Engine Oil Condition", "Engine Oil Color", "Brake Fluid Condition", 
            "Brake Fluid Color", "Engine Oil Leak", "Engine Summary", "Engine Images"
        ],
        "Voice of Customer": [
            "Customer Feedback", "Vehicle Feedback", "Issues Mentioned", "Customer Images"
        ]
    }

    # Mapping of simplified titles to full questions
    question_mapping = {
        "Truck Serial Number": "What is the Truck Serial Number? (e.g., 7301234, 730EJ73245, 73592849, 735EJBC9723)",
        "Truck Model": "What is the Truck Model? (e.g., 730, 730 EJ, 735, 745)",
        "Inspection ID": "What is the Inspection ID? (Auto-incremented unique number)",
        "Inspector Name": "Who is the Inspector? (Name)",
        "Employee ID": "What is the Inspection Employee ID?",
        "Inspection Date": "When was the Inspection Date & Time?",
        "Inspection Location": "Where was the Location of Inspection?",
        "Geo Coordinates": "What are the Geo Coordinates of Inspection? (Optional, in case of remote location)",
        "Service Meter Hours": "What are the Service Meter Hours (Odometer reading)?",
        "Inspector Signature": "What is the Inspector Signature?",
        "Customer Name": "Who is the Customer/Company Name?",
        "CAT Customer ID": "What is the CAT Customer ID?",
        "Left Front Pressure": "How's the pressure on the left front tire? Is it within the recommended range?",
        "Right Front Pressure": "Can you check the pressure for the right front tire? Let me know if it's looking good.",
        "Left Front Condition": "How would you rate the condition of the left front tire? Is it in good shape, okay, or does it need replacement?",
        "Right Front Condition": "What's the condition of the right front tire? Is it still good, okay, or does it need replacing?",
        "Left Rear Pressure": "How about the pressure on the left rear tire? Is it stable?",
        "Right Rear Pressure": "What's the pressure like on the right rear tire? Any adjustments needed?",
        "Left Rear Condition": "How does the left rear tire look? Is it in good condition, okay, or needs a change?",
        "Right Rear Condition": "What's the status of the right rear tire? Is it in good shape, okay, or needs replacing?",
        "Tire Overview": "Can you provide a brief overview of the tire conditions and pressures?",
        "Tire Images": "Please upload images of each tire in the order mentioned.",
        "Battery Brand": "What brand is the battery? For example, CAT, ABC, XYZ?",
        "Last Replaced": "When was the battery last replaced?",
        "Battery Voltage": "What's the current voltage of the battery? Is it 12V, 13V, or something else?",
        "Water Level": "How's the water level in the battery? Is it good, okay, or low?",
        "Visible Damage": "Is there any visible damage to the battery? If yes, please upload an image.",
        "Leakage Signs": "Are there any signs of leakage or rust on the battery? Yes or no?",
        "Battery Summary": "Can you summarize the battery's condition in a few sentences?",
        "Battery Images": "Please attach images of the battery.",
        "Exterior Damage": "Do you see any rust, dents, or damage on the exterior? If yes, can you provide details and attach images?",
        "Oil Leak": "Is there any oil leak in the suspension area? Yes or no?",
        "Exterior Summary": "Can you provide a summary of the exterior condition?",
        "Exterior Images": "Please attach images of any exterior issues or damage.",
        "Brake Fluid Level": "How's the brake fluid level? Is it good, okay, or low?",
        "Front Brakes Condition": "What's the condition of the front brakes? Are they good, okay, or do they need replacement?",
        "Rear Brakes Condition": "How about the rear brakes? Are they in good condition, okay, or need replacing?",
        "Emergency Brake Status": "What's the status of the emergency brake? Is it good, okay, or low?",
        "Brake System Summary": "Can you summarize the brake system's condition in a few sentences?",
        "Brake Images": "Please upload images related to the brakes.",
        "Engine Damage": "Is there any rust, dent, or damage in the engine area? If yes, please describe and upload images.",
        "Engine Oil Condition": "How's the condition of the engine oil? Is it good or bad?",
        "Engine Oil Color": "What's the color of the engine oil? Is it clean, brown, black, or another color?",
        "Brake Fluid Condition": "How does the brake fluid look? Is it good or bad?",
        "Brake Fluid Color": "What's the color of the brake fluid? Is it clean, brown, black, etc.?",
        "Engine Oil Leak": "Is there any oil leak in the engine? Yes or no?",
        "Engine Summary": "Can you provide a brief summary of the engine condition?",
        "Engine Images": "Please attach images of the engine, especially if there are any issues.",
        "Customer Feedback": "Have there been any comments or feedback from the customer? Please share.",
        "Vehicle Feedback": "What specific feedback has the customer provided about their vehicle?",
        "Issues Mentioned": "Are there any particular issues the customer has mentioned that need addressing?",
        "Customer Images": "If there are any images related to the customer's concerns or feedback, please upload them."
    }

    # Function to add a section to the content
    def add_section(title, data):
        content.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
        content.append(Spacer(1, 0.2 * inch))

        for item in data:
            # Use the question_mapping to get the full question if available, otherwise use the item as is
            full_question = question_mapping.get(item, item)
            answer = next((response['answer'] for response in responses if response['question'] == full_question), "N/A")
            content.append(Paragraph(f"{full_question}: {answer}", styles['Normal']))
            content.append(Spacer(1, 0.1 * inch))


    # Add all sections to the content
    for section_title, questions in categories.items():
        add_section(section_title, questions)

    # Build the PDF
    doc.build(content)

    print(f"PDF generated: {pdf_file}")

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

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    try:
        text = request.json['text']
        is_question = request.json.get('is_question', False)
        
        if not is_question:
            return jsonify({'message': 'Not a question, skipping text-to-speech'}), 200
        
        # Generate speech using pyttsx3
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            engine.save_to_file(text, temp_file.name)
            engine.runAndWait()
            temp_file_path = temp_file.name
        
        # Read the generated audio file
        with open(temp_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Remove temporary file
        os.remove(temp_file_path)
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return jsonify({'audio': f'data:audio/wav;base64,{audio_base64}'})
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        return jsonify({'error': str(e), 'message': 'Text-to-speech conversion failed. Please check your system configuration.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
