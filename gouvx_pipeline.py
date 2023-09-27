from vector_query import get_semantically_close_text
import openai

def get_prompt(client, question, query_results):
  text = f"""A partir des ces sites répondez aux questions en fin de document.
  La réponse devra être la plus claire et détaillée possible et se conformer à cette convention de nommage:

  Selon le site service-public.fr [...] [doc number]

  """

  if query_results:
    for i, result in enumerate(query_results, start=1):
      title = result["title"]
      url = result["url"]
      paragraph = get_semantically_close_text(question, client)

      text += f"""
      <a href="{url}">[{i}] {title} </a>:
      {paragraph}

      """

  text += f"Question: {question}"

  return text


def query_llm(prompt, history=None):
  messages = []
  
  if history:
    messages.extend(history)

  messages.append({
      "role": "user",
      "content": prompt
  })

  for chunk in openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages,
      stream=True,
  ):
      content = chunk["choices"][0].get("delta", {}).get("content")
      if content is not None:
          yield(content)


def ask_gouvx(question, client, model=None, n_results=1, history=None):
  if not history:
    response = get_semantically_close_text(question, client=client, model=model)

    if response and response["data"]["Get"]["ServicePublic"] is not None:
      query_results = response["data"]["Get"]["ServicePublic"][:n_results]
    else:
      raise ValueError('The weaviate query returned no response')

    prompt = get_prompt(client, question, query_results)
  else:
    query_results = ""
    prompt = question

  chatgpt_generator = query_llm(prompt, history)

  return prompt, query_results, chatgpt_generator
