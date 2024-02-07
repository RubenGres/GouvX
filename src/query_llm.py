import openai

def query_llm(user_prompt, system_prompt=None, history=None, model="gpt-4-turbo-preview"):
  """query the LLM, return a generator for each output token"""

  messages = []

  messages.append({
      "role": "system",
      "content": system_prompt
  })
  
  if history:
    messages.extend(history)

  messages.append({
      "role": "user",
      "content": user_prompt
  })

  for chunk in openai.ChatCompletion.create(
      model=model,
      messages=messages,
      stream=True,
  ):
      content = chunk["choices"][0].get("delta", {}).get("content", "")
      if content is not None:
          yield(content)
