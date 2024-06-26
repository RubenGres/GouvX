from typing import List
import requests
import os

def embed_text(text: List[str]) -> List[List[float]]:
    RUNPOD_INFINITY_ID = os.environ["RUNPOD_INFINITY_ID"]
    RUNPOD_API_KEY = os.environ["RUNPOD_API_KEY"]

    url = f"https://api.runpod.ai/v2/{RUNPOD_INFINITY_ID}/runsync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }

    payload = {
        "input": {
            "model": "dangvantuan/sentence-camembert-large",
            "input": text
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    response = response.json()

    embeddings = []

    for datapoint in response["output"]["data"]:
        embeddings.append(datapoint["embedding"])

    return embeddings
