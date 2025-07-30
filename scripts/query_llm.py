# def query_llm(user_query):
import os
import chromadb
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    markers = ['requirements.txt', 'README.MD']
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

project_root = get_project_root()
chroma_path = os.path.join(project_root, "data", "chroma_db")
client = chromadb.PersistentClient(path=chroma_path)
model = SentenceTransformer('all-MiniLM-L6-v2')

def combine_and_rank_results(all_results):
    """Combine and rank results based on relevance scores."""
    combine= {
        "documents": [],
        "metadatas": [],
        "distances": []
    }

    # fallten all results
    for result in all_results:
        combine["documents"].extend(result["documents"][0])
        combine["metadatas"].extend(result["metadatas"][0])
        combine["distances"].extend(result["distances"][0])
    # sort by distance (lower is better)
    sorted_indices = sorted(range(len(combine["distances"])), key=lambda i: combine["distances"][i])
    # reorder results
    for key in combine:
        combine[key] = [combine[key][i] for i in sorted_indices]
    return combine

def query_llm(user_query):
    load_dotenv()
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not set in environment variables")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not set!"
    """Query the LLM with the user's query and return the response."""""
    # --- Embed User Query ---
    query_embedding = model.encode([user_query])[0]
    # --- Query ChromaDB ---
    collections =['jazz_packages','propakistani_packages','ocr_packages']
    collection_results = []
    for collection_name in collections:
        try:
                collection = client.get_collection(name=collection_name)
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=10,
                    include=["documents", "metadatas", "distances"]
                )
                collection_results.append(results)
        except Exception as e:
            print(f"Error querying collection {collection_name}: {str(e)}")
            continue
    # --- Combine and Rank Results ---
    combined_results = combine_and_rank_results(collection_results)
    # --- Build Context with source information ---
    retrieved_info = ""
    for (doc, metadata) in zip(combined_results["documents"], combined_results["metadatas"]):
        source = metadata.get("source", "Unknown")
        retrieved_info += f"Source: {source}\n{doc}\n\n"



        # --- Construct Prompt for LLM ---
    prompt = (
        "You are JazzBot, a helpful assistant for Jazz, the mobile telecom company in Pakistan. "
        "Your job is to help users find the best mobile packages including internet, SMS, and call bundles.\n\n"
        "Here are the top relevant results from our database (including dummy, scraped, and OCR data):\n"
        f"{retrieved_info}\n\n"
        f"The user asked: \"{user_query}\"\n\n"
        "Based only on the information provided above, respond with a list of packages or information that matches the user's request. "
        "Mention the source (jazz_packages, scraped_data, or ocr_data) for each piece of information.\n\n"
        "If no exact matches are found, politely inform the user that no matching information was found."
    )
    llm_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "temperature": 0.5
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"