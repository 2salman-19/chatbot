# Jazz Packages Conversational Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for Jazz mobile packages (internet, SMS, call bundles, etc.), powered by ChromaDB for vector search and Groq LLM (Llama 3) for conversational, context-aware answers.

---

## Features

- **Semantic Search**: Find Jazz packages using natural language queries.
- **Conversational LLM**: Get human-like, context-aware answers in the terminal or web UI.
- **Retrieval-Augmented Generation**: Combines vector search with LLM for accurate, up-to-date responses.
- **Multi-source Data**: Ingests Jazz package data from PDF, OCR (images), and web scraping (ProPakistani).
- **Easy Data Updates**: Add or update packages and regenerate embeddings easily.
- **Interactive Chatbot**: Use in terminal or via a Streamlit web app.
- **web search** : if the user query dose not match with exist data collections then the web search will activate and get the results from the mentioned website with bangs duckduckgo library (ddg) 

---

## Project Structure

```
chatbot/
│
├── app/
│   └── streamlit_app.py         # Streamlit web app
│
├── data/
│   ├── jazz_packages.json       # Extracted from PDF
│   ├── propakistani_jazz_packages.json  # Scraped from ProPakistani
│   ├── extracted_packages.json  # Extracted from images (OCR)
│   ├── *_embeddings.npy         # Embeddings for each data source
│   ├── *_texts.json             # Texts for each data source
│   └── chroma_db/               # ChromaDB persistent storage
│
├── scripts/
│   ├── ingest_to_chromadb.py    # Ingests all data sources and generates embeddings
│   ├── chromaDB.py              # Loads embeddings/texts into ChromaDB collections
│   ├── query_llm.py             # Main chatbot logic (terminal & Streamlit)
│   ├── extract_pdf.py           # Extracts packages from PDF
│   ├── ocr.py                   # Extracts and parses packages from images
│   ├── propakistani_jazz_scraper.py # Scrapes packages from ProPakistani
│   └── ...                      # Other helpers/utilities
│
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd chatbot
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

### 5. Prepare Data and Embeddings

#### a. **Extract from PDF**
```bash
python scripts/extract_pdf.py
```
- Produces `data/jazz_packages.json`

#### b. **Extract from Images (OCR)**
- Place your screenshots in the correct folder (see `ocr.py`).
```bash
python scripts/ocr.py
```
- Produces `data/extracted_packages.json`

#### c. **Scrape from ProPakistani**
```bash
python scripts/propakistani_jazz_scraper.py
```
- Produces `data/propakistani_jazz_packages.json`

#### d. **Generate Embeddings for All Sources**
```bash
python scripts/ingest_to_chromadb.py
```
- Produces `.npy` and `.json` files for each source in `data/`

#### e. **Ingest into ChromaDB**
```bash
python scripts/chromaDB.py
```
- Loads all embeddings/texts into ChromaDB collections

---

## Running the Chatbot

### **Terminal Mode**
```bash
python scripts/query_llm.py
```
- Type your question (e.g., "weekly packages", "give me 7 days packages details").
- Type `exit`, `quit`, or `bye` to end the chat.

### **Web UI (Streamlit)**
```bash
streamlit run app/streamlit_app.py
```
- Open the provided local URL in your browser.
- Use the sidebar to ingest/update data or chat with the bot.

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

---

## Troubleshooting

- **ModuleNotFoundError**: Make sure you use `from scripts.xyz import ...` for local imports.
- **Circular Import**: Move shared functions to a utility module if needed.
- **ChromaDB Issues**: Delete the `data/chroma_db/` folder and re-run ingestion if you see DB errors.
- **API Key Errors**: Ensure `GROQ_API_KEY` is set in your environment.

---

## Contributing

- Pull requests and issues are welcome!
- Please open an issue for bugs, feature requests, or questions.

**Enjoy your Jazz Packages Conversational Chatbot!**
