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
embedding_path = os.path.join(project_root, "data", "jazz_package_embeddings.npy")
text_path = os.path.join(project_root, "data", "jazz_package_texts.json")
print("Resolved project root:", project_root)
print("Embedding path:", embedding_path)
print("Text path:", text_path)
chroma_path = os.path.join(project_root, "data", "chroma_db")

client = chromadb.PersistentClient(path=chroma_path)
print("ChromaDB persist directory:", chroma_path)

embeddings = np.load(embedding_path)
with open(text_path, "r", encoding="utf-8") as f:
    texts = json.load(f)

collection = client.get_or_create_collection(name="jazz_packages")
ids = [f"pkg_{i}" for i in range(len(texts))]
metadatas = [{"text": text} for text in texts]

collection.add(
    embeddings=embeddings,
    documents=texts,
    metadatas=metadatas,
    ids=ids
)

print(f"Ingested {len(texts)} packages into ChromaDB 'jazz_packages' collection")
print("Collections in DB:", [c.name for c in client.list_collections()])







