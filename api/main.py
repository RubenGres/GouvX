from urllib.parse import urlparse
import requests
import logging
import json
import re

from flask import Flask, request, Response, stream_with_context, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

from src.agents.gouvx import GouvX
from src import simpleproxy

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def main():
    return "GouvX api is listening on route /ask"


@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    response = simpleproxy.proxy(url)
    return response


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
