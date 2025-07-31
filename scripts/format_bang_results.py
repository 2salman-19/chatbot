def format_bang_results(results):
    """
    Format DuckDuckGo bang search results for LLM consumption
    """
    if not results:
        return "No recent packages found online."
    
    formatted = "Latest packages found online:\n\n"
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        snippet = result.get('body', 'No summary available')
        url = result.get('href', 'No URL')
        source_type = result.get('source_type', 'Unknown source')
        
        formatted += f"{i}. {title}\n"
        formatted += f"   Summary: {snippet}\n"
        formatted += f"   Source: {source_type}\n"
        formatted += f"   URL: {url}\n\n"
    
    formatted += "Note: These results are from online searches and may be more current than our database. "
    formatted += "Please verify details on the official Jazz website.\n"
    
    return formatted