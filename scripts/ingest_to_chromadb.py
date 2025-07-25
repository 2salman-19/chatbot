def ingest_to_chromadb():
    from sentence_transformers import SentenceTransformer
    import json
    import numpy as np

    # 1. Load packages
    with open('../data/jazz_packages.json', 'r', encoding='utf-8') as f:
        packages = json.load(f)

    # 2. Prepare texts
    texts = [
        f"{pkg['Name']}. {pkg.get('Description', '')} Validity: {pkg.get('Validity', '')}. Price: {pkg.get('Price', '')}. Activation Code: {pkg.get('Activation Code', '')}"
        for pkg in packages
    ]
    print(texts)

    # 3. Load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 4. Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)

    # 5. Save embeddings and metadata (for ChromaDB or further use)
    np.save('../data/jazz_package_embeddings.npy', embeddings)
    with open('../data/jazz_package_texts.json', 'w', encoding='utf-8') as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)


    print("Shape:", embeddings.shape)
    print("First embedding vector (truncated):", embeddings[0][:10])  # Show first 10 values of the first vector
    print("First 3 embeddings (truncated):", embeddings[:3, :10])     # Show first 3 vectors, first 10 values each
    print("number of text ", len(texts))
    print("number of embeddings ", len(embeddings))

