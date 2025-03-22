import numpy as np
import faiss
import json
import requests
from sentence_transformers import SentenceTransformer

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Use a Hugging Face model

# Load the FAISS index and metadata
index = faiss.read_index("vector_index.faiss")
with open("metadata.json", "r") as f:
    metadata = json.load(f)

# Function to query the FAISS index
def query_faiss(query_text, top_k=5):
    # Generate embedding for the query
    query_embedding = model.encode(query_text)
    
    # Search the FAISS index
    distances, indices = index.search(np.array([query_embedding]), top_k)
    
    # Retrieve results
    results = []
    for i in range(top_k):
        results.append({
            "filename": metadata[indices[0][i]]["filename"],
            "text": metadata[indices[0][i]]["text"],
            "distance": distances[0][i]
        })
    return results

# Function to query Ollama
def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama2",  # Use the Ollama model name here
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Combine FAISS and Ollama
def ask_question(query_text):
    # Step 1: Query FAISS for relevant documents
    faiss_results = query_faiss(query_text)
    context = "\n\n".join([result["text"] for result in faiss_results])

    # Step 2: Create a prompt for Ollama
    prompt = f"""You are a helpful assistant. Use the following context to answer the question:
    
    Context:
    {context}

    Question:
    {query_text}

    Answer:
    """

    # Step 3: Query Ollama with the prompt
    response = query_ollama(prompt)
    return response

# Example usage
query_text = "How many AI classes does PSU offer?"
response = ask_question(query_text)
print("Response:", response)