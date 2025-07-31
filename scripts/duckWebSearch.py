# ----- web search script -----
# duckWebSearch.py
from ddgs import DDGS

import re

def search_jazz_with_bang(query, max_results=5):
    """
    Search for Jazz packages using DuckDuckGo bang commands
    
    Args:
        query (str): The user's search query
        max_results (int): Maximum number of results to return
    
    Returns:
        list: Search results with titles, snippets, and URLs
    """
    # Clean and enhance the query
    clean_query = clean_query_for_search(query)
    
    # Try multiple bang commands for comprehensive results
    site_queries = [
        f"site:jazz.com.pk {clean_query} package details",
        f"site:propakistani.pk {clean_query} jazz bundle",
        f"{clean_query} Jazz mobile internet plan Pakistan"
    ]

    all_results = []

    with DDGS() as ddgs:
        for q in site_queries:
            print(f"Searching with: {q}")
            try:
                results = ddgs.text(
                    q,
                    region='pk-en',
                    safesearch='moderate',
                    timelimit='y',
                    max_results=max_results
                )
                for result in results:
                    result['search_query'] = q
                    result['source_type'] = determine_source_type(q)
                all_results.extend(results)
            except Exception as e:
                print(f"Error with query '{q}': {e}")
                continue

    unique_results = remove_duplicate_results(all_results)
    return unique_results[:max_results]

def clean_query_for_search(query):
    """
    Clean and optimize the query for better search results
    """
    # Remove unnecessary words
    stop_words = ['tell', 'me', 'about', 'what', 'are', 'is', 'the', 'for']
    query_words = [word for word in query.split() if word.lower() not in stop_words]
    
    # Add package-related terms if not present
    if not any(word in query.lower() for word in ['package', 'offer', 'bundle', 'deal', 'international', 'city']):
        query_words.append('package')
    
    # Add location context if not present
    if not any(word in query.lower() for word in ['pakistan', 'jazz']):
        query_words.append('Pakistan')
    
    return ' '.join(query_words)

def determine_source_type(site_queries):
    """
    Determine the source type based on the site query used
    """
    if 'site:jazz.com.pk' in site_queries:
        return 'Official Jazz Website'
    elif 'site:propakistani.pk' in site_queries:
        return 'ProPakistani'
    else:
        return 'General Web'

def remove_duplicate_results(results):
    """
    Remove duplicate results based on URL or title similarity
    """
    seen_urls = set()
    unique_results = []
    
    for result in results:
        url = result.get('href', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    return unique_results