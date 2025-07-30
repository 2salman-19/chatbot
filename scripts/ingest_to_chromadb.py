from sentence_transformers import SentenceTransformer
import json
import numpy as np
import os

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    markers= ['requirements.txt', 'README.md', '.gitignore']
    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return os.path.dirname(os.path.dirname(__file__))

def ingest_to_chromadb(json_path, text_fn, emb_path, text_output_path):
    """
    processes the json file to generate embeddings and save texts.
    args:
         json_path: Path to input JSON file
        text_fn: Function to transform each JSON item to text
        emb_path: Path to save embeddings (.npy file)
        text_out_path: Path to save processed texts (JSON file)
    """
    print(f"Processing JSON file: {json_path}")

    # 1. Load packages
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            items = json.load(f)
    except Exception as e:
        print(f"Failed to load JSON file {json_path}: {e}")
        return

    # 2. Prepare texts
    texts= [text_fn(item) for item in items]
    print(f'simple text for {json_path}')
    for i, text in enumerate(texts[:2]):
        print(f"Text {i+1}, first 100 chars: {text[:100]}...")


    # 3. Load embedding model
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 4. Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"generate embeddings with shape: {embeddings.shape}")

# 5. Save embeddings and texts  (for ChromaDB or further use)
    try:
        np.save(emb_path, embeddings)
        with open (text_output_path, 'w', encoding='utf-8') as f:
            json.dump(texts, f, ensure_ascii=False, indent=2)
        print(f"save text to {text_output_path}")
        print(f"Embeddings saved to {emb_path}")
    except Exception as e:
        print(f"Error saving files : {str(e)}")

def main():
    project_root = get_project_root()
    data_dir = os.path.join(project_root, 'data')

    # 1. Jazz packages (dummy data)
    print("=== Processing Jazz Packages (Dummy Data) ===")
    ingest_to_chromadb(
        json_path=os.path.join(data_dir, 'jazz_packages.json'),
        text_fn=lambda pkg: (
            f"{pkg['Name']}. {pkg.get('Description', '')} "
            f"Validity: {pkg.get('Validity', '')}. "
            f"Price: {pkg.get('Price', '')}. "
            f"Activation Code: {pkg.get('Activation Code', '')}"
        ),
        emb_path=os.path.join(data_dir, 'jazz_package_embeddings.npy'),
        text_output_path=os.path.join(data_dir, 'jazz_package_texts.json')
    )
    
    # 2. Scraped packages (ProPakistani data)
    print("\n=== Processing Scraped Packages (ProPakistani Data) ===")
    ingest_to_chromadb(
        json_path=os.path.join(data_dir, 'propakistani_jazz_packages.json'),
        text_fn=lambda pkg: (
            f"{pkg['package_name']}. "
            f"On-Net: {pkg.get('onnet_mins', 'N/A')} mins, "
            f"Off-Net: {pkg.get('offnet_mins', 'N/A')} mins, "
            f"SMS: {pkg.get('sms', 'N/A')}, "
            f"Data: {pkg.get('data_mb', 'N/A')} MB, "
            f"Validity: {pkg.get('validity', 'N/A')}, "
            f"Price: {pkg.get('price_rs', 'N/A')} Rs, "
            f"Subscription: {pkg.get('subscription_code', 'N/A')}, "
            f"Category: {pkg.get('category', 'N/A')}"
        ),
        emb_path=os.path.join(data_dir, 'propakistani_package_embeddings.npy'),
        text_output_path=os.path.join(data_dir, 'propakistani_package_texts.json')
    )
    
    # 3. OCR packages (extracted from images)
    print("\n=== Processing OCR Packages (Extracted from Images) ===")
    ingest_to_chromadb(
        json_path=os.path.join(data_dir, 'extracted_packages.json'),
        text_fn=lambda pkg: (
            f"{pkg['extracted_data']['package_name']}. "
            f"Description: {'; '.join(pkg['extracted_data'].get('description', []))}. "
            f"Price: {pkg['extracted_data'].get('price', 'N/A')}"
        ),
        emb_path=os.path.join(data_dir, 'ocr_package_embeddings.npy'),
        text_output_path=os.path.join(data_dir, 'ocr_package_texts.json')
    )
    
    print("\n=== All Data Processing Complete ===")

if __name__ == "__main__":
    main()

