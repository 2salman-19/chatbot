# def query_llm(user_query):
import os
import requests
from dotenv import load_dotenv
from scripts.parallelchroma import query_all_collections_parallel, query_all_sequential_collections
from scripts.result_combiner import combine_and_rank_results
from scripts.duckWebSearch import search_jazz_with_bang, determine_source_type, remove_duplicate_results
from sentence_transformers import SentenceTransformer
from scripts.format_bang_results import format_bang_results
import chromadb

load_dotenv()

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    markers = ['requirements.txt', 'README.MD']
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
        
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def should_use_bang_search(query, database_results):
    """
    Determine if we should use bang search based on query and database results
    """
    # If no results from database
    if not database_results or not database_results.get("documents"):
        return True
    
    # Check for keywords indicating latest/current information
    latest_keywords = [
        'latest', 'current', 'new package', 'today', 'now', 'recent', 'updated',
        '2024', 'this month', 'this week', 'available now'
    ]
    
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in latest_keywords):
        return True
    
    # Check for specific package types not in database
    package_types = ['5g', '4g', 'unlimited', 'night', 'student', 'senior']
    if any(ptype in query_lower for ptype in package_types):
        # Check if database results contain these types
        db_text = ' '.join(database_results["documents"]).lower()
        if not any(ptype in db_text for ptype in package_types):
            return True
    
    return False

def query_llm(user_query):
    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY not set in environment variables")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not set!"

    project_root = get_project_root()
    chroma_path = os.path.join(project_root, "data", "chroma_db")

    # First, verify ChromaDB and collections exist
    try:
        client = chromadb.PersistentClient(path=chroma_path)
        available_collections = [col.name for col in client.list_collections()]
        print(f"Available collections: {available_collections}")
    except Exception as e:
        return f"Error connecting to ChromaDB: {str(e)}"
    
    # load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate query embedding
    query_embedding = model.encode([user_query])[0]

    # Define collections to query
    collections = ['jazz_packages', 'propakistani_packages', 'ocr_packages']
    
    # Filter to only include collections that exist
    existing_collections = [col for col in collections if col in available_collections]
    if not existing_collections:
        return "No valid collections found in ChromaDB."
    
    print(f"Querying existing collections: {existing_collections}")
    
    # Try parallel querying first
    print("Attempting parallel query...")
    collection_results_dict = query_all_collections_parallel(
        chroma_path, existing_collections, query_embedding, n_results=10
    )
    
    # If parallel query failed, try sequential
    if not collection_results_dict:
        print("Parallel query failed, trying sequential...")
        collection_results_dict = query_all_sequential_collections(
            chroma_path, existing_collections, query_embedding, n_results=10
        )
    
    # Convert dictionary values to list for combining
    collection_results = list(collection_results_dict.values())
    
    if not collection_results:
        return "I couldn't find any relevant information about Jazz packages in our database."
    
    # Combine and rank results
    combined_results = combine_and_rank_results(collection_results)

    # Build context with source information
    retrieved_info = ""
    for doc, metadata in zip(combined_results["documents"], combined_results["metadatas"]):
        source = metadata.get("source", "Unknown")
        retrieved_info += f"Source: {source}\n{doc}\n\n"
    
       # If no results found
    if not combined_results["documents"]:
        return "I couldn't find any relevant information about Jazz packages in our database."

    # Check if we should use bang search
    if should_use_bang_search(user_query, combined_results):
        print("Using DuckDuckGo bang search for latest packages...")
        bang_results = search_jazz_with_bang(user_query)
        
        if bang_results:
            # Format bang search results
            bang_info = format_bang_results(bang_results)
            retrieved_info += f"\n{bang_info}"
        else:
            retrieved_info += "\nNo recent packages found online.\n"
    
    # Construct prompt for LLM
    prompt = (
    "You are JazzBot, a helpful assistant for Jazz, the mobile telecom company in Pakistan. "
    "Your job is to help users find the best mobile packages including internet, SMS, and call bundles.\n\n"
    "Here are the top relevant results from our database and web search:\n"
    f"{retrieved_info}\n\n"
    f"The user asked: \"{user_query}\"\n\n"
    "Instructions:\n"
    "1. For packages from our database, mention the source (jazz_packages, propakistani_packages, or ocr_packages).\n"
    "2. For packages from web search, mention the source as 'Web Search' and include the specific source type (e.g., Official Jazz Website, ProPakistani) if provided.\n"
    "3. Always prioritize database results over web search results when both are available.\n"
    "4. If web search results are included, advise the user to verify the details on the official Jazz website as they may change.\n"
    "5. If no exact matches are found in either source, politely inform the user.\n\n"
    "Based on the information provided above, respond with a list of packages that match the user's request."
)

    llm_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7
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