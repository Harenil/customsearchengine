import requests
from bs4 import BeautifulSoup
import re
import logging
from .database import store_scraped_content
from unstructured.partition.html import *
from unstructured.documents.elements import *
from unstructured.partition.auto import *
import json
from unstructured.cleaners.core import *

def fetch_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'}
    return requests.get(url, headers=headers)

def scrape_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    article_content = extract_content_with_selectors(soup)
    article_content_dom = find_main_content_by_dom_traversal(soup)
    return article_content, article_content_dom

def extract_content_with_selectors(soup):
    content_selectors = [
        'article',
        '.post',
        '.entry-content',
        '#main',
        'main',
        '.article-content',
        '.post-content',
        '.content',
        '.post-entry',
        '.text',
        '#content',
        '.blog-post',
        '.story',
        '.article-body',
        '.post-body',
        '.entry',
        '.article-text',
        # Add more selectors as needed
    ]
    
    article_content = None
    first_h1 = soup.find('h1')
    for selector in content_selectors:
        content = soup.select_one(selector)
        if content:
            if first_h1 and first_h1.find_previous_sibling() is None:
                article_content = str(first_h1) + str(content)
            else:
                article_content = str(content)
            break

    if not article_content and first_h1:
        article_content = str(first_h1) + ''.join(map(str, first_h1.find_all_next(string=True)))
        end_of_content_markers = ['footer', '.footer', '#footer', 'aside', '.related', '.author-bio']
        for marker in end_of_content_markers:
            end_content = soup.select_one(marker)
            if end_content:
                article_content = article_content.split(str(end_content), 1)[0]
                break

    if article_content:
        article_content = BeautifulSoup(article_content, 'html.parser').get_text(separator=' ', strip=True)
        article_content = re.sub(r'(?is)<script.*?>.*?</script>', '', article_content)

    return article_content

def find_main_content_by_dom_traversal(soup):
    max_paragraphs = 0
    main_content_candidate = None
    for elem in soup.find_all(['div', 'article', 'section', 'main']):
        paragraph_count = len(elem.find_all('p'))
        if paragraph_count > max_paragraphs:
            max_paragraphs = paragraph_count
            main_content_candidate = elem

    if main_content_candidate:
        main_content_candidate = BeautifulSoup(str(main_content_candidate), 'html.parser').get_text(separator=' ', strip=True)
        main_content_candidate = re.sub(r'(?is)<script.*?>.*?</script>', '', main_content_candidate)

    return main_content_candidate

def extract_headings(content):
    soup = BeautifulSoup(content, 'html.parser')
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    headings_data = [{'text': heading.get_text(strip=True), 'level': heading.name} for heading in headings]
    return headings_data

def scrape_and_store(url, keyword):
    try:
        page_response = fetch_page(url)
        if page_response.status_code == 200:
            article_content, article_content_dom = scrape_content(page_response.text)
            headings = extract_headings(page_response.text)  # Extract headings from the content
            article_content_unstructured_json = scrape_with_unstructured(url)  # Scrape with unstructured library and get JSON
            return store_scraped_content(url, keyword, article_content, article_content_dom, headings, article_content_unstructured_json)  # Pass JSON to store function
        else:
            return {
                'status_code': page_response.status_code,
                'error_message': page_response.reason,
                'article_content_length': 0,
                'article_content_dom_length': 0,
                'article_content_unstructured_length': 0,  # Include length of unstructured content
                'article_content_unstructured_json': None,  # Include JSON of unstructured content
                'row_id': None
            }
    except Exception as e:
        logging.exception(f"An error occurred while scraping {url}")
        return {
            'status_code': 0,
            'error_message': str(e),
            'article_content_length': 0,
            'article_content_dom_length': 0,
            'article_content_unstructured_length': 0,  # Include length of unstructured content
            'article_content_unstructured_json': None,  # Include JSON of unstructured content
            'row_id': None
        }
        
def scrape_with_unstructured(url):
    try:
        # Custom headers with a user-agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'
        }
        elements = partition_html(url=url, html_assemble_articles=True, headers=headers)

        sections = []
        current_section = None

        for el in elements:
            if isinstance(el, Title) and el.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Start a new section for each title
                current_section = {"type": el.tag, "title": str(el), "content": {}}
                sections.append(current_section)
            elif current_section is not None:
                # Add content to the current section
                el_tag = el.tag if el.tag else 'other'
                if el_tag not in current_section["content"]:
                    current_section["content"][el_tag] = []
                current_section["content"][el_tag].append(clean_non_ascii_chars(clean(replace_unicode_quotes(str(el)), extra_whitespace=True)))

        return json.dumps(sections)  # Convert the list of sections to JSON string
    except ValueError as e:
        # Print custom error message without traceback
        print(f"An error occurred while scraping {url} with unstructured: {e}")
        return None
    except Exception as e:
        # Handle other exceptions that might occur
        print(f"An unexpected error occurred while scraping {url} with unstructured: {e}")
        return None
