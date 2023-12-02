from flask import Flask, request, jsonify, render_template
import requests
import logging
from searchengine.database import get_db_connection, create_tables, store_scraped_content
from searchengine.scraping import fetch_page, scrape_content
#from .scraping import scrape_and_store
from .search import process_search_results
from searchengine.search import (
    search_google,
    GOOGLE_API_KEY,
    GOOGLE_CSE_ID,
    process_search_results  # Import the function here
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('search_page.html')

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': 'Missing search keyword'}), 400

    search_url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={keyword}"
    response = requests.get(search_url)

    if response.status_code == 200:
        search_results = process_search_results(response.json(), keyword)
        return jsonify(search_results)
    else:
        return jsonify({'error': 'Failed to fetch search results'}), response.status_code

@app.route('/content/<int:row_id>', methods=['GET'])
def get_content(row_id):
    with get_db_connection() as conn:
        content = conn.execute('SELECT article_content, article_content_dom FROM headings WHERE id = ?', (row_id,)).fetchone()
        if content:
            return jsonify({
                'article_content': content['article_content'],
                'article_content_dom': content['article_content_dom']
            })
        else:
            return jsonify({'error': 'Content not found'}), 404

# Initialize database at startup
create_tables()

if __name__ == '__main__':
    app.run(debug=True)