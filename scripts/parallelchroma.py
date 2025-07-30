import chromadb
from sentence_transformers import SentenceTransformer
import concurrent.futures
import os
import time



def query_single_collection(chroma_path, collection_name, query_embedding, n_results=10):
    """Query a single collection to be used in parallel execution"""
    try:
        # create a new clint for each thread
        client = chromadb.PersistentClient(path=chroma_path)
        # check if the collection exists
        try:
            collection = client.get_collection(name=collection_name)
        except Exception as e:
            print(f"Collection '{collection_name}' not found.")
            return (collection_name, None)
        # Query the collection
        results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
        return (collection_name, results)
    except Exception as e:
        print(f"Error querying {collection_name}: {str(e)}")
        return (collection_name, None)

def query_all_collections_parallel(chroma_path, collections, query_embedding, n_results=10):
        """Query multiple collections in parallel"""
        results = {}
        # verify chromaDB path exists
        if not os.path.exists(chroma_path):
            print(f"ChromaDB path '{chroma_path}' does not exist.")
            return results
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            # Submit all queries at once
            future_to_collection = {
                executor.submit(query_single_collection, chroma_path, name, query_embedding, n_results): name
                for name in collections
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_collection):
                collection_name = future_to_collection[future]
                try:
                    name, result = future.result()
                    if result is not None:
                        results[name] = result
                        print(f"Successfully queried {collection_name}")
                except Exception as e:
                    print(f"Exception in {collection_name}: {str(e)}")
        
        return results

def query_all_sequential_collections(chroma_path, collections, query_embedding, n_results=10):
    """fallback sequential query method"""
    results = {}
    try:
        client = chromadb.PersistentClient(path=chroma_path)
    except Exception as e:
        print(f"Error connecting to ChromaDB client: {str(e)}")
        return results
    # Get available collections
    try:
        available_collections = [col.name for col in client.list_collections()]
        print(f"Available collections: {available_collections}")
    except Exception as e:
        print(f"Error listing collections: {str(e)}")
        return results
    
    # Query each collection
    for collection_name in collections:
        if collection_name not in available_collections:
            print(f"Collection {collection_name} not found, skipping...")
            continue
        
        try:
            collection = client.get_collection(name=collection_name)
            result = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            results[collection_name] = result
            print(f"Successfully queried {collection_name}")
        except Exception as e:
            print(f"Error querying {collection_name}: {str(e)}")
            continue
    
    return results