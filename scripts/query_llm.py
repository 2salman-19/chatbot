# def query_llm(user_query):
import os
import requests
from dotenv import load_dotenv
from scripts.parallelchroma import ParallelChromaQuery
from scripts.result_combiner import combine_and_rank_results

load_dotenv()

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    markers = ['requirements.txt', 'README.MD']
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def query_llm(user_query):
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not set in environment variables")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not set!"

    project_root = get_project_root()
    chroma_path = os.path.join(project_root, "data", "chroma_db")
    
    # Initialize parallel query system
    parallel_query = ParallelChromaQuery(chroma_path)
    
    # Define collections to query
    collections = ['jazz_packages', 'propakistani_packages', 'ocr_packages']
    
    # Generate query embedding
    query_embedding = parallel_query.model.encode([user_query])[0]
    
    # Query all collections in parallel
    print("Querying collections in parallel...")
    collection_results = parallel_query.query_all_collections(collections, query_embedding)
    
    # Convert results to list for combining
    results_list = list(collection_results.values())
    
    if not results_list:
        return "I couldn't find any relevant information about Jazz packages in our database."
    
    # Combine and rank results
    combined_results = combine_and_rank_results(results_list)
    
    # Build context with source information
    retrieved_info = ""
    for doc, metadata in zip(combined_results["documents"], combined_results["metadatas"]):
        source = metadata.get("source", "Unknown")
        retrieved_info += f"Source: {source}\n{doc}\n\n"
    
    # Construct prompt for LLM
    prompt = (
        "You are JazzBot, a helpful assistant for Jazz, the mobile telecom company in Pakistan. "
        "Your job is to help users find the best mobile packages including internet, SMS, and call bundles.\n\n"
        "Here are the top relevant results from our database:\n"
        f"{retrieved_info}\n\n"
        f"The user asked: \"{user_query}\"\n\n"
        "Based only on the information provided above, respond with a list of packages that match the user's request. "
        "Mention the source (jazz_packages, propakistani_packages, or ocr_packages) for each package.\n\n"
        "If no exact matches are found, politely inform the user that no matching packages were found."
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