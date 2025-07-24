import logging
import random
import time
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

import common.webs as utils
from common.llm import call_gemini_api
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)

__gemini_model = "gemini-2.0-flash"
__gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{__gemini_model}:generateContent"
__generation_config = {"temperature": 0.7, "max_output_tokens": 2048, "top_p": 1.0, "top_k": 32, }
__prompt = "'{0}' 이라는 제목의 블로그 포스트에 대한 코멘트를 하나만 간단하게 작성해줘 아래 '{1}' 내용을 바탕으로, 방문자 입장에서 담백하고 자연스럽게 작성해야 해. 코멘트 길이는 50자 내외로 맞춰 줘."


def setup_driver() -> WebDriver:
    options = Options()
    options.add_argument("-profile")
    options.add_argument("/Users/genius/Library/Application Support/Firefox/Profiles/fsqapq5q.Genius")
    options.add_argument("--window-size=400,1080")
    service = Service(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


def parse_post(post_: WebElement) -> Optional[Dict[str, str]]:
    try:
        link = post_.find_element(By.CSS_SELECTOR, "a.link__A4O1D").get_attribute('href')
        name = post_.find_element(By.CSS_SELECTOR, "span.text__f81dq").text
        title = post_.find_element(By.CSS_SELECTOR, "strong.title__Hj5DO").text
        return {"link": link, "name": name, "title": title}
    except NoSuchElementException as exception:
        logging.error(f"Failed to parse post element. {exception}")
        return None


def get_recommend_posts(driver_: WebDriver) -> List[Dict[str, str]]:
    try:
        posts_elements = WebDriverWait(driver_, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.postlist__qxOgF")))
        return [parsed for post_ in posts_elements if (parsed := parse_post(post_)) is not None]
    except TimeoutException:
        logging.error("No posts found or timeout occurred.")
        return []


def get_gemini_comment(gemini_api_key: str, gemini_model: str, title: str, content_: str) -> str:
    response = call_gemini_api(gemini_api_key, gemini_model, __prompt.format(title, content_), __generation_config)
    return response.strip() if response else ""


def get_ollama_comment(title: str, content_: str, url: str = 'http://localhost:11434/api/generate') -> str:
    response = utils.call_ollama_api(__prompt.format(title, content_), "gemma3:latest", url=url)
    return response.strip() if response else ""


def generate_and_write_comment_if_needed(driver_: WebDriver, post_: Dict[str, str], content_: str, is_exist_mmix_reply_: bool) -> None:
    if not is_exist_mmix_reply_:
        comment = get_ollama_comment(post_['title'], content_[:3000])
        logging.info(f"Post: {post_['name']} Generated comment: {comment}")
        if comment:
            utils.write_comment(driver_, comment)
            time.sleep(random.uniform(1, 2))


if __name__ == '__main__':
    configuration = Configuration()
    configuration.set_browser_headless(False)
    driver = utils.setup_firefox_profile_driver(configuration)
    driver.get(configuration.naver_blog_mobile_recommendation_url)
    try:
        utils.window_scroll_more(driver, 10, 0, 500, link=configuration.naver_blog_mobile_recommendation_url)
        posts = get_recommend_posts(driver)
        posts_count = len(posts)
        for index, post in enumerate(posts):
            try:
                logging.info(f"Processing buddy {index + 1}/{posts_count} Post: {post['name']}, Link: {post['link']}, Title: {post['title']}")
                driver.get(post['link'])
                time.sleep(random.uniform(1, 2))
                content = utils.get_content(driver)
                reply_button = utils.get_reply_button(driver)
                if content and reply_button:
                    driver.execute_script("arguments[0].click();", reply_button)
                    time.sleep(random.uniform(1, 2))
                    is_exist_mmix_reply = utils.get_mmix_reply(driver)
                    logging.info(f"Post: {post['name']} Mmix reply exists: {is_exist_mmix_reply}")
                    generate_and_write_comment_if_needed(driver, post, content, is_exist_mmix_reply)
            except Exception as e:
                logging.error(f"Error processing post {post['name']}: {e}")
                pass
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()
        logging.info("Driver closed.")
