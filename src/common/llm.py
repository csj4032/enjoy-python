import google.generativeai as genai
import requests
from typing import Optional, Dict, Any
from src.config.configuration import Configuration


def call_gemini_api(api_key: str, model_name: str, context_: Optional[str] = None, generation_config: Optional[Dict[str, Any]] = None, safety_settings: Optional[Dict[str, Any]] = None) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(contents=context_, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


def call_ollama_api(prompt: str, url: Optional[str] = None, model: Optional[str] = None) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")
