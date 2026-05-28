from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
import pickle
import os
import streamlit as st
class RAGPipeline:
    def __init__(self):
        self.vector_store = None
        # Use Azure OpenAI Embeddings
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-ada-002",  # Your embedding deployment name
            openai_api_version=st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=st.secrets.get("AZURE_OPENAI_ENDPOINT"),
            api_key=st.secrets.get("AZURE_OPENAI_API_KEY"),
            chunk_size=16
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def create_vector_store(self, text):
        """Create FAISS vector store from document text"""
        chunks = self.text_splitter.split_text(text)
        
        if not chunks:
            return None
            
        self.vector_store = FAISS.from_texts(chunks, self.embeddings)
        return self.vector_store
    
    def retrieve_docs(self, query, k=3):
        """Retrieve relevant document chunks for a query"""
        if not self.vector_store:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        return docs
    
    def get_retrieved_context(self, query, k=3):
        """Get formatted context from retrieved documents"""
        docs = self.retrieve_docs(query, k)
        
        if not docs:
            return "No relevant documentation found in the knowledge base."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Source {i}]: {doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def save_vector_store(self, path="vector_store.pkl"):
        """Save vector store to disk"""
        if self.vector_store:
            with open(path, 'wb') as f:
                pickle.dump(self.vector_store, f)
    
    def load_vector_store(self, path="vector_store.pkl"):
        """Load vector store from disk"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                self.vector_store = pickle.load(f)
            return True
        return False