"""
Document Analyzer Module
Provides RAG (Retrieval-Augmented Generation) capabilities for document analysis and Q&A.
"""

import os
import re
from datetime import datetime
from typing import List
import chromadb
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from pypdf import PdfReader
from config import GEMINI_API_KEY

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function using Google's Gemini model for document analysis.
    """
    
    def __call__(self, input: Documents) -> Embeddings:
        """
        Generates embeddings for input documents using Gemini.
        
        Args:
            input (Documents): Input documents to embed
            
        Returns:
            Embeddings: Generated embeddings
        """
        try:
            model = "models/embedding-001"
            title = "Custom query"
            embeddings = genai.embed_content(
                model=model,
                content=input,
                task_type="retrieval_document",
                title=title
            )
            return embeddings["embedding"]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []


def load_pdf(file_path):
    """
    Loads and extracts text from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return ""


def split_text(text: str):
    """
    Splits text into chunks based on delimiters for better processing.
    
    Args:
        text (str): Input text to split
        
    Returns:
        List[str]: List of text chunks
    """
    try:
        split_text_chunks = re.split(r'(\n \n)', text)
        return [chunk for chunk in split_text_chunks if chunk != ""]
    except Exception as e:
        print(f"Error splitting text: {e}")
        return [text]


def create_chroma_db(documents: List, path: str):
    """
    Creates a ChromaDB database with the provided documents.
    
    Args:
        documents (List): List of documents to add to the database
        path (str): Path where the database should be stored
        
    Returns:
        tuple: (database, database_name)
    """
    try:
        name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        chroma_client = chromadb.PersistentClient(path=path)
        db = chroma_client.create_collection(
            name=name, 
            embedding_function=GeminiEmbeddingFunction()
        )

        for i, doc in enumerate(documents):
            db.add(documents=[doc], ids=[str(i)])

        return db, name
    except Exception as e:
        print(f"Error creating ChromaDB: {e}")
        return None, None


def load_chroma_collection(path, name):
    """
    Loads an existing ChromaDB collection.
    
    Args:
        path (str): Path to the database
        name (str): Name of the collection to load
        
    Returns:
        Collection: Loaded ChromaDB collection
    """
    try:
        chroma_client = chromadb.PersistentClient(path=path)
        return chroma_client.get_collection(
            name=name, 
            embedding_function=GeminiEmbeddingFunction()
        )
    except Exception as e:
        print(f"Error loading ChromaDB collection: {e}")
        return None


def get_relevant_passage(query, db, n_results):
    """
    Retrieves the most relevant passage from the database for a given query.
    
    Args:
        query (str): Search query
        db: ChromaDB collection
        n_results (int): Number of results to retrieve
        
    Returns:
        List[str]: List of relevant passages
    """
    try:
        passages = db.query(query_texts=[query], n_results=n_results)['documents'][0]
        return passages
    except Exception as e:
        print(f"Error retrieving relevant passages: {e}")
        return []


def make_rag_prompt(query, relevant_passage):
    """
    Generates a prompt for the Generative AI model using RAG context.
    
    Args:
        query (str): User's question
        relevant_passage (str): Relevant context from the database
        
    Returns:
        str: Formatted prompt for the AI model
    """
    try:
        escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
        prompt = (
            """You are a helpful, friendly, and conversational assistant that answers questions 
            using the reference passage provided below. Your responses should be clear, accessible, 
            and engaging, especially for a non-technical audience. Break down complex concepts into 
            simple terms, using relatable examples where appropriate, and avoid unnecessary jargon. 
            Be concise when possible, but ensure your answers are comprehensive and provide all the 
            necessary context to fully address the question. If the reference passage does not directly 
            relate to the question, you may ignore it or supplement your answer with general knowledge.
            
            QUESTION: '{query}' 
            PASSAGE: '{escaped}' 
            
            ANSWER:"""
        ).format(query=query, escaped=escaped)

        return prompt
    except Exception as e:
        print(f"Error creating RAG prompt: {e}")
        return f"Please answer this question: {query}"


def generate_gemini_answer(prompt):
    """
    Generates an answer using the Generative AI model.
    
    Args:
        prompt (str): Input prompt for the model
        
    Returns:
        str: Generated answer
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        answer = model.generate_content(prompt)
        return answer.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer at this time."


def generate_answer(db, query):
    """
    Generates an answer for the provided query using the database.
    
    Args:
        db: ChromaDB collection
        query (str): User's question
        
    Returns:
        str: Generated answer
    """
    try:
        relevant_text = get_relevant_passage(db, query, n_results=3)
        if not relevant_text:
            return "I couldn't find relevant information to answer your question."
        
        prompt = make_rag_prompt(query, relevant_passage="".join(relevant_text))
        return generate_gemini_answer(prompt)
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I encountered an error while processing your question."


def analyze_document(file_path, output_path="document_analysis"):
    """
    Analyzes a document and creates a searchable database.
    
    Args:
        file_path (str): Path to the document to analyze
        output_path (str): Path where the analysis database should be stored
        
    Returns:
        tuple: (database, database_name) or (None, None) if failed
    """
    try:
        # Load and process the document
        pdf_text = load_pdf(file_path)
        if not pdf_text:
            return None, None
        
        chunked_text = split_text(text=pdf_text)
        if not chunked_text:
            return None, None
        
        # Create the database
        db, name = create_chroma_db(documents=chunked_text, path=output_path)
        return db, name
        
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return None, None


def interactive_document_qa(db):
    """
    Interactive Q&A session for document analysis.
    
    Args:
        db: ChromaDB collection to query
    """
    try:
        print("Document Q&A Session Started. Type 'exit' to quit.")
        
        while True:
            query = input("\nEnter your question: ").strip()
            
            if query.lower() == 'exit':
                print("Exiting Q&A session.")
                break
            
            if not query:
                print("Please enter a question.")
                continue
            
            # Generate answer
            answer = generate_answer(db, query)
            print(f"\nAnswer: {answer}")
            
    except KeyboardInterrupt:
        print("\nQ&A session interrupted.")
    except Exception as e:
        print(f"Error in Q&A session: {e}")


def get_document_stats(db):
    """
    Provides statistics about the document database.
    
    Args:
        db: ChromaDB collection
        
    Returns:
        dict: Database statistics
    """
    try:
        stats = {
            'total_documents': 0,
            'collection_name': db.name if db else 'Unknown',
            'embedding_function': 'Gemini Embedding Model'
        }
        
        if db:
            stats['total_documents'] = db.count()
        
        return stats
    except Exception as e:
        print(f"Error getting document stats: {e}")
        return {}
