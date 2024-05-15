import re
from .abstract_tool import LLMTool
import weaviate

class VectorQuery(LLMTool):
    """Vector query tool using weaviate vector DB"""

    def __init__(self, weaviate_endpoint=None, weaviate_key=None, huggingface_key=None, n_results=3):
        if weaviate_endpoint and weaviate_key and huggingface_key:
            self.client = weaviate.Client(
                url = weaviate_endpoint,
                auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_key),
                additional_headers={
                    'X-HuggingFace-Api-Key': huggingface_key
                }
            )

        self.n_results=n_results
        self.last_query_results = None

    def get_system_prompt(self):
        tool_prompt="""Outil VectorQuery :
Vous disposez de l'outil VectorQuery. Utilisez VectorQuery dans les circonstances suivantes :
- L'utilisateur pose une question sur le droit Française
- L'utilisateur vous demande explicitement de rechercher quelque chose

L'outil VectorQuery dispose des commandes suivantes :
browse(query : str) Envoie une requête au moteur de recherche gouvx et affiche les résultats.
exemple d'utilisation : browse(query : "comment aller mieux ?")

A chaque question, demandez vous: est ce que cette question est à propos de la loi? Si oui utilisez l'outil.
"""

        return tool_prompt


    def trigger(self, line):
        pattern = r"^browse\((.*?)\)$"
        match = re.search(pattern, line)

        if match:
            arguments = match.group(1)
            arguments_dict = {}
            for arg in arguments.split(','):
                key, value = arg.strip().split(':')
                arguments_dict[key.strip()] = value.strip()
            
            return self.apply(arguments_dict)
        
        return ""

    def apply(self, args):
        query = args['query']

        response = query_db(self.client, text=query, n_results=self.n_results)
        self.last_query_results = response

        return parse_weaviate_response(response)


def query_db(client, text=None, embedding=None, n_results=3):
    query = (
       client.query
      .get("ServicePublic", ["text", "url", "title"])
    )

    if embedding:
        nearVector = {"vector": embedding}
        query = query.with_near_vector(nearVector)
    elif text:
       query = query.with_near_text({"concepts": [text]})
    else:
      raise ValueError('please provide ethier text or embedding')

    query = (
        query
        .with_limit(n_results)
        .with_additional(['certainty'])
    )

    response = query.do()

    if 'errors' in response["data"]["Get"].keys() and response["data"]["Get"]['errors'] is not None:
       raise RuntimeError('Weaviate error:', response["data"]["Get"]['errors'])    

    if not response or response["data"]["Get"]["ServicePublic"] is None:
        raise ValueError('The weaviate query returned no response')

    return response


def parse_weaviate_response(response):
    system_prompt = """

A l'aide de ces documents, répondre à la question de l'utilisateur:
- Si les documents ne permettent pas de repondre a la question de l'utilisateur, répondre que vous n'avez pas réussi à trouver de réponse
- Si nécessaire, mentionner les documents par leur numéro

Documents:
"""
    whole_paragraphs = {}
    for paragraph in response["data"]["Get"]["ServicePublic"]:
        title = paragraph["title"]
        content = paragraph.get("text", "")
        
        # Check if the title already exists, append the content if it does.
        if title in whole_paragraphs:
            whole_paragraphs[title] += "\n" + content
        else:
            whole_paragraphs[title] = content

    for i, (title, paragraph) in enumerate(whole_paragraphs.items(), start=1):
        system_prompt += f"\n\nDocument [{i}]: {title}\n{paragraph}"

    return system_prompt
