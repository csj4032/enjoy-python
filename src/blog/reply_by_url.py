import logging
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import common.webs as utils
from constants import Prompts, Models, APIConfig

logging.basicConfig(level=logging.INFO)


def get_ollama_comment(title_: str, category_: str, content_: str, model_: str = Models.OLLAMA_DEFAULT, url: str = APIConfig.OLLAMA_DEFAULT_URL) -> str:
    prompt = Prompts.URL_COMMENT.format(title_, category_, content_)
    response = utils.call_ollama_api(prompt, model=model_, url=url)
    return response.strip() if response else ""

def setup_driver() -> WebDriver:
    options = FirefoxOptions()
    options.add_argument(f"--headless")
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


if __name__ == '__main__':
    driver = setup_driver()
    try:
        driver.get("https://m.blog.naver.com/PostView.naver?blogId=91077334&logNo=223938907868&navType=by")
        category = WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.blog_category"))).text.strip()
        title = WebDriverWait(driver, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.se-title-text"))).text.strip()
        content = utils.get_content(driver)
        comment = get_ollama_comment(title, category, content)
        logging.info(f"Generated comment: {comment}")
    except Exception as exception:
        logging.error(f"An error occurred: {exception}")
    finally:
        time.sleep(random.uniform(1, 10))
        driver.quit()
