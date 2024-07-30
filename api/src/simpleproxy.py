from urllib.parse import urlparse
import requests
import difflib
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re
import pproxy
from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlparse
from threading import Thread
from bs4 import BeautifulSoup
import asyncio
from flask import jsonify, Response

allowed_urls = [
    "service-public.fr",
    "legifrance.gouv.fr"
]


def setup_proxy_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    handler = loop.run_until_complete(run_pproxy())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('exit!')

    handler.close()
    loop.run_until_complete(handler.wait_closed())
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

def setup():
    thread = Thread(target=setup_proxy_thread)
    thread.daemon = True
    thread.start()


async def run_pproxy():
    server = pproxy.Server('ss://0.0.0.0:1234')
    remote = pproxy.Connection('ss://1.2.3.4:5678')
    args = dict(rserver=[remote], verbose=print)

    handler = await server.start_server(args)
    return handler

def rewrite_links(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Convert relative URLs in 'a' tags
    for tag in soup.find_all('a', href=True):
        tag['href'] = f"/proxy?url={urljoin(base_url, tag['href'])}"

    # Convert relative URLs in 'img' tags
    for tag in soup.find_all('img', src=True):
        tag['src'] = f"/proxy?url={urljoin(base_url, tag['src'])}"

    # Convert relative URLs in 'link' tags
    for tag in soup.find_all('link', href=True):
        tag['href'] = f"/proxy?url={urljoin(base_url, tag['href'])}"

    # Convert relative URLs in 'script' tags
    for tag in soup.find_all('script', src=True):
        tag['src'] =  f"/proxy?url={urljoin(base_url, tag['src'])}"

    return str(soup)


def proxy(url):
    url_pattern = re.compile(r'^https:\/\/(?:www\.)?((.*\.)?service-public\.fr|service-public\.fr|legifrance\.gouv\.fr)(?:\/.*)?$')

    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Check if the URL is from the allowed domains
    if not url_pattern.match(url):
        return jsonify({"error": "URL not allowed"}), 400

    # Perform the request to the target URL
    resp = requests.get(url)
    content_type = resp.headers.get('Content-Type', '')

    print(content_type)

    # Rewrite links if the response is HTML
    if 'text/html' in content_type:
        base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
        rewritten_html = rewrite_links(resp.text, base_url)
        return Response(rewritten_html, content_type=content_type)
    else:
        return Response(resp.content, content_type=content_type)


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
