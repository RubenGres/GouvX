from urllib.parse import urlparse
import requests
import difflib
import re

from flask import jsonify, Response

allowed_urls = [
    "service-public.fr",
    "legifrance.gouv.fr"
]


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def fix_links(match, url):
    attribute = match.group(1)
    link = match.group(2)
    if link.startswith(('http://', 'https://')):
        # Absolute links
        return f'{attribute}="/proxy?url={link}"'
    else:
        # Relative links
        base_url = get_base_url(url)
        new_link = base_url + link if link.startswith('/') else base_url + '/' + link
        return f'{attribute}="/proxy?url={new_link}"'


def fix_css_urls(match, url):
    link = match.group(1).strip('\'"')
    if link.startswith(('http://', 'https://')):
        # Absolute URLs
        return f'url("/proxy?url={link}")'
    else:
        # Relative URLs
        base_url = get_base_url(url)
        new_link = base_url + link if link.startswith('/') else base_url + '/' + link
        return f'url("/proxy?url={new_link}")'


def find_longest_match_substring(source_string, query):
    """
    Finds the longest *fuzzy* matching substring between the source string and the query string.
    
    Parameters:
    source_string (str): The string in which to search for the longest matching substring.
    query (str): The string to find the longest matching substring within the source string.
    
    Returns:
    tuple: A tuple (start_index, end_index) representing the start and end indices of the longest 
           matching substring in the source_string. If no match is found, returns None.
    """

    matcher = difflib.SequenceMatcher(None, source_string, query)
    match = matcher.find_longest_match(0, len(source_string), 0, len(query))
    
    if match.size != 0:
        return (match.a, match.a + match.size)
    else:
        return None


def proxy(url):
    url_pattern = re.compile(r'^https:\/\/(?:www\.)?((.*\.)?service-public\.fr|service-public\.fr|legifrance\.gouv\.fr)(?:\/.*)?$')

    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Check if the URL is from the allowed domains
    if not url_pattern.match(url):
        return jsonify({"error": "URL not allowed"}), 400

    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()

        # Sanitize the response content
        sanitized_content = re.sub(r'<script.*?>.*?</script>', '', response.text, flags=re.S)

        # Replace href, src, and srcset links
        final_html = re.sub(r'(href|src|srcset)=["\']([^"\']+)["\']', lambda x: fix_links(x, url), sanitized_content)

        # Replace CSS url() links
        final_html = re.sub(r'url\(["\']?([^"\')]+)["\']?\)', lambda x: fix_css_urls(x, url), final_html)

        return Response(final_html, content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error fetching the URL", "details": str(e)}), 500
    

def highlight_text_in_webpage(url, text_to_highlight):
    response = proxy(url)
    text = response.get_data(as_text=True)

    opening_tag = "<div style='background-color: yellow'>"
    closing_tag = "</div>"

    indexes = find_longest_match_substring(text, text_to_highlight)
    if not indexes:
        return response

    start, highlighted, end = text[:indexes[0]], text[indexes[0]:indexes[1]], text[indexes[1]:]
    response.set_data(start + opening_tag + highlighted + closing_tag + end)

    return response
