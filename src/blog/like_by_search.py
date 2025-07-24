import logging
import random
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from blog.like_by_buddy_added import try_click_element
from common.search import get_naver_mobile_blog_by_trends
from common.webs import setup_edge_profile_driver, like_post
from config.configuration import Configuration


def get_posts(driver_: WebDriver) -> list[WebElement]:
    try:
        return WebDriverWait(driver_, 3).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card__reUkU")))
    except TimeoutException:
        logging.error("Timeout while trying to find posts.")
        return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    configuration.set_naver_api_search_display(100)
    blogs = get_naver_mobile_blog_by_trends(configuration)
    driver = setup_edge_profile_driver(configuration)
    driver.set_window_position(-500, 0)
    try:
        for index, blog in enumerate(blogs):
            logging.info(f"Processing buddy {index + 1}/{len(blogs)}: {blog.nick_name} [{blog.mobile_link}]")
            time.sleep(random.uniform(2, 3))
            driver.get(blog.mobile_link)
            time.sleep(random.uniform(2, 3))
            try_click_element(driver, "button[data-click-area='ltb.post']")
            time.sleep(random.uniform(2, 3))
            try_click_element(driver, "button[data-click-area='pls.card']")
            like_post(driver, get_posts(driver), blog)
            time.sleep(random.uniform(2, 3))
    except TimeoutException as exception:
        logging.error(f"Timeout while trying to find elements: {exception}")
    finally:
        driver.quit()
        logging.info("Driver closed.")
