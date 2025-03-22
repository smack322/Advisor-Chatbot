import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load a pre-trained model for generating embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index
dimension = 384  # Dimension of the embeddings (all-MiniLM-L6-v2 outputs 384-dimensional vectors)
index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search

# Function to extract text from JSON
def extract_text_from_json(json_data):
    text = ""
    if "paragraphs" in json_data:
        text += " ".join(json_data["paragraphs"])
    if "headings" in json_data:
        for key, value in json_data["headings"].items():
            text += f" {value}"
    if "lists" in json_data:
        for lst in json_data["lists"]:
            text += " ".join(lst)
    return text

# Directory containing JSON files
json_dir = "../scripts/scraped_data"

# List to store embeddings and corresponding metadata
embeddings = []
metadata = []

# Process each JSON file
for filename in os.listdir(json_dir):
    if filename.endswith(".json"):
        with open(os.path.join(json_dir, filename), "r") as f:
            data = json.load(f)
            text = extract_text_from_json(data)
            embedding = model.encode(text)  # Generate embedding
            embeddings.append(embedding)
            metadata.append({
                "filename": filename,
                "text": text
            })

# Convert embeddings to a numpy array
embeddings = np.array(embeddings)

# Add embeddings to the FAISS index
index.add(embeddings)

# Save the FAISS index and metadata
faiss.write_index(index, "vector_index.faiss")
with open("metadata.json", "w") as f:
    json.dump(metadata, f)

print("Data has been vectorized and stored in FAISS.")