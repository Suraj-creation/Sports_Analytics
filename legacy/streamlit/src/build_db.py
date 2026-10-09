import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, '..', 'input')
DB_FAISS_BASE_PATH = os.path.join(SCRIPT_DIR, '..', 'rag_database', 'faiss_indices')

# Available sports
SUPPORTED_SPORTS = ['badminton', 'soccer', 'tennis', 'volleyball']

def build_database_for_sport(sport_name):
    """
    Builds and persists a FAISS vector database for a specific sport
    from documents in the sport's input subdirectory.
    """
    print(f"Starting to build the database for {sport_name}...")
    
    sport_input_dir = os.path.join(INPUT_DIR, sport_name)
    sport_db_path = os.path.join(DB_FAISS_BASE_PATH, f'{sport_name}_faiss_index')
    
    # 1. Load documents
    print(f"Loading documents from: {os.path.abspath(sport_input_dir)}")
    if not os.path.exists(sport_input_dir):
        print(f"Warning: Sport directory not found at {os.path.abspath(sport_input_dir)}")
        return False

    # Load text documents
    txt_loader = DirectoryLoader(
        sport_input_dir, 
        glob="**/*.txt", 
        loader_cls=TextLoader, 
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True
    )
    txt_documents = txt_loader.load()
    
    # Load CSV documents
    try:
        from langchain_community.document_loaders.csv_loader import CSVLoader
        csv_loader = DirectoryLoader(
            sport_input_dir, 
            glob="**/*.csv", 
            loader_cls=CSVLoader,
            loader_kwargs={"encoding": 'utf-8'},
            show_progress=True
        )
        csv_documents = csv_loader.load()
    except ImportError:
        print("Warning: Could not import CSVLoader. Install with: pip install pandas")
        csv_documents = []
    
    documents = txt_documents + csv_documents
    
    if not documents:
        print(f"No documents found to load for {sport_name}. Please check the 'input/{sport_name}' directory for .txt or .csv files.")
        return False
        
    print(f"Loaded {len(documents)} documents ({len(txt_documents)} text, {len(csv_documents)} CSV) for {sport_name}.")

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks for {sport_name}.")

    # 3. Create embeddings
    print("Initializing embedding model... (This may take a moment)")
    # Using a smaller, efficient model suitable for local use
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 4. Create and persist the vector store
    print(f"Creating and persisting the FAISS index for {sport_name} at: {os.path.abspath(sport_db_path)}")
    vectordb = FAISS.from_documents(texts, embedding_model)
    vectordb.save_local(sport_db_path)
    print(f"\nFAISS index for {sport_name} built and saved successfully!")
    print(f"Index is saved in the '{sport_db_path}' directory.")
    return True

def build_database():
    """
    Builds and persists FAISS vector databases for all supported sports.
    """
    print("Starting to build databases for all sports...")
    
    # Create base directory if it doesn't exist
    os.makedirs(DB_FAISS_BASE_PATH, exist_ok=True)
    
    success_count = 0
    for sport in SUPPORTED_SPORTS:
        if build_database_for_sport(sport):
            success_count += 1
    
    print(f"\nDatabase building completed! {success_count}/{len(SUPPORTED_SPORTS)} sports processed successfully.")
    if success_count > 0:
        print(f"Indices are saved in the '{DB_FAISS_BASE_PATH}' directory.")
    
    return success_count > 0

if __name__ == "__main__":
    build_database()

