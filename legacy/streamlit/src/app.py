import hmac
import streamlit as st
import warnings
import csv
warnings.filterwarnings(
    "ignore",
    message=".*encoder_attention_mask.*",
    category=FutureWarning
)

import os
import json
import datetime
from typing import TypedDict, Optional, List, Any, Dict
import io
import tempfile
import base64
import time
import shutil

# LangChain / LangGraph
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Import task modules - model agnostic and modular
from highlights import generate_highlights_response as generate_highlights_response_external
from summarization import generate_summarization_response as generate_summarization_response_external
from qa import generate_qa_response as generate_qa_response_external, generate_qa_response

# Import core validation and processing modules
from core.validation import DataValidator, DataProcessor

# Import sport factory for sport selection
from sports.factory import SportFactory
# Import theme system
# Removed theme system - using simple dark theme

from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_FAISS_BASE_PATH = os.path.join(PROJECT_ROOT, 'rag_database', 'faiss_indices')
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LM Studio Configuration
LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "phi-3-mini-128k-instruct"

# GLOBAL CACHE to bypass LangGraph state management issues
_GLOBAL_RALLY_CACHE = {}

# --- State Definition for LangGraph ---
class AgentState(TypedDict, total=False):
    player_names: str
    task: str
    question: str
    video_url: str
    semantics_path: str
    semantics_analysis: str
    retrieved_context: str
    generation: str
    highlight_rallies: List
    event_data: List[Dict[str, Any]]  # Add event_data field
    sport_adapter: Optional[Any]  # Add sport adapter to state
    highlights_limit: Optional[int]  # Add highlights_limit field

# --- Database Rebuild Function ---
def rebuild_database():
    """Rebuild all sport-specific FAISS indices using src/build_db.py."""
    try:
        import importlib.util
        build_db_path = os.path.join(SCRIPT_DIR, 'build_db.py')
        if not os.path.exists(build_db_path):
            st.error(f"build_db.py not found at {build_db_path}")
            return False

        spec = importlib.util.spec_from_file_location("build_db", build_db_path)
        build_db = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(build_db)

        if hasattr(build_db, 'build_database'):
            st.info("Starting sport-specific FAISS database rebuild...")
            success = build_db.build_database()
            if success:
                st.success("All sport-specific FAISS indices rebuilt successfully!")
            else:
                st.error("Some sport indices failed to build. Check logs for details.")
            return success
        else:
            st.error("build_db.build_database() not found")
            return False
    except Exception as e:
        st.error(f"Database rebuild failed: {e}")
        return False

# --- Enhanced Styling Functions ---
def inject_dark_theme_css():
    """Inject simple dark theme CSS."""
    dark_theme_css = """
    <style>
    /* Dark theme base */
    :root {
        --bg-color: #0f0f0f;
        --card-bg: #1a1a1a;
        --text-color: #ffffff;
        --text-secondary: #cccccc;
        --accent-color: #4f46e5;
        --border-color: #333333;
    }

    body {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
        width: 100%;
        box-sizing: border-box;
    }

    .header-section {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid var(--border-color);
        margin-bottom: 2rem;
        margin-top:-100px;
    }

    .header-section h1 {
        color: var(--text-color);
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .header-section p {
        color: var(--text-secondary);
        font-size: 1.2rem;
    }

    .content-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-bottom: 2rem;
        width: 100%;
        box-sizing: border-box;
    }

    .upload-card {
        background: var(--card-bg);
        border: 2px dashed var(--accent-color);
        border-radius: 12px;
        padding: 2.37rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .upload-card:hover {
        border-color: #6366f1;
        background: #222222;
    }

    .info-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
    }

    .stButton button, .stDownloadButton > button {
        background: var(--accent-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important; /* Full width buttons for better touch targets */
        box-sizing: border-box;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: var(--card-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        width: 100% !important;
        box-sizing: border-box;
    }

    .stExpander {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    /* Tablet breakpoint */
    @media (max-width: 1024px) {
        .content-grid { grid-template-columns: 1fr; }
        .main-container { padding: 1.5rem; }
        .upload-card { padding: 1.75rem; }
        .header-section h1 { font-size: 2.25rem; }
        .header-section p { font-size: 1.05rem; }
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .content-grid { grid-template-columns: 1fr; gap: 1.25rem; }
        .main-container { padding: 1.25rem; }
        .upload-card { padding: 1.5rem; }
        .info-card { padding: 1.25rem; }
        .header-section h1 { font-size: 2rem; }
        .header-section p { font-size: 0.95rem; }
    }

    /* Small phones */
    @media (max-width: 480px) {
        .main-container { padding: 1rem; }
        .content-grid { gap: 1rem; }
        .upload-card { padding: 1.25rem; }
        .header-section h1 { font-size: 1.75rem; }
        .header-section p { font-size: 0.9rem; }
    }
    </style>
    """
    st.markdown(dark_theme_css, unsafe_allow_html=True)




def show_processing_page():
    """Display animated processing page."""
    print("\n=== Inside show_processing_page ===")
    # Create a container that spans the full width of the two columns above
    with st.container():
        st.markdown("""
        <div class="processing-container" style="width: 100%; margin: 0 auto;">
            <h2>ðŸ§  AI Analysis in Progress</h2>
            <div class="progress-circle"></div>
            <h3>Neural Networks Processing Your Data...</h3>
            <p>Our advanced AI is analyzing patterns, extracting insights, and generating comprehensive reports.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Animated progress bar
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # Add custom CSS to make the container full width
        st.markdown("""
        <style>
            .processing-container {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                border-radius: 20px;
                padding: 3rem;
                text-align: center;
                color: white;
                margin: 2rem 0;
                width: 100% !important;
                max-width: none !important;
            }
            
            .progress-circle {
                width: 100px;
                height: 100px;
                border: 8px solid rgba(255,255,255,0.2);
                border-top: 8px solid #00d4ff;
                border-radius: 50%;
                margin: 2rem auto;
                animation: spin 2s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
        """, unsafe_allow_html=True)
        
        stages = [
            "🔍 Analyzing uploaded files...",
            "🧠 Processing with Neural Networks...",
            "📊 Extracting performance metrics...",
            "🎯 Identifying key patterns...",
            "💡 Generating insights...",
            "✨ Finalizing report..."
        ]
        
        for i, stage in enumerate(stages):
            progress_text.text(stage)
            progress_bar.progress((i + 1) / len(stages))
            time.sleep(1)
        
        return True

# --- LLM Loader ---
@st.cache_resource
def load_llm():
    """Loads the configured LLM using LLMProviderFactory."""
    try:
        from core.llm_provider import LLMProviderFactory
        llm = LLMProviderFactory.get_default_llm()

        # Test connection
        try:
            _ = llm.invoke("Hello")
            return llm
        except Exception as e:
            provider = os.getenv("LLM_PROVIDER", "azure_openai")
            st.error(f"Failed to connect to {provider} LLM service: {e}")
            return None

    except Exception as e:
        st.error(f"Failed to initialize LLM client: {e}")
        return None


# --- Core Components ---
@st.cache_resource
def load_retriever(sport_name: str = None):
    """Loads the FAISS retriever from local storage for a specific sport."""
    try:
        if sport_name is None:
            st.error("No sport specified for database loading.")
            return None
        
        db_path = os.path.join(DB_FAISS_BASE_PATH, f'{sport_name}_faiss_index')
        
        if not os.path.exists(db_path):
            st.error(f"FAISS index not found at {db_path}. Please run 'python src/build_db.py' first.")
            return None

        embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectordb = FAISS.load_local(
            db_path,
            embedding_function,
            allow_dangerous_deserialization=True
        )
        return vectordb.as_retriever()
    except Exception as e:
        st.error(f"Error loading retriever for {sport_name}: {e}")
        return None
def transcribe_audio_alternative(file_path):
    """Alternative transcription method using local speech recognition if available."""
    try:
        import speech_recognition as sr
        import pydub

        # Convert audio to WAV format if needed
        if not file_path.lower().endswith('.wav'):
            audio = pydub.AudioSegment.from_file(file_path)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                audio.export(temp_wav.name, format='wav')
                wav_path = temp_wav.name
        else:
            wav_path = file_path

        # Initialize recognizer
        r = sr.Recognizer()

        # Load audio file
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)

        transcript = ""
        # Try Google Web Speech API (online)
        try:
            transcript = r.recognize_google(audio_data)
        except sr.RequestError:
            try:
                # Try offline recognition with PocketSphinx
                transcript = r.recognize_sphinx(audio_data)
            except sr.RequestError:
                transcript = "[Audio transcription unavailable - install speech_recognition and pydub]"
        except sr.UnknownValueError:
            transcript = "[Could not understand audio content]"

        # Clean up temporary file if created
        if wav_path != file_path and os.path.exists(wav_path):
            os.unlink(wav_path)

        return transcript

    except ImportError:
        return f"[Audio file {os.path.basename(file_path)} - install speech_recognition and pydub for transcription]"
    except Exception as e:
        return f"[Audio transcription failed: {str(e)}]"

def save_uploaded_files(uploaded_files) -> str:
    """Save uploaded files to a temporary directory and return the path."""
    if not uploaded_files:
        return ""
    
    # Create a temporary directory for this session
    temp_dir = tempfile.mkdtemp(prefix="streamlit_sports_analysis_")
    
    for uploaded_file in uploaded_files:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    return temp_dir

# --- LangGraph Nodes ---
def analyze_semantics(state: AgentState):
    """Sport-agnostic data analysis using the selected sport adapter."""
    try:
        print("[DEBUG] Starting analyze_semantics (sport-agnostic)")
        semantics_path = state.get('semantics_path', '')
        sport_adapter = state.get('sport_adapter')

        if not sport_adapter:
            error_msg = "No sport adapter provided."
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        print(f"[DEBUG] Semantics path: {semantics_path}")
        print(f"[DEBUG] Sport adapter: {sport_adapter.sport_name}")

        # Handle empty or invalid path
        if not semantics_path:
            error_msg = "No path provided."
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        # Validate the path
        if not os.path.exists(semantics_path):
            error_msg = f"Path does not exist: {semantics_path}"
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        # Find all CSV files in the path
        if os.path.isfile(semantics_path):
            # Single file
            csv_files = [semantics_path]
        elif os.path.isdir(semantics_path):
            # Directory
            csv_files = [os.path.join(semantics_path, f)
                        for f in os.listdir(semantics_path)
                        if os.path.isfile(os.path.join(semantics_path, f))
                        and f.lower().endswith('.csv')]
        else:
            error_msg = f"Invalid path type: {semantics_path}"
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        if not csv_files:
            error_msg = "No CSV files found in the provided path."
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        st.info(f"Found {len(csv_files)} CSV file(s). Processing...")
        print(f"[DEBUG] Found {len(csv_files)} CSV files")

        # Use DataValidator to process files
        validator = DataValidator(sport_adapter)
        processor = DataProcessor(sport_adapter)

        valid_files = []
        all_event_data = []

        for file_path in csv_files:
            print(f"[DEBUG] Processing file: {file_path}")

            try:
                # Validate and parse the file
                file_valid_files, file_event_data = validator.validate_csv_files(file_path)
                if file_event_data:
                    valid_files.extend(file_valid_files)
                    all_event_data.extend(file_event_data)

            except Exception as e:
                import traceback
                error_msg = f"❌ Error processing {os.path.basename(file_path)}: {str(e)}\n{traceback.format_exc()}"
                print(f"[ERROR] {error_msg}")
                st.error(f"❌ Error processing {os.path.basename(file_path)}: {str(e)}")
                continue

        if not all_event_data:
            error_msg = "No valid event data could be processed from the provided CSV files."
            print(f"[ERROR] {error_msg}")
            return {
                "semantics_analysis": error_msg,
                "event_data": []
            }

        print(f"[DEBUG] Processed {len(all_event_data)} events from {len(valid_files)} files")

        # Process the event data using the sport adapter
        try:
            processed_events = processor.process_rally_data(all_event_data)
            print(f"[DEBUG] Processed {len(processed_events)} events")
        except Exception as e:
            error_msg = f"Error processing event data: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {"semantics_analysis": error_msg, "event_data": []}

        # Generate summary statistics
        summary_stats = processor.generate_summary_stats(processed_events)

        # Create analysis summary
        analysis_summary = f"""
Sport: {sport_adapter.sport_name.title()}
Events Processed: {len(processed_events)}
Average Excitement Score: {summary_stats.get('average_excitement_score', 0):.2f}
Data Quality: Good ({len(valid_files)}/{len(csv_files)} files valid)
"""

        print(f"[DEBUG] analyze_semantics completed successfully")

        # Return sport-agnostic results
        result = {
            "event_data": processed_events,  # Generic event data instead of rally_data
            "semantics_analysis": analysis_summary,
            "processed_files": valid_files,
            "event_count": len(processed_events),
            "summary_stats": summary_stats,
            "sport_adapter": sport_adapter  # Pass adapter forward
        }

        print(f"[DEBUG] analyze_semantics result keys: {list(result.keys())}")

        return result

    except Exception as e:
        error_message = f"Analysis failed: {str(e)}"
        if 'valid_files' in locals() and valid_files:
            error_message += f" Files processed: {', '.join(valid_files)}."
        return {"semantics_analysis": error_message, "event_data": []}

def retrieve_documents(state: AgentState):
    """Retrieves relevant documents from the FAISS vector store and preserves event_data."""
    try:
        print("\n" + "="*80)
        print("RETRIEVE_DOCUMENTS: Starting document retrieval...")
        print(f"[DEBUG] State keys: {list(state.keys())}")

        # Get sport adapter and event data
        sport_adapter = state.get('sport_adapter')
        event_data = state.get('event_data', [])

        print(f"[DEBUG] Event data count: {len(event_data) if isinstance(event_data, list) else 0}")
        # Get player names from state
        player_names = state.get('player_names', '').lower()
        print(f"[DEBUG] Player names for retrieval: {player_names}")

        # Load the retriever
        retriever = load_retriever(sport_adapter.sport_name if sport_adapter else None)
        if not retriever:
            error_msg = "❌ Error: Could not load the document retriever."
            print(f"[ERROR] {error_msg}")
            return {
                "retrieved_context": error_msg,
                "event_data": event_data  # Preserve event_data
            }

        # Prepare the query based on available state
        query_parts = []

        # Add player names to the query if available
        if player_names:
            query_parts.append(f"Information about {player_names}")

        # Add task to the query if available
        task = state.get('task', '').lower()
        if task == 'summarize':
            query_parts.append("summary of the match")
        elif task == 'highlights':
            query_parts.append("key moments and highlights")
        elif task == 'qa':
            query_parts.append("answer to the question")

        # Add question to the query if available
        if 'question' in state and state['question']:
            query_parts.append(state['question'])

        # Add sport-specific terminology
        if sport_adapter:
            sport_queries = sport_adapter.get_default_queries()
            query_parts.extend(sport_queries[:2])  # Add first 2 sport queries

        # If we don't have enough context, use a generic query
        if not query_parts:
            query = f"{sport_adapter.sport_name} match analysis" if sport_adapter else "sports match analysis"
        else:
            query = ". ".join(query_parts)

        print(f"[DEBUG] Retrieving documents for query: {query}")

        # Retrieve documents
        docs = retriever.get_relevant_documents(query)
        print(f"[DEBUG] Retrieved {len(docs)} documents")

        # Format the context
        context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}"
                              for i, doc in enumerate(docs)])
        print(f"[DEBUG] Retrieved context length: {len(context)} characters")

        print(f"[DEBUG] Returning to workflow with event_data type: {type(event_data)}")
        print(f"[DEBUG] event_data length: {len(event_data) if isinstance(event_data, list) else 0}")

        return {
            "retrieved_context": context,
            "event_data": event_data,  # Ensure event_data is always returned
            "sport_adapter": sport_adapter  # Pass adapter forward
        }

    except Exception as e:
        st.error(f"Error during document retrieval: {e}")
        return {
            "retrieved_context": f"Retrieval failed: {str(e)}",
            "event_data": event_data  # Preserve event_data even on error
        }

def generate_final_response(state: AgentState):
    """Routes to appropriate task-specific response generator from external modules."""
    try:
        print("\n" + "="*80)
        print("GENERATE_FINAL_RESPONSE: Starting response generation...")
        print(f"[DEBUG] State keys: {list(state.keys())}")

        # Get task type and sport adapter
        task = state.get('task', 'summarize').lower()
        sport_adapter = state.get('sport_adapter')
        event_data = state.get('event_data', [])

        print(f"[DEBUG] Task: {task}")
        print(f"[DEBUG] Event data count: {len(event_data) if isinstance(event_data, list) else 0}")

        # Route to the appropriate response generator from external modules
        response = None
        try:
            if task == 'summarize':
                # Map event_data to highlight_rallies for summarization module compatibility
                state_copy = state.copy()
                state_copy['highlight_rallies'] = state.get('event_data', [])
                response = generate_summarization_response_external(state_copy)
            elif task == 'highlights':
                response = generate_highlights_response_external(state)
            elif task == 'qa':
                # Map event_data to highlight_rallies for QA module compatibility
                state_copy = state.copy()
                state_copy['highlight_rallies'] = state.get('event_data', [])
                response = generate_qa_response_external(state_copy)
            else:
                response = {"generation": f"Unknown task: {task}"}

        except Exception as e:
            import traceback
            error_msg = f"❌ An error occurred while generating the response: {str(e)}\n\n"
            error_msg += f"Traceback:\n{traceback.format_exc()}"
            print(f"[ERROR] {error_msg}")
            return {"generation": error_msg}

    except Exception as e:
        import traceback
        error_msg = f"❌ An error occurred in generate_final_response: {str(e)}\n\n"
        error_msg += f"Traceback:\n{traceback.format_exc()}"
        print(f"[ERROR] {error_msg}")
        return {"generation": error_msg}

# --- Build the Graph ---
@st.cache_resource
def create_workflow():
    """Creates and returns the compiled workflow."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_semantics", analyze_semantics)
    workflow.add_node("retrieve_db_docs", retrieve_documents)
    workflow.add_node("generate_final_response", generate_final_response)

    # Define the workflow edges
    workflow.set_entry_point("analyze_semantics")

    # Add conditional edge to check if we have event_data after analyze_semantics
    def should_continue_after_analysis(state):
        print("\n[DEBUG] Checking if we should continue after analysis...")
        print(f"[DEBUG] State keys: {list(state.keys())}")

        # Debug: Print all state values for inspection
        for key, value in state.items():
            if key == 'event_data':
                print(f"[DEBUG] State[{key}] type: {type(value)}")
                if isinstance(value, list):
                    print(f"[DEBUG] State[{key}] length: {len(value)}")
                    if value and isinstance(value[0], dict):
                        print(f"[DEBUG] First item keys: {list(value[0].keys())}")
            elif key == 'semantics_analysis':
                print(f"[DEBUG] State[{key}] type: {type(value)}")
                if isinstance(value, str):
                    print(f"[DEBUG] Value preview: {value[:200]}...")

        # Check for event_data in various formats
        event_data = state.get('event_data', [])
        print(f"[DEBUG] event_data type: {type(event_data)}")

        # Case 1: event_data is a non-empty list
        if isinstance(event_data, list) and event_data:
            print(f"[DEBUG] Found {len(event_data)} events in event_data list")
            if len(event_data) > 0 and isinstance(event_data[0], dict):
                print("[DEBUG] First event item:", {k: v for k, v in event_data[0].items() if k != 'ball_types'})
            return "retrieve_db_docs"

        # Case 2: event_data is a string that can be parsed
        if isinstance(event_data, str) and event_data.strip():
            print("[DEBUG] Found event_data as string, checking if it contains event data...")
            # Check if it's a JSON string
            try:
                import json
                parsed = json.loads(event_data)
                if isinstance(parsed, list) and parsed:
                    print(f"[DEBUG] Successfully parsed {len(parsed)} events from JSON string")
                    state['event_data'] = parsed  # Update state with parsed data
                    return "retrieve_db_docs"
            except json.JSONDecodeError:
                pass

        # Case 3: Check if we have a valid task that doesn't require event_data
        task = state.get('task', '').lower()
        if task in ['summarize', 'qa']:
            print(f"[DEBUG] Task '{task}' doesn't strictly require event_data, continuing...")
            return "retrieve_db_docs"

        print("[WARNING] No valid event data found after analysis, going directly to response generation")
        print("[DEBUG] Last state before going to response generation:")
        for k, v in state.items():
            print(f"- {k}: {type(v).__name__}")
            if k == 'event_data' and isinstance(v, list) and len(v) > 0:
                print(f"  First item keys: {list(v[0].keys())}")

        return "generate_final_response"  # No valid event data, go directly to response

    workflow.add_conditional_edges(
        "analyze_semantics",
        should_continue_after_analysis,
        {
            "retrieve_db_docs": "retrieve_db_docs",
            "generate_final_response": "generate_final_response"
        }
    )

    # From retrieve_db_docs, always go to generate_final_response
    workflow.add_edge("retrieve_db_docs", "generate_final_response")

    workflow.add_edge("generate_final_response", END)

    return workflow.compile()

# --- Streamlit Web Interface ---
def check_auth(username: str, password: str) -> bool:
    """Check if username and password are correct."""
    expected_user = os.getenv("ADMIN_USERNAME")
    expected_pass = os.getenv("ADMIN_PASSWORD")
    if not expected_user or not expected_pass:
        return False
    return hmac.compare_digest(username, expected_user) and hmac.compare_digest(password, expected_pass)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Sports Analytics AI",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session states
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Inject dark theme CSS
    inject_dark_theme_css()
    
    # Sidebar for sport selection and configuration
    with st.sidebar:
        # Modern sidebar header
        st.markdown("### 🏆 Sport Selection")

        # Sport selection
        available_sports = SportFactory.get_available_sports()
        coming_soon_sports = SportFactory.get_coming_soon_sports()

        # Combine available and coming soon sports
        all_sports = available_sports + coming_soon_sports
        sport_options = []

        # Add available sports with checkmark
        for sport in available_sports:
            sport_options.append(f"✅ {sport.title()}")

        # Add coming soon sports
        for sport in coming_soon_sports:
            sport_options.append(f"🔜 {sport.title()} (Coming Soon)")

        selected_sport_option = st.selectbox(
            "Choose your sport:",
            options=sport_options,
            help="Select the sport for analysis. Only badminton is fully supported currently.",
            key="sport_selector"
        )

        # Extract the sport name from the selection
        if selected_sport_option.startswith("✅ "):
            selected_sport = selected_sport_option[2:].lower()
        elif selected_sport_option.startswith("🔜 "):
            selected_sport = selected_sport_option[2:].replace(" (Coming Soon)", "").lower()
        else:
            selected_sport = selected_sport_option.lower()

        # Get sport adapter and config
        try:
            if selected_sport == 'badminton':
                sport_adapter = SportFactory.get_adapter(selected_sport)
                sport_config = sport_adapter.config
                st.success(f"✅ Selected: {sport_config.name.title()}")
            else:
                st.warning(f"🔜 {selected_sport.title()} support is coming soon!")
                st.info("Currently, Only 🏸 Badminton analysis is fully supported. Please select Badminton to proceed.")
                sport_adapter = None
                sport_config = None
        except Exception as e:
            st.error(f"❌ Error loading sport adapter: {e}")
            sport_adapter = None
            sport_config = None


        # AI connection test
        provider_name = os.getenv("LLM_PROVIDER", "azure_openai").replace("_", " ").title()
        model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini") if "azure" in os.getenv("LLM_PROVIDER", "azure_openai").lower() else os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        if st.button("🔗 Test AI Connection", use_container_width=True):
            with st.spinner(f"Testing {provider_name} ({model_name})..."):
                llm = load_llm()
                if llm:
                    st.success(f"✅ {provider_name} ({model_name}) Connected!")
                else:
                    st.error("❌ Connection failed!")

        st.markdown("---")

        # Admin authentication
        if not st.session_state.get('authenticated', False):
            with st.expander("🔐 Admin Login", expanded=False):
                with st.form("login_form"):
                    st.write("Admin Access")
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login", use_container_width=True):
                        if check_auth(username, password):
                            st.session_state.authenticated = True
                            st.success("✅ Logged in successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
        else:
            st.success("🔓 Admin Mode Active")
            if st.button("🔒 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

            # Admin controls
            if st.button("🔄 Rebuild Database", use_container_width=True, help="Rebuild the FAISS vector database"):
                with st.spinner("Rebuilding database..."):
                    success = rebuild_database()
                    if success:
                        st.success("✅ Database rebuilt successfully!")

    # Main interface with simple layout
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header section
    st.markdown("""
    <div class="header-section">
        <h1> 🏆 Sports Analytics AI</h1>
        <p>Advanced Performance Analysis Powered by Local AI Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

    # Content grid
    st.markdown('<div class="content-grid">', unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 📁 Data Input")

            # Upload zone
            st.markdown("""
            <div class="upload-card">
                <h4> Upload Sports Data</h4>
                <p>Drop your match files here</p>
                <small>Supports: CSV, JSON, TXT, Audio files</small>
            </div>
            """, unsafe_allow_html=True)

            # File upload
            uploaded_files = st.file_uploader(
                "Select match files",
                accept_multiple_files=True,
                type=['txt', 'json', 'csv', 'wav', 'mp3', 'flac'],
                help="Upload match data files. Supports rally data, match statistics, and audio commentary.",
                label_visibility="collapsed"
            )

            if uploaded_files:
                st.success(f"📂 {len(uploaded_files)} Files Uploaded")
                for file in uploaded_files:
                    st.markdown(f"""
                    <div class="genz-card">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span>🏸</span>
                            <span>{file.name}</span>
                            <span style="margin-left: auto; font-size: 0.8rem; opacity: 0.7;">{file.type}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 👤 Player Information")

            col2a, col2b = st.columns(2)

            with col2a:
                player1 = st.text_input(
                    "Player 1 Name",
                    placeholder=sport_config.get_terminology('player1', 'e.g., Viktor Axelsen') if sport_config else "Enter first player name",
                    help="Enter the name of the first player"
                )

            with col2b:
                player2 = st.text_input(
                    "Player 2 Name",
                    placeholder=sport_config.get_terminology('player2', 'e.g., Kento Momota') if sport_config else "Enter second player name",
                    help="Enter the name of the second player"
                )

            # Video URL input (optional)
            video_url = st.text_input(
                "Match Video URL (For Only Highlights)",
                placeholder="Enter match video URL or path (Optional) ",
                help="Optional: Provide match video for highlight clips",
                key="video_url_input"
            )

            # Highlights count selection - manual input
            if 'highlights_limit' not in st.session_state:
                st.session_state.highlights_limit = 7

            highlights_limit = st.number_input(
                "Enter number of top highlights:",
                min_value=1,
                max_value=100,
                value=int(st.session_state.get('highlights_limit', 7)),
                step=1,
                key="highlights_number"
            )

            # Persist manual input to session state
            st.session_state.highlights_limit = int(highlights_limit)
            print(f"[DEBUG] UI - Setting highlights_limit in session_state: {int(highlights_limit)}")

            # Player names construction
            if player1 and player2:
                player_names = f"{player1} vs {player2}"
            elif player1:
                player_names = f"{player1} vs opponent"
            elif player2:
                player_names = f"{player2} vs opponent"
            else:
                player_names = "the badminton players"

            # Simple player info display
            st.markdown(f"""
            <div class="info-card">
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span> Analyzing: <strong>{player_names}</strong></span>
                </div>
                {f'<div>📹 Video provided: Highlight clips will be generated</div>' if video_url else '<div style="opacity: 0.7;">💡 Add video URL for highlight clips</div>'}
            </div>
            """, unsafe_allow_html=True)


    st.markdown('</div>', unsafe_allow_html=True)  # Close content-grid

    # Task selection section
    st.markdown("### 🎯 Analysis Task")

    task_options = {
        "🏆 Match Summary": "summarize",
        "🎬 Match Highlights": "highlights",
        "❓ Q&A Analysis": "qa"
    }

    selected_task = st.selectbox(
        "Choose match analysis type:",
        options=list(task_options.keys()),
        help="Select the type of match  performance analysis you want to perform",
        key="task_selector"
    )

    task = task_options[selected_task]

    # Question input for Q&A
    question = ""
    if task == "qa":
        question = st.text_area(
            "Enter your match question:",
            placeholder=sport_config.get_terminology('question', 'e.g., How was the player\'s smash technique in the second game?') if sport_config else "e.g., How was the player's smash technique?",
            help="Leave blank for comprehensive rally analysis, or ask a specific match question",
            height=100
        )

    st.markdown('</div>', unsafe_allow_html=True)  # Close main-container

    # Analysis button
    if st.button("Start Match Analysis", type="primary"):
        if not uploaded_files:
            st.error("Please upload at least one match data file to analyze.")
            st.stop()

        if not sport_adapter:
            st.error("Please select Badminton as your sport before analyzing.")
            st.stop()

        # Save uploaded files to temporary directory
        temp_dir = save_uploaded_files(uploaded_files)

        try:
            # Create workflow
            app = create_workflow()

            # Get highlights_limit from session state to ensure it's always available
            # Force a default if not set
            if 'highlights_limit' not in st.session_state:
                st.session_state.highlights_limit = 7
            
            current_highlights_limit = st.session_state.get('highlights_limit', 7)
            print(f"[DEBUG] Button clicked - highlights_limit from session_state: {current_highlights_limit}")
            print(f"[DEBUG] Full session_state keys: {list(st.session_state.keys())}")
            print(f"[DEBUG] Task selected: {task}")
            
            # Also try to get from the widget directly
            widget_value = st.session_state.get('highlights_number', 7)
            print(f"[DEBUG] Widget value (highlights_number): {widget_value}")
            
            # Use the widget value as priority, then session state, then default
            if widget_value and widget_value > 0:
                final_highlights_limit = int(widget_value)
            elif current_highlights_limit and current_highlights_limit > 0:
                final_highlights_limit = int(current_highlights_limit)
            else:
                final_highlights_limit = 7
                
            print(f"[DEBUG] Final highlights_limit to use: {final_highlights_limit}")
            print(f"[DEBUG] Type of final_highlights_limit: {type(final_highlights_limit)}")
            
            # Prepare initial state
            print(f"[DEBUG] Creating initial_state with highlights_limit: {final_highlights_limit}")
            initial_state: AgentState = {
                "semantics_path": temp_dir,
                "player_names": player_names,
                "task": task,
                "question": question,
                "video_url": video_url if video_url else "",
                "semantics_analysis": "",
                "retrieved_context": "",
                "generation": "",
                "event_data": [],  # Initialize event_data
                "sport_adapter": sport_adapter,  # Add sport adapter to state
                "highlights_limit": final_highlights_limit,  # User-selected highlights count from widget/session state
                "highlight_rallies": []  # Initialize highlight_rallies in state
            }
            print(f"[DEBUG] initial_state['highlights_limit'] = {initial_state['highlights_limit']}")

            # Run analysis
            start_time = time.time()

            with st.spinner("Analyzing match data..."):
                final_state: AgentState = app.invoke(initial_state)

            end_time = time.time()

            # Store results in session state for Q&A
            if task == "qa":
                st.session_state.analysis_state = final_state

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
        finally:
            # Clean up temporary directory if not needed for Q&A
            if task != "qa" and temp_dir:
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass

    # Interactive Q&A section
    if task == "qa" and 'analysis_state' in st.session_state:
        st.header(" Interactive Match Q&A")
        st.markdown("Ask follow-up questions about the match analysis:")

        follow_up_question = st.text_input(
            "Your match question:",
            placeholder="e.g., What were the key tactical differences in the rallies?",
            key="followup"
        )

        if st.button("Ask Match Question") and follow_up_question:
            # Create new state for follow-up question
            follow_state = st.session_state.analysis_state.copy()
            follow_state['question'] = follow_up_question

            with st.spinner("Analyzing match question..."):
                response = generate_qa_response(follow_state)

            if response.get("generation"):
                st.markdown("### 🏸 Answer:")
                st.markdown(response['generation'])
            else:
                st.error("Failed to generate answer.")

if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Sports Analysis RAG System")
    parser.add_argument("--rebuild-db", action="store_true", help="Rebuild the FAISS database")
    
    args = parser.parse_args()
    
    if args.rebuild_db:
        print("Starting database rebuild from command line...")
        if rebuild_database():
            print("✅ Database rebuilt successfully!")
            exit(0)
        else:
            print("❌ Database rebuild failed!")
            exit(1)
    else:
        # Run the Streamlit app
        main()