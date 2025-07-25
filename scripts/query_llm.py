def query_llm(user_query):
    import os
    import chromadb
    from sentence_transformers import SentenceTransformer
    import requests

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
    collection = client.get_collection("jazz_packages")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # --- Embed and Retrieve ---
    query_embedding = model.encode([user_query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=15,
        include=["documents", "metadatas"]
    )
    # --- Build Context from Retrieved Packages ---
    retrieved_info = ""
    for doc in results["documents"][0]:
        retrieved_info += f"{doc}\n"



    # --- Construct Prompt for LLM ---
    prompt = (
        "You are a helpful assistant for Jazz, the mobile telecom company in Pakistan. "
        "You help users with information about Jazz's mobile packages (internet, SMS, call bundles, etc).\n"
        "Here are the top matching Jazz packages based on the user's question:\n"
        f"{retrieved_info}\n"
        f"User question: {user_query}\n"
        "Answer the user's question using only the information above. If the answer is not in the packages, say so politely."
    )
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "GROQ_API_KEY not set!"
    llm_model = "meta-llama/llama-4-scout-17b-16e-instruct"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": llm_model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
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

    print("change has been done")