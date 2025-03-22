import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from docx import Document

def extract_text_from_docx(file_path):
    """Extract text from a .docx file."""
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can use other models as well

def generate_embeddings(text):
    """Generate embeddings for the given text."""
    return model.encode(text)


# Initialize FAISS index
dimension = 384  # Dimension of the embeddings (all-MiniLM-L6-v2 outputs 384-dimensional vectors)
index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity search

# List to store embeddings and corresponding metadata
embeddings = []
metadata = []

# Directory containing Word documents
docx_dir = "../documents"

# Process each Word document
for filename in os.listdir(docx_dir):
    if filename.endswith(".docx") or filename.endswith(".doc"):
        file_path = os.path.join(docx_dir, filename)
        text = extract_text_from_docx(file_path)
        embedding = generate_embeddings(text)  # Generate embedding
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

print("Word documents have been vectorized and stored in FAISS.")