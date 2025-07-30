# result_combiner.py
def combine_and_rank_results(all_results):
    """Combine and rank results from multiple collections"""
    combined = {
        "documents": [],
        "metadatas": [],
        "distances": []
    }
    
    # Flatten results from all collections
    for result in all_results:
        if "documents" in result and result["documents"]:
            combined["documents"].extend(result["documents"][0])
            combined["metadatas"].extend(result["metadatas"][0])
            combined["distances"].extend(result["distances"][0])
    
    # Sort by distance (lower is better)
    if combined["distances"]:
        sorted_indices = sorted(range(len(combined["distances"])), key=lambda i: combined["distances"][i])
        
        # Reorder all lists
        for key in combined:
            combined[key] = [combined[key][i] for i in sorted_indices]
    
    return combined