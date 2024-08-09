import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load the inspection data
with open('inspection_data.json', 'r') as f:
    inspection_data = json.load(f)

# Flatten the data into a list of questions
flat_data = []
for category in inspection_data:
    for question in category['questions']:
        flat_data.append({"text": question})

# Prepare data for Sentence Transformers
questions = [item["text"] for item in flat_data]
model = SentenceTransformer('all-MiniLM-L6-v2')
question_embeddings = model.encode(questions, convert_to_tensor=True)

# Initialize the generator
generator_tokenizer = T5Tokenizer.from_pretrained("t5-base")
generator_model = T5ForConditionalGeneration.from_pretrained("t5-base")

def query_rag_model(query):
    # Vectorize the query
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Find nearest neighbors
    distances = util.pytorch_cos_sim(query_embedding, question_embeddings)[0]
    top_indices = np.argsort(distances)[-5:]
    retrieved_texts = [questions[i] for i in top_indices]

    # Generate a response based on the retrieved context
    context = " ".join(retrieved_texts)
    input_text = "answer: " + context
    generator_inputs = generator_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = generator_model.generate(generator_inputs["input_ids"], max_length=150)
    answer = generator_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return answer

def manual_input_loop():
    while True:
        query = input("Enter your question (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        response = query_rag_model(query)
        print("RAG Model Response:", response)

if __name__ == "__main__":
    manual_input_loop()
