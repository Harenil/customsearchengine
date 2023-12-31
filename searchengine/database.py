import sqlite3
import os
import json
from contextlib import contextmanager

# Set the base directory for the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'headings.sqlite')
print(f"Database path: {DATABASE}")
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    with get_db_connection() as conn:
        try:
            conn.execute('''CREATE TABLE IF NOT EXISTS headings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            keyword TEXT,
                            url TEXT NOT NULL,
                            article_content TEXT,
                            article_content_dom TEXT,
                            article_content_unstructured TEXT,
                            article_content_unstructured_json TEXT,
                            headings_json TEXT
                        )''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while creating tables: {e}")

def store_scraped_content(url, keyword, article_content, article_content_dom, headings, article_content_unstructured_json):
    headings_json = json.dumps(headings)
    article_content_length = len(article_content) if article_content else 0
    article_content_dom_length = len(article_content_dom) if article_content_dom else 0
    article_content_unstructured_length = len(json.loads(article_content_unstructured_json)) if article_content_unstructured_json else 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM headings WHERE url = ?', (url,))
        existing_row = cursor.fetchone()

        if existing_row:
            cursor.execute('''
                UPDATE headings
                SET article_content = ?, article_content_dom = ?, article_content_unstructured = ?, article_content_unstructured_json = ?, headings_json = ?, keyword = ?
                WHERE id = ?
            ''', (article_content, article_content_dom, article_content_unstructured_json, article_content_unstructured_json, headings_json, keyword, existing_row['id']))
            row_id = existing_row['id']
        else:
            cursor.execute('''
                INSERT INTO headings (url, article_content, article_content_dom, article_content_unstructured, article_content_unstructured_json, headings_json, keyword)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, article_content, article_content_dom, article_content_unstructured_json, article_content_unstructured_json, headings_json, keyword))
            row_id = cursor.lastrowid

        conn.commit()
        return {
            'status_code': 200,
            'error_message': None,
            'article_content_length': article_content_length,
            'article_content_dom_length': article_content_dom_length,
            'article_content_unstructured_length': article_content_unstructured_length,
            'article_content_unstructured_json': article_content_unstructured_json,
            'row_id': row_id
        }
