import google.generativeai as genai
import requests
from src.config.configuration import Configuration


def call_gemini_api(api_key, model_name, context_=None, generation_config=None, safety_settings=None):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(contents=context_, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


def call_ollama_api(prompt, url: str = None, model: str = None) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")
