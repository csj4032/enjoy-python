import logging
import random
import time
from urllib.parse import urlparse, parse_qs

import google.generativeai as genai
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.configuration import Configuration


def setup_firefox_driver(configuration: Configuration):
    options = FirefoxOptions()
    options.add_argument("--window-size=480,1480")
    options.set_preference("general.useragent.override", configuration.iphone_user_agent)
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


def setup_firefox_profile_driver(configuration: Configuration):
    options = FirefoxOptions()
    options.add_argument("-profile")
    options.add_argument(configuration.firefox_profile_path)
    options.add_argument(f"--window-size=480,1480")
    options.set_preference("general.useragent.override", configuration.iphone_user_agent)
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


def setup_edge_profile_driver(configuration: Configuration):
    options = EdgeOptions()
    options.add_argument(f"--user-data-dir={configuration.edge_profile_path}")
    options.add_argument(f"profile-directory=Profile 3")
    options.add_argument(f"--window-size=480,1480")
    service = EdgeService(executable_path="/usr/local/bin/msedgedriver")
    return webdriver.Edge(service=service, options=options)


def window_scroll(driver_, range_, x_coord, y_coord, scroll_random_start_time=0, scroll_random_end_time=10, link=""):
    for index_ in range(range_):
        logging.info(f"Scrolling {index_ + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))


def window_scroll_more(driver_, range_, x_coord, y_coord, selector="button.button_show__VRCFg", scroll_random_start_time=0, scroll_random_end_time=10, link=""):
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            more_button = WebDriverWait(driver_, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            more_button.click()
            logging.info(f"Clicked more button {index + 1}/{range_} times. link : {link}")
            time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))
        except TimeoutException:
            pass


def window_scroll_top(driver_, range_, x_coord, y_coord, selector="button.button_show__VRCFg", link=""):
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            top_button = WebDriverWait(driver_, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            if top_button is not None:
                break
        except TimeoutException:
            pass


def get_content(driver_):
    try:
        content_elements = WebDriverWait(driver_, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.se-text-paragraph")))
        return " ".join([element.text for element in content_elements])
    except TimeoutException:
        logging.error("Content element not found or timeout occurred.")
        return ""


def get_reply_button(driver_):
    try:
        return WebDriverWait(driver_, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_reply")))
    except TimeoutException:
        logging.error("Reply content not found or timeout occurred.")
        return None


def get_mmix_reply(driver_):
    try:
        name_elements = WebDriverWait(driver_, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.u_cbox_name")))
        for name in name_elements:
            href = name.get_attribute("href")
            if 'csj4032' in parse_qs(urlparse(href).query).get('blogId', []):
                return True
        return False
    except TimeoutException:
        logging.error("MMIX reply textarea not found or timeout occurred.")
        return False


def write_comment(driver_, comment_):
    try:
        driver_.find_element(By.ID, "naverComment__write_textarea").send_keys(comment_)
        time.sleep(random.uniform(1, 2))
        driver_.find_element(By.CSS_SELECTOR, "button.u_cbox_btn_upload").click()
        time.sleep(random.uniform(1, 2))
    except NoSuchElementException:
        logging.error("Comment textarea not found.")
        return


def call_gemini_api(api_key, model_name, context_=None, generation_config=None, safety_settings=None):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(contents=context_, generation_config=generation_config, safety_settings=safety_settings)
    return response.text


def call_ollama_api(prompt, model='llama3:latest'):
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")
