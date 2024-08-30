import os
import re
import json
from ..prompt_builder import SystemPromptBuilder
from ..query_llm import query_llm
from ..agents.abstract_agent import AbstractAgent
from ..agents.tool_caller import ToolCaller
from ..tools.vector_query import VectorQuery

class GouvX(AbstractAgent):
    def __init__(self, sources):
        self.sources = sources
        self.PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        self.RAG_NRESULTS = int(os.getenv('RAG_NRESULTS', '3'))
        self.last_query_results = None

    def query(self, user_prompt, history=None, use_vllm=False):
        base_prompt = f"""Vous êtes GouvX, un assitant virtuel bienveillant et serviable permettant de naviguer les services du service public et répondre au question portant sur le droit civil, public ou privé.
Répondez précisément et clairement aux questions de l'utilisateur en respectant les règles suivantes:
- Ne JAMAIS inclure de lien
- Si une question ne porte pas sur les services du service public ou sur le droit civil, public ou privé, REFUSEZ DE REPONDRE et rappellez votre rôle
- En repondant à une question, respecter la convention de nommage: "Selon service-public.fr ..."
- Repondre en texte clair, sans balises ou marqueurs"""

        tools = [
            VectorQuery(pinecone_key=self.PINECONE_API_KEY, n_results=self.RAG_NRESULTS, sources=self.sources)
        ]

        # call the tool caller agent to make a decision
        tool_caller = ToolCaller(tools)
        tool_response = tool_caller.query(user_prompt=user_prompt)

        self.last_query_results = tool_response["data"]

        if tool_response["tool_name"]:
            print("used tool", tool_response["tool_name"], "args:", tool_response["args"])

        system_prompt = SystemPromptBuilder(base_prompt).build_system_prompt()
        
        if tool_response["prompt"]:
            system_prompt += tool_response["prompt"]

        if use_vllm:
            model = os.getenv('VLLM_MODEL')
        else:
            model = "gpt-3.5-turbo-16k"

        reply = query_llm(user_prompt=user_prompt,
                          system_prompt=system_prompt,
                          history=history,
                          model=model,
                          use_vllm=use_vllm)

        return reply
