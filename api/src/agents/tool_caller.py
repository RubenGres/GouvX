import os
import json
from ..tools.vector_query import VectorQuery
from ..prompt_builder import SystemPromptBuilder
from ..query_llm import query_llm
from ..agents.abstract_agent import AbstractAgent

class ToolCaller(AbstractAgent):
    def __init__(self, tools_instances):
        self.tool_instances = tools_instances
        
    def query(self, user_prompt):
        base_prompt = """Vous pouvez lancer différents outils. Répondez selon ce format en json: 
{
    "tool": Nom de la fonction à appeller ou None,
    "args": kwargs de la fonction
}

Utilisez le meilleur outil à votre disposition pour répondre au mieux à la question de l'utilisateur. Si aucun outil n'est necessaire, renvoyer None dans chaque champ.

Exemples:
{
    "tool": "browse",
    "args": {
        "query": "latest AI trends in 2024"
    }
}

{
    "tool": None,
    "args": None
}
"""

        system_prompt = SystemPromptBuilder(base_prompt).build_system_prompt(self.tool_instances)

        reply = query_llm(user_prompt=user_prompt, system_prompt=system_prompt, history=None, response_format={ "type": "json_object" })

        response = "".join(list(reply))

        # Parse the JSON
        data = json.loads(response)

        # Extract the tool and arguments
        tool_name = data['tool']
        args = data['args']

        tool_response = self.use_tool(tool_name, args)
        
        tool_reponse = {
            "tool_name": tool_name,
            "args": args,
            "prompt": tool_response["prompt"],
            "data": tool_response["data"]
        }

        return tool_reponse

    def use_tool(self, tool_name, args):
        for tool_instance in self.tool_instances:
            if tool_instance.name == tool_name:
                return tool_instance.apply(args)
            
        return {
            "prompt": None,
            "data": None
        }
