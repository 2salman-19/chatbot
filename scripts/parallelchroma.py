import chromadb
from sentence_transformers import SentenceTransformer
import concurrent.futures


    # Perform parallel queries
class ParallelChromaQuery:
    def __init__(self, chroma_path):
        self.chroma_path = chroma_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def query_single_collection(self, collection_name, query_embedding):
        """Query a single collection to be used in parallel execution"""
        try:
            client = chromadb.PersistentClient(path=self.chroma_path)
            collection = client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=10,
                include=["documents", "metadatas", "distances"]
            )
            return (collection_name, results)
        except Exception as e:
            print(f"Error querying {collection_name}: {str(e)}")
            return (collection_name, None)
    
    def query_all_collections(self, collections, query_embedding):
        """Query multiple collections in parallel"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all queries at once
            future_to_collection = {
                executor.submit(self.query_single_collection, name, query_embedding): name
                for name in collections
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_collection):
                collection_name = future_to_collection[future]
                try:
                    name, result = future.result()
                    if result is not None:
                        results[name] = result
                except Exception as e:
                    print(f"Exception in {collection_name}: {str(e)}")
        
        return results