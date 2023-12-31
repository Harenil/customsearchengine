import requests
import os
from .scraping import scrape_and_store  # Import scrape_and_store here

# Retrieve API keys from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Searches Google Custom Search Engine using the provided keyword.
def search_google(keyword):
    search_url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={keyword}"
    response = requests.get(search_url)
    return response

def process_search_results(search_data, keyword):
    search_results = search_data.get('items', [])
    scrape_results = [process_search_result(result, keyword) for result in search_results]
    return {
        'raw_search_results': search_data,
        'scrape_results': scrape_results
    }

def process_search_result(result, keyword):
    url = result.get('link', '')
    scrape_store_result = scrape_and_store(url, keyword) if url else None
    return {
        'url': url,
        'status_code': scrape_store_result.get('status_code') if scrape_store_result else None,
        'error': scrape_store_result.get('error_message') if scrape_store_result else 'Scraping failed',
        'article_content_length': scrape_store_result.get('article_content_length') if scrape_store_result else 0,
        'article_content_dom_length': scrape_store_result.get('article_content_dom_length') if scrape_store_result else 0,
        'article_content_unstructured_length': scrape_store_result.get('article_content_unstructured_length') if scrape_store_result else 0,
        'article_content_unstructured_json': scrape_store_result.get('article_content_unstructured_json') if scrape_store_result else None,
        'row_id': scrape_store_result.get('row_id') if scrape_store_result else None
    }