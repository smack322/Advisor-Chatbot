import os
import json
import numpy as np
import faiss
from docx import Document  # Ensure this is from the correct library
from sentence_transformers import SentenceTransformer
from win32com import client as wc  # For .doc files on Windows

# Load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index
dimension = 384
index = faiss.IndexFlatL2(dimension)

# Function to extract text from .docx files
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

# Function to extract text from .doc files (Windows only)
def extract_text_from_doc(file_path):
    word = wc.Dispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Open(file_path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text

# Directory containing Word documents
docx_dir = "../documents"

# List to store embeddings and corresponding metadata
embeddings = []
metadata = []

# Process each file in the directory
for filename in os.listdir(docx_dir):
    file_path = os.path.join(docx_dir, filename)
    if filename.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif filename.endswith(".doc"):
        text = extract_text_from_doc(file_path)
    else:
        continue  # Skip non-Word files

    # Generate embedding and store metadata
    embedding = model.encode(text)
    embeddings.append(embedding)
    metadata.append({
        "filename": filename,
        "text": text
    })

# Convert embeddings to a numpy array and add to FAISS
embeddings = np.array(embeddings)
index.add(embeddings)

# Save the FAISS index and metadata
faiss.write_index(index, "vector_index.faiss")
with open("metadata.json", "w") as f:
    json.dump(metadata, f)

print("Word documents (.docx and .doc) have been vectorized and stored in FAISS.")