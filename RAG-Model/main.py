import json
from transformers import GPT2LMHeadModel, GPT2Tokenizer

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

def summarize_with_gpt2(text):
    """Summarize text using GPT-2."""
    if not text:
        return "No concerning responses found."

    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')

    # Encode and generate summary
    inputs = tokenizer.encode(text, return_tensors='pt', max_length=1024, truncation=True)
    outputs = model.generate(inputs, max_length=100, num_beams=5, early_stopping=True)

    # Decode summary
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary.strip()

def manual_input_loop():
    responses = {}
    concerning_responses = {}

    for category in question_sequence:
        questions = questions_by_category.get(category, [])
        
        for question in questions:
            # Ask the user the question
            print(f"System: {question}")
            
            # Get the user's response
            user_answer = input("Your response: ")

            # Store the user's response
            if category not in responses:
                responses[category] = {}
            responses[category][question] = user_answer

            # Check if the response is concerning and store it
            if is_concerning(user_answer):
                if category not in concerning_responses:
                    concerning_responses[category] = {}
                concerning_responses[category][question] = user_answer

    # Save all responses
    with open('user_responses.json', 'w') as f:
        json.dump(responses, f, indent=4)

    # Save concerning responses
    with open('concerning_responses.json', 'w') as f:
        json.dump(concerning_responses, f, indent=4)

    # Prepare text for summarization
    text_for_summarization = ""
    for category, questions in concerning_responses.items():
        text_for_summarization += f"Category: {category}\n"
        for question, answer in questions.items():
            text_for_summarization += f"Question: {question}\nResponse: {answer}\n"

    # Summarize with GPT-2
    summary = summarize_with_gpt2(text_for_summarization)
    print("\n--- GPT-2 Summarized Concerning Parts ---")
    print(summary)

if __name__ == "__main__":
    manual_input_loop()