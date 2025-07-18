import logging
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import blog.utils as utils
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)

__prompt = "'{0}' 이라는 제목의 {1} 카테고리 블로그 글에 대한 코멘트를 작성해줘. 아래 '{2}' 내용을 참고해서, 남성 방문자 입장에서 자연스러운 한 문장으로 작성해야 해."


def get_ollama_comment(title_, category_, content_, model='gemma3:latest'):
    response = utils.call_ollama_api(__prompt.format(title_, category_, content_), model=model)
    return response.strip() if response else ""


def setup_driver():
    options = FirefoxOptions()
    options.add_argument(f"--headless")
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


if __name__ == '__main__':
    driver = setup_driver()
    try:
        driver.get("https://m.blog.naver.com/PostView.naver?blogId=shin30233&logNo=223936356948&navType=by")
        category = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.blog_category"))).text.strip()
        title = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.se-title-text"))).text.strip()
        content = utils.get_content(driver)
        comment = get_ollama_comment(title, category, content)
        logging.info(f"Generated comment: {comment}")
    except Exception as exception:
        logging.error(f"An error occurred: {exception}")
    finally:
        time.sleep(random.uniform(1, 10))
        driver.quit()
