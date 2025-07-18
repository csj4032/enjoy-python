import logging
import random
import time
from typing import List, Dict, Optional

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from common.search import get_mobile_naver_blog_results_by_trend, Item
from common.webs import setup_edge_profile_driver
from config.configuration import Configuration


def try_click_element(driver_: WebDriver, selector: str, timeout: int = 3) -> None:
    try:
        WebDriverWait(driver_, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException) as e:
        logging.error(f"Element with selector '{selector}' not found or not clickable.")
        pass


def get_posts(driver_: WebDriver) -> List[WebElement]:
    try:
        return WebDriverWait(driver_, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card__reUkU")))
    except TimeoutException:
        logging.error("Timeout while trying to find posts.")
        return []


def like_post(driver_: WebDriver, posts_: List[WebElement], blog_: Item, limit: int = 10) -> None:
    if not posts_:
        logging.warning(f"No posts found for {blog_.nick_name}.")
        return
    for index_, post in enumerate(posts_[:random.randint(5, limit)]):
        try:
            time.sleep(random.uniform(1, 3))
            like_button = WebDriverWait(driver_, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.u_likeit_list_btn._button.off")))
            driver_.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
            time.sleep(random.uniform(1, 3))
            driver_.execute_script("arguments[0].click();", like_button)
            href_ = post.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute('href')
            logging.info(f"Liking post {index_ + 1}/{len(posts_)} for {blog_.nick_name} [{href_}]")
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException) as exception_:
            logging.error(f"Failed to like post {index_ + 1} for {blog_.nick_name}: {exception_}")
            pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    configuration.set_browser_headless(False)
    configuration.set_naver_api_display(100)
    blogs = get_mobile_naver_blog_results_by_trend(configuration)
    driver = setup_edge_profile_driver(configuration)
    driver.set_window_position(-500, 0)
    try:
        for index, blog in enumerate(blogs):
            logging.info(f"Processing buddy {index + 1}/{len(blogs)}: {blog.nick_name} [{blog.mobile_link}]")
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
