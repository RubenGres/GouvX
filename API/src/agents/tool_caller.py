import os
from ..tools.vector_query import VectorQuery
from ..prompt_builder import SystemPromptBuilder
from ..query_llm import query_llm
from ..agents.abstract_agent import AbstractAgent

class ToolCaller(AbstractAgent):
    def __init__(self):
        pass

    def query(self, user_prompt):
        base_prompt = f"""Vous êtes un assitant permettant de lancer différents outils. Répondez selon ce format: 
    need_tool: "True" si la question necessie une recherche, "False" sinon
    function_call: Appel aux fonctions des outils à disposition (ex: browse(query: "Remboursement dette publique"))

exemples de retour:
    need_tool: False
    function_call: None

    need_tool: True
    function_call: browse("remboursement sécurité sociale")
        """

        prompt_builder = SystemPromptBuilder(base_prompt)

        query_tool = VectorQuery()

        system_prompt = prompt_builder.build_system_prompt([query_tool])

        reply = query_llm(user_prompt=user_prompt, system_prompt=system_prompt, history=None)

        return "".join(list(reply))
