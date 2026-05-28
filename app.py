import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from classification import QueryClassifier, QueryType
from rag_pipeline import RAGPipeline
from prompts import build_prompt
from memory import ConversationMemory
from utils.pdf_loader import load_pdf
from utils.knowledge_base import KnowledgeBase

# -----------------------------
# Load environment
# -----------------------------
load_dotenv()

# Azure OpenAI Configuration
#azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
#api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

azure_endpoint = st.secrets.get("AZURE_OPENAI_ENDPOINT")
azure_api_key = st.secrets.get("AZURE_OPENAI_API_KEY")
api_version = st.secrets.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
# Initialize AzureChatOpenAI
llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  # Your deployment name
    openai_api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_api_key,
    temperature=0.3   
)

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Samsung Smart Support Copilot",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .query-type-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .troubleshooting { background-color: #ff6b6b; color: white; }
    .comparison { background-color: #4ecdc4; color: white; }
    .general { background-color: #45b7d1; color: white; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Initialize Session State
# -----------------------------
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory()

if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = RAGPipeline()

if "vector_store_initialized" not in st.session_state:
    st.session_state.vector_store_initialized = False

# -----------------------------
# Helper function for LLM calls
# -----------------------------
def get_llm_response(prompt: str) -> str:
    """Helper function to get response from Azure OpenAI"""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"Error calling Azure OpenAI: {str(e)}")
        return "I'm sorry, I encountered an error. Please try again."

def get_llm_classification(query: str) -> str:
    """Get query classification from Azure OpenAI"""
    prompt = f"""
    Classify the following customer support query into exactly ONE category:
    
    Categories:
    - TROUBLESHOOTING: Issues, problems, errors, device not working properly
    - PRODUCT_COMPARISON: Comparing two or more products, asking which is better
    - GENERAL: Questions about features, specifications, general information
    
    Query: "{query}"
    
    Output only the category name (TROUBLESHOOTING/PRODUCT_COMPARISON/GENERAL):
    """
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip().upper()
    except:
        return "GENERAL"

# -----------------------------
# Sidebar - Settings & Knowledge Base
# -----------------------------
with st.sidebar:
    st.title("⚙️ Support Copilot")
    st.markdown("---")
    
    # Connection Status
    st.subheader("🔌 Azure OpenAI Status")
    try:
        # Test connection with a simple prompt
        test_response = llm.invoke("Say 'Connected'")
        if "Connected" in test_response.content:
            st.success("✅ Connected to Azure OpenAI")
        else:
            st.warning("⚠️ Connection may be unstable")
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)[:50]}...")
    
    st.markdown("---")
    
    # Classification Method
    st.subheader("🔍 Classification Settings")
    classification_method = st.radio(
        "Classification Method",
        ["Rule-based (Faster)", "LLM-based (More Accurate)"],
        help="Rule-based uses keyword matching. LLM-based uses GPT for better accuracy."
    )
    use_llm_classification = classification_method == "LLM-based (More Accurate)"
    
    st.markdown("---")
    
    # Debug Options
    st.subheader("🐛 Debug Settings")
    show_rag_details = st.checkbox("Show RAG Details", value=False)
    show_classification = st.checkbox("Show Query Classification", value=True)
    show_context = st.checkbox("Show Retrieved Context", value=False)
    
    st.markdown("---")
    
    # Knowledge Base Stats
    st.subheader("📚 Knowledge Base")
    if st.session_state.vector_store_initialized:
        st.success("✅ Document loaded")
    else:
        st.info("📂 Upload a PDF to enable RAG")
    
    # Clear chat button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.memory.clear()
        st.session_state.chat_history_display = []
        st.rerun()
    
    st.markdown("---")
    st.caption("🔧 Samsung Smart Support Copilot v1.0")
    st.caption("Powered by Azure OpenAI")

# -----------------------------
# Main Header
# -----------------------------
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🔧 Samsung Smart Support Copilot")
    st.markdown("*AI-powered customer support assistant for Samsung Electronics*")
with col2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/24/Samsung_Logo.svg", width=100)

st.markdown("---")

# -----------------------------
# Two-Column Layout
# -----------------------------
col_chat, col_upload = st.columns([2, 1])

# -----------------------------
# Column 1: Chat Interface
# -----------------------------
with col_chat:
    st.subheader("💬 Support Chat")
    
    # Chat container
    chat_container = st.container()
    
    # Initialize chat history display
    if "chat_history_display" not in st.session_state:
        st.session_state.chat_history_display = []
    
    # Input area
    with st.container():
        user_query = st.text_area(
            "How can I help you today?",
            placeholder="Example: 'My Galaxy S24 is overheating' or 'Compare Galaxy S23 vs S24'",
            key="user_input",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit_button = st.button("📤 Send", type="primary", use_container_width=True)
        with col_btn2:
            example_button = st.button("📋 Show Examples", use_container_width=True)
    
    # Show examples
    if example_button:
        st.info("""
        **Example Queries:**
        - 🔧 Troubleshooting: "Why is my Galaxy phone overheating?"
        - 📊 Comparison: "Compare Samsung Galaxy S23 vs S24 Ultra"
        - 📝 General: "What is the battery capacity of Galaxy S24?"
        - 🔄 Follow-up: "What if the problem keeps happening?"
        """)
    
    # Process query
    if submit_button and user_query:
        with st.spinner("🤔 Analyzing your query..."):
            # 1. Classify Query
            if use_llm_classification:
                classification_result = get_llm_classification(user_query)
                if classification_result == "TROUBLESHOOTING":
                    query_type = QueryType.TROUBLESHOOTING
                elif classification_result == "PRODUCT_COMPARISON":
                    query_type = QueryType.PRODUCT_COMPARISON
                else:
                    query_type = QueryType.GENERAL
            else:
                query_type = QueryClassifier.classify(user_query)
            
            # 2. Get chat history context
            chat_history = st.session_state.memory.get_formatted_history()
            followup_context = st.session_state.memory.get_context_for_followup(user_query)
            
            # 3. Retrieve relevant documents (RAG)
            retrieved_docs = []
            retrieved_context = ""
            if st.session_state.vector_store_initialized:
                retrieved_docs = st.session_state.rag_pipeline.retrieve_docs(user_query, k=3)
                retrieved_context = st.session_state.rag_pipeline.get_retrieved_context(user_query, k=3)
            else:
                retrieved_context = "No knowledge base loaded. Using general support knowledge."
            
            # 4. Build prompt based on query type
            combined_context = f"{chat_history}\n{followup_context}"
            prompt = build_prompt(
                query_type.value,
                combined_context,
                chat_history,
                retrieved_context,
                user_query
            )
            
            # 5. Generate response using Azure OpenAI
            answer = get_llm_response(prompt)
            
            # 6. Add to memory
            st.session_state.memory.add_exchange(user_query, answer, query_type.value)
            
            # 7. Log interaction
            KnowledgeBase.log_interaction(user_query, query_type.value, answer)
            
            # 8. Display in chat
            with chat_container:
                # Display query type badge
                if show_classification:
                    badge_color = {
                        "troubleshooting": "🔴",
                        "comparison": "🟢",
                        "general": "🔵"
                    }.get(query_type.value, "⚪")
                    st.markdown(f"{badge_color} **Query Type:** `{query_type.value.upper()}`")
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_query)
                
                # Display assistant message
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    
                    # Add confidence note if no RAG
                    if not st.session_state.vector_store_initialized:
                        st.caption("⚠️ *Response based on general knowledge. Upload product documentation for more accurate answers.*")
            
            # Show RAG details if enabled
            if show_rag_details and retrieved_docs:
                with st.expander("📄 Retrieved Document Chunks"):
                    for i, doc in enumerate(retrieved_docs, 1):
                        st.markdown(f"**Chunk {i}:**")
                        st.text(doc.page_content[:500])
                        st.markdown("---")
            
            # Show context if enabled
            if show_context and retrieved_context:
                with st.expander("🔍 Retrieved Context"):
                    st.text(retrieved_context[:1000])
    
    # Display chat history
    with chat_container:
        # Show all exchanges from memory
        for exchange in st.session_state.memory.history:
            with st.chat_message("user"):
                st.markdown(exchange['question'])
            with st.chat_message("assistant"):
                st.markdown(exchange['answer'])
                st.caption(f"Query type: {exchange['query_type']}")

# -----------------------------
# Column 2: Document Upload & Knowledge Base
# -----------------------------
with col_upload:
    st.subheader("📂 Knowledge Base")
    
    # Document Upload
    st.markdown("### Upload Documentation")
    st.caption("Upload product manuals, FAQs, or support documents")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload PDFs containing product information, troubleshooting guides, or specifications"
    )
    
    if uploaded_file:
        with st.spinner("📖 Processing document..."):
            try:
                # Extract text from PDF
                text = load_pdf(uploaded_file)
                
                if text:
                    # Create vector store
                    vector_store = st.session_state.rag_pipeline.create_vector_store(text)
                    
                    if vector_store:
                        st.session_state.vector_store_initialized = True
                        st.success(f"✅ Successfully loaded: {uploaded_file.name}")
                        st.info(f"📊 Document size: {len(text)} characters")
                    else:
                        st.error("Failed to create vector store")
                else:
                    st.error("Could not extract text from PDF. Please ensure it's not scanned.")
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    # Knowledge Base Status
    st.markdown("---")
    st.markdown("### 📊 Knowledge Base Status")
    
    if st.session_state.vector_store_initialized:
        st.success("🟢 Vector Store Active")
        st.caption("Document is indexed and ready for retrieval")
    else:
        st.warning("🟡 No Knowledge Base Loaded")
        st.caption("Upload a PDF to enable RAG-powered responses")
    
    # Common Solutions
    st.markdown("---")
    st.markdown("### 🔧 Common Solutions")
    
    issue_type = st.selectbox(
        "Quick troubleshooting for:",
        ["Overheating", "Battery Drain", "WiFi Issues", "Screen Problems"]
    )
    
    if st.button("Show Common Solutions"):
        solutions = KnowledgeBase.get_common_solution(issue_type)
        if solutions:
            st.markdown("**Recommended steps:**")
            for i, step in enumerate(solutions, 1):
                st.markdown(f"{i}. {step}")
        else:
            st.info("Upload product documentation for specific solutions")
    
    # Tips
    st.markdown("---")
    st.markdown("### 💡 Tips for Best Results")
    st.markdown("""
    - **Be specific** about your device model
    - Include **error messages** if any
    - Upload **product manuals** for accurate RAG responses
    - Ask **follow-up questions** for clarification
    - Reference **previous answers** in conversation
    """)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("🔧 Samsung Smart Support Copilot | Powered by Azure OpenAI | For customer support use only")