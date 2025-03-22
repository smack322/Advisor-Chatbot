# WordPress RAG Implementation with Open Source Components
import os
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download NLTK resources (first-time only)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class WordPressRAGAgent:
    def __init__(self, wordpress_url, model_path="models/llama-2-7b-chat.gguf", embeddings_model="all-MiniLM-L6-v2"):
        """
        Initialize the WordPress RAG agent
        
        Args:
            wordpress_url: Base URL of the WordPress site
            model_path: Path to the local LLM model (GGUF format)
            embeddings_model: HuggingFace embeddings model to use
        """
        self.wordpress_url = wordpress_url
        self.model_path = model_path
        
        # Initialize embeddings
        logger.info(f"Loading embeddings model: {embeddings_model}")
        self.embeddings = HuggingFaceEmbeddings(model_name=embeddings_model)
        
        # Setup text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        # Create directory for vector database if it doesn't exist
        os.makedirs("vector_db", exist_ok=True)
        
        self.vector_db = None
        self.llm = None
        self.qa_chain = None
        
    def scrape_wordpress_site(self):
        """Scrape content from WordPress site"""
        logger.info(f"Starting scrape of WordPress site: {self.wordpress_url}")
        
        # Get the sitemap
        sitemap_url = f"{self.wordpress_url.rstrip('/')}/sitemap.xml"
        try:
            response = requests.get(sitemap_url)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            soup = BeautifulSoup(response.content, 'xml')
            urls = [loc.text for loc in soup.find_all('loc')]
            
            if not urls:
                # Try alternate sitemap location
                sitemap_url = f"{self.wordpress_url.rstrip('/')}/wp-sitemap.xml"
                response = requests.get(sitemap_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'xml')
                urls = [loc.text for loc in soup.find_all('loc')]
        except Exception as e:
            logger.error(f"Error accessing sitemap: {e}")
            # Fallback to crawling from homepage
            urls = [self.wordpress_url]
            
        logger.info(f"Found {len(urls)} URLs to process")
        
        documents = []
        for url in urls:
            try:
                # Skip non-HTML content
                if not url.endswith(('.html', '.htm', '/')) and '.' in url.split('/')[-1]:
                    continue
                    
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script, style, and nav elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                    element.decompose()
                
                # Extract title
                title = soup.title.string if soup.title else ""
                
                # Extract main content (adjust selectors based on your WordPress theme)
                content_selectors = ['article', '.post-content', '.entry-content', 'main', '#content']
                content = ""
                
                for selector in content_selectors:
                    content_element = soup.select_one(selector)
                    if content_element:
                        content = content_element.get_text(separator=' ', strip=True)
                        break
                
                if not content and soup.body:
                    # Fallback to body content
                    content = soup.body.get_text(separator=' ', strip=True)
                
                # Clean the content
                content = re.sub(r'\s+', ' ', content).strip()
                content = re.sub(r'Share this:', '', content)
                
                if content:
                    documents.append({
                        "url": url,
                        "title": title,
                        "content": content
                    })
                    logger.info(f"Scraped: {url}")
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
        
        logger.info(f"Successfully scraped {len(documents)} pages")
        return documents
    
    def process_documents(self, documents):
        """Process scraped documents and create a vector store"""
        logger.info("Processing documents and creating vector store")
        
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc["content"])
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    "url": doc["url"],
                    "title": doc["title"]
                })
        
        if not texts:
            logger.error("No text chunks extracted from documents")
            return False
            
        # Create FAISS vector store
        self.vector_db = FAISS.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        
        # Save the vector store locally
        self.vector_db.save_local("vector_db/wordpress_faiss_index")
        logger.info(f"Created vector store with {len(texts)} chunks")
        return True
    
    def load_model(self):
        """Load the local LLM model"""
        logger.info(f"Loading LLM from {self.model_path}")
        try:
            self.llm = LlamaCpp(
                model_path=self.model_path,
                temperature=0.1,
                max_tokens=2048,
                n_ctx=4096,
                verbose=False
            )
            return True
        except Exception as e:
            logger.error(f"Error loading LLM: {e}")
            return False
    
    def load_vector_store(self):
        """Load existing vector store"""
        try:
            self.vector_db = FAISS.load_local("vector_db/wordpress_faiss_index", self.embeddings)
            logger.info("Loaded existing vector store")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def setup_qa_chain(self):
        """Set up the QA chain for answering questions"""
        if not self.vector_db:
            logger.error("Vector store not initialized")
            return False
            
        if not self.llm:
            logger.error("LLM not initialized")
            return False
            
        retriever = self.vector_db.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        
        logger.info("QA chain setup complete")
        return True
    
    def answer_question(self, question):
        """Answer a question using the RAG system"""
        if not self.qa_chain:
            return "QA system not initialized properly."
            
        try:
            result = self.qa_chain({"query": question})
            
            answer = result["result"]
            sources = []
            
            # Add sources to the answer
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    if doc.metadata["url"] not in sources:
                        sources.append(doc.metadata["url"])
            
            final_answer = f"{answer}\n\nSources:\n"
            for source in sources:
                final_answer += f"- {source}\n"
                
            return final_answer
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"Error processing your question: {str(e)}"
    
    def initialize(self, force_rescrape=False):
        """Initialize the RAG agent"""
        # Check if vector store exists
        if not force_rescrape and os.path.exists("vector_db/wordpress_faiss_index"):
            if self.load_vector_store():
                if self.load_model():
                    return self.setup_qa_chain()
                return False
        
        # Scrape and process if no existing vector store or force_rescrape
        documents = self.scrape_wordpress_site()
        if not documents:
            logger.error("No documents scraped")
            return False
            
        if not self.process_documents(documents):
            return False
            
        if not self.load_model():
            return False
            
        return self.setup_qa_chain()


# Usage example
if __name__ == "__main__":
    # Initialize agent
    agent = WordPressRAGAgent(
        wordpress_url="https://your-wordpress-site.com",
        model_path="models/llama-2-7b-chat.gguf"  # Path to your downloaded LLM
    )
    
    # Initialize the system (scrape website and build vector store)
    if agent.initialize():
        # Example question
        question = "What services does this company offer?"
        answer = agent.answer_question(question)
        print(f"Q: {question}\n\nA: {answer}")
    else:
        print("Failed to initialize the RAG agent")