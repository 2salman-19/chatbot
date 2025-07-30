import os
import chromadb
import numpy as np
import json

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

def ingest_collection(collection_name, embedding_file, text_file):
    """Generalized function to ingest data into a ChromaDB collection"""
    try:
        embeddings = np.load(embedding_file)
        with open(text_file, "r", encoding="utf-8") as f:
            texts = json.load(f)

        collection = client.get_or_create_collection(name=collection_name)
        ids = [f"{collection_name}_{i}" for i in range(len(texts))]
        metadatas = [{"text": text, "source": collection_name} for text in texts]

        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingested {len(texts)} documents into collection '{collection_name}'")
        return True
    except Exception as e:
        print(f"Error ingesting {collection_name}: {str(e)}")
        return False


# collections for dummy data
print("=== Ingesting Dummy Data Collections ===")
ingest_collection(
    collection_name="jazz_packages",
    embedding_file=os.path.join(project_root, "data", "jazz_package_embeddings.npy"),
    text_file=os.path.join(project_root, "data", "jazz_package_texts.json")
)
# collections for scrape ProPakistani data
print("=== Ingesting ProPakistani Data Collections ===")
ingest_collection(
    collection_name="propakistani_packages",
    embedding_file=os.path.join(project_root,"data", "propakistani_package_embeddings.npy"),
    text_file=os.path.join(project_root, "data", "propakistani_package_texts.json")
)
# collections for OCR data
print("=== Ingesting OCR Data Collections ===")
ingest_collection(
    collection_name="ocr_packages",
    embedding_file=os.path.join(project_root, "data", "ocr_package_embeddings.npy"),
    text_file=os.path.join(project_root, "data", "ocr_package_texts.json")
)





