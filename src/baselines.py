import os
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DataFrameLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from huggingface_hub import InferenceClient

# Constants
DATA_DIR = "data"
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")

def create_vector_db():
    print("Loading CSV files...")
    
    # Read files
    try:
        files_df = pd.read_csv(os.path.join(DATA_DIR, "Nodes_Files.csv")).dropna(subset=["content"])
        files_df['text'] = "FILE: " + files_df['path'] + "\nCONTENT:\n" + files_df['content']
    except Exception:
        files_df = pd.DataFrame(columns=["id", "text"])
        
    try:
        functions_df = pd.read_csv(os.path.join(DATA_DIR, "Nodes_Functions.csv")).dropna(subset=["code"])
        functions_df['text'] = "FUNCTION: " + functions_df['name'] + "\nCODE:\n" + functions_df['code']
    except Exception:
        functions_df = pd.DataFrame(columns=["id", "text"])
        
    try:
        prompts_df = pd.read_csv(os.path.join(DATA_DIR, "Nodes_Prompts.csv")).dropna(subset=["content"])
        prompts_df['text'] = "PROMPT:\n" + prompts_df['content']
    except Exception:
        prompts_df = pd.DataFrame(columns=["id", "text"])

    # Combine all into one DataFrame for unified processing
    all_texts = pd.concat([files_df[['id', 'text']], functions_df[['id', 'text']], prompts_df[['id', 'text']]])
    
    print(f"Total documents to process: {len(all_texts)}")
    
    loader = DataFrameLoader(all_texts, page_content_column="text")
    documents = loader.load()

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    print(f"Total chunks created: {len(splits)}")

    # Initialize HuggingFace Embeddings
    print("Initializing embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Chroma vector store...")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=CHROMA_DB_DIR)
    print(f"Vector DB successfully created at {CHROMA_DB_DIR}")

def get_vector_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

def run_llm_only(query: str, hf_token: str) -> str:
    """Run LLM-Only Baseline (Zero Context)"""
    client = InferenceClient("meta-llama/Meta-Llama-3.1-8B-Instruct", token=hf_token)
    prompt = f"User Query: {query}\n\nTrace the exact lineage and provide your analysis."
    response = client.text_generation(prompt, max_new_tokens=500)
    return response

def run_vector_rag(query: str, hf_token: str) -> str:
    """Run Basic Vector RAG Baseline"""
    retriever = get_vector_retriever()
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    client = InferenceClient("meta-llama/Meta-Llama-3.1-8B-Instruct", token=hf_token)
    prompt = f"Context:\n{context}\n\nUser Query: {query}\n\nAnswer the user query based ONLY on the provided context."
    response = client.text_generation(prompt, max_new_tokens=500)
    return response

if __name__ == "__main__":
    if not os.path.exists(CHROMA_DB_DIR):
        create_vector_db()
    else:
        print("Vector DB already exists.")
