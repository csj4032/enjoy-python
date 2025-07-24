import google.generativeai as genai
import requests


def call_gemini_api(api_key: str, model_name: str, context_: str | None = None, generation_config: dict[str, any] | None = None, safety_settings: dict[str, any] | None = None) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(contents=context_, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


def call_ollama_api(prompt: str, url: str | None = None, model: str | None = None) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")
