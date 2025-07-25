# Jazz Packages Conversational Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Jazz mobile packages (internet, SMS, call bundles, etc.), powered by ChromaDB for vector search and Groq LLM (Llama 3) for conversational, context-aware answers.

---

## Features
- **Semantic Search**: Find Jazz packages using natural language queries.
- **Conversational LLM**: Get human-like, context-aware answers in the terminal.
- **Retrieval-Augmented Generation**: Combines vector search with LLM for accurate, up-to-date responses.
- **Easy Data Updates**: Add or update packages and regenerate embeddings easily.
- **Interactive Terminal Chat**: Ongoing conversation until you type `exit`, `quit`, or `bye`.

---

## Setup Instructions

### 1. Clone the Repository
```bash
# Replace with your repo URL if public
git clone <your-repo-url>
cd jazz pakege chatbot
```

### 2. Python Environment
- Python 3.8+
- (Recommended) Use a virtual environment:
  ```bash
  python -m venv chatbot
  chatbot\Scripts\activate  # On Windows
  # or
  source chatbot/bin/activate  # On Linux/Mac
  ```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Set Up Groq API Key
- Get your API key from [Groq Console](https://console.groq.com/)
- Set it as an environment variable:
  ```powershell
  $env:GROQ_API_KEY="your-actual-groq-api-key"  # For current session (Windows PowerShell)
  # Or permanently (user-level):
  [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your-actual-groq-api-key", "User")
  ```

### 5. Prepare ChromaDB and Embeddings
- Make sure your Jazz package data is in `data/jazz_packages.json`.
- To (re)generate embeddings and ingest data:
  ```bash
  python scripts/ingest_to_chromadb.py
  ```
  This will create/update the ChromaDB vector store in `data/chroma_db/`.

---

## Running the Chatbot

```bash
python scripts/query_llm.py
```
- Type your question (e.g., "weekly packages", "give me 7 days packages details").
- Type `exit`, `quit`, or `bye` to end the chat.

---

## Example Usage

```
Ask about a Jazz package: weekly packages
Processing...
Jazz Weekly Mega. 7 GB Internet Validity: 7 Days. Price: Rs. 210. Activation Code: *159#
Jazz Custom Package 14. 1400 MBs + 140 SMS Validity: 7 Days. Price: Rs. 140. Activation Code: *114#
...

LLM Response:
Here are some Jazz weekly packages:
- Jazz Weekly Mega: 7 GB Internet, Validity: 7 Days, Price: Rs. 210, Activation Code: *159#
- Jazz Custom Package 14: 1400 MBs + 140 SMS, Validity: 7 Days, Price: Rs. 140, Activation Code: *114#
...
```


## Contributing
- Pull requests and issues are welcome!
- Please open an issue for bugs, feature requests, or questions.

**Enjoy your Jazz Packages Conversational Chatbot!**
