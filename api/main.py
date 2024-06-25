from src.agents.gouvx import GouvX

from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from flask_socketio import SocketIO
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def main():
    return "GouvX api is listening on route /ask"

@app.route('/ask/', methods=['POST'])
def ask():
    user_prompt = request.form['question']
    sources = request.form['sources']
    sources = sources.split(",")
    
    history = request.form['history']
    history = json.loads(history)    

    gouvx_agent = GouvX(sources)

    try:
        if len(history) > 10:
            raise ValueError("conversation too long")
        
        llm_generator = gouvx_agent.query(user_prompt, history=history)
        query_results = gouvx_agent.last_query_results
    except ValueError:
        query_results = [None]
        llm_generator = (lambda _: "Désolé mais j'ai atteint mon quota de réponses pour cette conversation")("")

    def response_stream(chatgpt_generator, query_results=None):
        yield json.dumps(query_results if query_results else []).encode('utf-8')
        yield "\n".encode('utf-8')
        for line in chatgpt_generator:
            yield line.encode('utf-8')

    print("user:", request.remote_addr, "prompt:", user_prompt, "requires_search:", query_results is not None )
    return Response(stream_with_context(response_stream(llm_generator, query_results)), mimetype='text/plain', direct_passthrough=True)
