import os
from openai import OpenAI

def get_openai_client(use_vllm=False):
    if not use_vllm:
       return OpenAI(api_key=os.environ.get("OPENAI_KEY"))
    
    RUNPOD_VLLM_ID = os.environ.get("RUNPOD_VLLM_ID")

    return OpenAI(
        api_key=os.environ.get("RUNPOD_API_KEY"),
        base_url=f"https://api.runpod.ai/v2/{RUNPOD_VLLM_ID}/openai/v1",
    )

def query_llm(user_prompt, system_prompt=None, history=None, model="gpt-4-turbo-preview", use_vllm=False):
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

    client = get_openai_client(use_vllm)    

    for chunk in client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    ):
        content = chunk.choices[0].delta.content
        if content is not None:
            yield(content)
