from urllib.parse import urlparse
import requests
import logging
import json
import re

from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from src.agents.gouvx import GouvX

url_pattern = re.compile(r'^https:\/\/(?:www\.)?((.*\.)?service-public\.fr|service-public\.fr|legifrance\.gouv\.fr)(?:\/.*)?$')

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def main():
    return "GouvX api is listening on route /ask"


@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')

    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Check if the URL is from the allowed domains
    if not url_pattern.match(url):
        return jsonify({"error": "URL not allowed"}), 400

    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()

        def get_base_url(url):
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base_url

        # Redirects links to the proxy
        def fix_links(match):
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

        def fix_css_urls(match):
            link = match.group(1).strip('\'"')
            if link.startswith(('http://', 'https://')):
                # Absolute URLs
                return f'url("/proxy?url={link}")'
            else:
                # Relative URLs
                base_url = get_base_url(url)
                new_link = base_url + link if link.startswith('/') else base_url + '/' + link
                return f'url("/proxy?url={new_link}")'

        # Sanitize the response content
        sanitized_content = re.sub(r'<script.*?>.*?</script>', '', response.text, flags=re.S)
        sanitized_content = response.text

        # Replace href, src, and srcset links
        final_html = re.sub(r'(href|src|srcset)=["\']([^"\']+)["\']', fix_links, sanitized_content)

        # Replace CSS url() links
        final_html = re.sub(r'url\(["\']?([^"\')]+)["\']?\)', fix_css_urls, final_html)

        return Response(final_html, content_type=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Error fetching the URL", "details": str(e)}), 500

@app.route('/ask/', methods=['POST'])
def ask():
    user_prompt = request.form['question']

    use_vllm = request.form['use_vllm'] == "True"

    sources = request.form['sources']
    sources = sources.split(",")
    
    history = request.form['history']
    history = json.loads(history)    

    gouvx_agent = GouvX(sources)

    def response_stream(chatgpt_generator, query_results=None):
        yield json.dumps(query_results if query_results else []).encode('utf-8')
        yield "\n".encode('utf-8')
        for line in chatgpt_generator:
            yield line.encode('utf-8')

    try:
        if len(history) > 20:
            raise ValueError("conversation too long")
        
        llm_generator = gouvx_agent.query(user_prompt, history=history, use_vllm=use_vllm)
        query_results = gouvx_agent.last_query_results
    except ValueError:
        query_results = [None]
        llm_generator = (lambda _: "Il y a eu une erreur, merci de réessayer plus tard")("")
        logging.error("An error occurred", exc_info=True)

    print("user:", request.remote_addr, " prompt:", user_prompt, " requires_search:", query_results is not None, " use_vllm:", use_vllm)
    return Response(stream_with_context(response_stream(llm_generator, query_results)), mimetype='text/plain', direct_passthrough=True)

if __name__ == "__main__":
    app.run(debug=True)
