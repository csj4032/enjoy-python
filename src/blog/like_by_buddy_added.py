import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, UnexpectedAlertPresentException, InvalidSessionIdException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import ReadTimeoutError

from common.search import Blog
from common.webs import setup_edge_profile_driver, move_to_buddy_added_scroll, try_click_element, get_buddies_by_added, like_post
from config.configuration import Configuration


def get_posts(driver_: WebDriver) -> list[WebElement]:
    try:
        posts_ = WebDriverWait(driver_, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card__reUkU")))
        return posts_
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException):
        logging.error("Timeout while trying to find posts.")
        return []


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    driver = setup_edge_profile_driver(configuration)
    try:
        move_to_buddy_added_scroll(driver, configuration, range_=250)
        buddies = get_buddies_by_added(driver)
        for index, buddy in enumerate(buddies):
            try:
                logging.info(f"Processing buddy {index + 1}/{len(buddies)}: {buddy['nick_name']} [{buddy['link']}]")
                driver.get(buddy['link'])
                time.sleep(random.uniform(1, 2))
                try_click_element(driver, "button[data-click-area='ltb.post']")
                time.sleep(random.uniform(1, 2))
                try_click_element(driver, "button[data-click-area='pls.card']")
                like_post(driver, get_posts(driver), Blog(nick_name=buddy['nick_name'], mobile_link=buddy['link']))
                time.sleep(random.uniform(1, 2))
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException, InvalidSessionIdException) as exception:
                logging.error(f"Error processing buddy {buddy['nick_name']}: {exception}")
                continue
    except TimeoutException as e:
        logging.error(f"Timeout while trying to find elements: {e}")
    finally:
        time.sleep(random.uniform(1, 2))
        driver.quit()
        logging.info("Driver closed.")
