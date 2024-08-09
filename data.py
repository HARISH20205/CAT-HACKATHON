import json
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Simulated Knowledge Base
knowledge_base = {
    "tire_information": {
        "left_front": {
            "pressure": "32 PSI",
            "condition": "good"
        },
        "right_front": {
            "pressure": "31 PSI",
            "condition": "good"
        },
        "left_rear": {
            "pressure": "30 PSI",
            "condition": "okay"
        },
        "right_rear": {
            "pressure": "29 PSI",
            "condition": "needs replacement"
        }
    },
    "battery_information": {
        "brand": "CAT",
        "last_replaced": "2023-08-01",
        "current_voltage": "12.8V",
        "water_level": "good",
        "damage": "no",
        "leakage_or_rust": "no"
    },
    "exterior_information": {
        "rust_or_damage": "no",
        "oil_leak_in_suspension_area": "no",
        "detailed_condition": "The exterior is in good condition with no visible rust, dents, or damage."
    },
    "brakes_information": {
        "brake_fluid_level": "good",
        "front_brakes_condition": "good",
        "rear_brakes_condition": "okay",
        "emergency_brake_status": "good"
    },
    "engine_information": {
        "rust_or_damage": "no",
        "engine_oil_condition": "good",
        "engine_oil_color": "clean",
        "brake_fluid_condition": "good",
        "brake_fluid_color": "clean",
        "oil_leak": "no",
        "detailed_condition": "The engine is in good condition with no signs of rust, damage, or oil leaks."
    },
    "voice_of_customer": {
        "comments": "Customer mentioned a slight noise coming from the front brakes.",
        "feedback": "The customer is concerned about the brakes and wants them checked.",
        "specific_issues": "Brakes may need inspection due to noise."
    }
}

# Simple Retriever Function
def retrieve_info(question, knowledge_base):
    question = question.lower()  # Convert to lowercase for matching
    
    if "tire" in question:
        return json.dumps(knowledge_base["tire_information"], indent=4)
    elif "battery" in question:
        return json.dumps(knowledge_base["battery_information"], indent=4)
    elif "exterior" in question:
        return json.dumps(knowledge_base["exterior_information"], indent=4)
    elif "brake" in question:
        return json.dumps(knowledge_base["brakes_information"], indent=4)
    elif "engine" in question:
        return json.dumps(knowledge_base["engine_information"], indent=4)
    elif "customer" in question:
        return json.dumps(knowledge_base["voice_of_customer"], indent=4)
    else:
        return "No relevant information found in the knowledge base."

# Example question
question = "How’s the pressure on the left front tire?"

# Retrieve information
retrieved_info = retrieve_info(question, knowledge_base)
print("Retrieved Info:", retrieved_info)

# Load GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Combine the retrieved info with the question
input_text = question + "\nKnowledge Base Info:\n" + retrieved_info

# Tokenize the input
inputs = tokenizer.encode(input_text, return_tensors="pt")

# Generate a response
outputs = model.generate(inputs, max_length=150, do_sample=True, top_p=0.95, top_k=60)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\nGenerated Response:", response)
