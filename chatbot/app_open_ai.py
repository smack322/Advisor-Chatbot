import streamlit as st
import numpy as np
import faiss
import json
from openai import OpenAI
from sentence_transformers import SentenceTransformer

OPEAN_AI_KEY = ""
# Initialize the OpenAI client
client = OpenAI(api_key=OPEN_AI_KEY)

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the FAISS index and metadata
index = faiss.read_index("vector_index.faiss")
with open("metadata.json", "r") as f:
    metadata = json.load(f)

# Function to query the FAISS index
def query_faiss(query_text, top_k=5):
    query_embedding = model.encode(query_text)
    distances, indices = index.search(np.array([query_embedding]), top_k)
    results = []
    for i in range(top_k):
        results.append({
            "filename": metadata[indices[0][i]]["filename"],
            "text": metadata[indices[0][i]]["text"],
            "distance": distances[0][i]
        })
    return results

# Function to query OpenAI
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" for faster responses
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to combine FAISS and OpenAI
def ask_question(query_text):
    # Step 1: Query FAISS for relevant documents
    faiss_results = query_faiss(query_text)
    context = "\n\n".join([result["text"] for result in faiss_results])

    # Step 2: Create a prompt for OpenAI
    prompt = f"""You are a knowledgeable and friendly AI assistant for a university. Your role is to help students, advisors, and administrators by providing accurate and detailed answers to their questions about university classes, technologies, and program requirements.

    ### Instructions:
    1. Use the following context to answer the question. If the context is insufficient, provide a general but accurate response.
    2. Be concise but thorough in your answers.
    3. If the question is unclear, ask for clarification.
    4. For program requirements, list specific courses or steps if available in the context.
    5. For technology-related questions, provide practical advice or resources.
    6. If you cannot find relevant information, politely inform the user and suggest contacting the relevant department.

    ### Context:
    {context}

    ### Question:
    {query_text}

    ### Answer:
    """

    # Step 3: Query OpenAI with the prompt
    response = query_openai(prompt)
    return response, faiss_results

# Streamlit UI
st.title("University Class and Program Advisor")
st.write("Ask questions about university classes and programs.")

# Input box for user query
query_text = st.text_input("Enter your question:")

# Button to submit the query
if st.button("Submit"):
    if query_text:
        with st.spinner("Searching for answers..."):
            response, faiss_results = ask_question(query_text)
        st.success("Response:")
        st.write(response)

        # Display retrieved documents
        st.subheader("Retrieved Documents:")
        for result in faiss_results:
            st.write(f"**{result['filename']}**")
            st.write(result["text"])
            st.write(f"**Distance**: {result['distance']}")
            st.write("---")
    else:
        st.warning("Please enter a question.")