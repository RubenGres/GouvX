import re
from .abstract_tool import LLMTool
from ..call_embedder import embed_text
from pinecone import Pinecone, ServerlessSpec


class VectorQuery(LLMTool):
    """Vector query tool using vector DB"""

    def __init__(self, pinecone_key=None, n_results=3, sources=None):
        if pinecone_key:
            self.client = Pinecone(api_key=pinecone_key)

        self.n_results=n_results
        self.sources = sources
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

        response = self.query_db(text=query, n_results=self.n_results, sources=self.sources)
        self.last_query_results = response

        system_prompt = """

        A l'aide de ces documents, répondre à la question de l'utilisateur:
        - Si les documents ne permettent pas de repondre a la question de l'utilisateur, répondre que vous n'avez pas réussi à trouver de réponse
        - Si nécessaire, mentionner les documents par leur numéro

        Documents:
        """

        whole_paragraphs = {}
        for match in response:
            title = match["url"]
            content = match.get("content", "")
            
            # Check if the title already exists, append the content if it does.
            if title in whole_paragraphs:
                whole_paragraphs[title] += "\n" + content
            else:
                whole_paragraphs[title] = content

        for i, (title, paragraph) in enumerate(whole_paragraphs.items(), start=1):
            system_prompt += f"\n\nDocument [{i}]: {title}\n{paragraph}"

        return system_prompt


    def query_db(self, text=None, embedding=None, n_results=3, sources=None):
        index = self.client.Index("gouvx")

        if text and embedding:
            raise ValueError('please provide only one of text or embedding')

        if text:
            embedding = embed_text(text)[0]

        results = {}
        for source in sources:
            partial_result = index.query(
                namespace=source,
                vector=embedding,
                top_k=n_results,
                include_metadata=True
            )

            results[source] = partial_result

        formatted_results = []
        for source, partial_result in results.items():
            for match in partial_result["matches"]:
                title = match["metadata"]["title"]
                url = match["metadata"]["url"]
                content = match["metadata"].get("text", "")

                formatted_results.append({                    
                    "title": title,
                    "url": url,
                    "source": source,
                    "content": content
                })

        #TODO rerank results by score or using runpod infinity api

        return formatted_results
