import logging
import random
import time
import json
import os

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from common.webs import setup_firefox_driver, window_scroll
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)

def load_posts():
    config_path = os.path.join(os.path.dirname(__file__), '../../config/posts.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)['posts']
        return [{"keywords": post["keywords"], "link": post["link"].replace("blog.naver.com", "m.blog.naver.com")} for post in posts]



def get_search(driver_: WebDriver, link_: str, keyword_: str, selector_: str, match_element: str = "", timeout_: int = 5) -> WebElement | None:
    logging.info(f"Searching for '{keyword_}' in  {selector_},[{match_element}] with link: {link_}")
    try:
        title_elements = WebDriverWait(driver_, timeout_).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector_)))
        for element_ in title_elements:
            href_ = element_.get_attribute("href")
            if href_ == link_:
                logging.info(f"Matched for '{keyword_}' in  {selector_},[{match_element}] with link: {link_}")
                return element_
    except TimeoutException as exception_:
        logging.error(f"Element with selector '{selector_}' not found: {exception_.msg}")
        pass
    return None


if __name__ == '__main__':
    configuration = Configuration()
    posts = load_posts()
    shuffle_posts = random.sample(posts, len(posts))
    for post in shuffle_posts:
        keyword = random.choice(post["keywords"])
        link = post['link']
        driver = setup_firefox_driver(configuration)
        try:
            driver.set_window_position(0, 0)
            driver.get(configuration.naver_mobile_url)
            time.sleep(random.uniform(1, 2))
            search_box = WebDriverWait(driver, 1).until(ec.presence_of_element_located((By.ID, "query")))
            search_box.send_keys(random.choice(post["keywords"]))
            search_box.send_keys(Keys.RETURN)
            matched_element = get_search(driver, link, keyword, "a.aEO4VwHkswcCgUXjRh6w.Lznm151o9qLNLUldttoM", "검색 최상단 영역")
            time.sleep(random.uniform(1, 3))
            if matched_element is None:
                matched_element = get_search(driver, link, keyword, "a.title_link", "인기글 영역")
            time.sleep(random.uniform(1, 3))
            if matched_element is None:
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.LINK_TEXT, "블로그"))).click()
                logging.info(f"Clicked on '블로그' link to search in blog section.")
                matched_element = get_search(driver, link, keyword, "a.dsc_link", "블로그 영역")
            time.sleep(random.uniform(2, 2))
            if matched_element is not None:
                start_time = time.time()
                matched_element.click()
                window_scroll(driver, int(random.uniform(25, 30)), 0, int(random.uniform(100, 500)), 20, 25, link)
                logging.info(f"Time taken to process '{keyword}': {time.time() - start_time:.2f} seconds")
        except Exception as exception:
            logging.info(f"An error occurred: {exception}")
        finally:
            time.sleep(random.uniform(10, 15))
            driver.quit()
