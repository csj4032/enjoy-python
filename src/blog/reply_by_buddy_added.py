import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from common.webs import setup_firefox_profile_driver, move_to_buddy_added_scroll, try_click_element, process_reply_and_is_limited, get_buddies_by_added_with
from config.configuration import Configuration

__prompt = "'{0}' 이라는 제목의 블로그 글에 대한 코멘트를 하나만 간단하게 작성해줘. 아래 '{1}' 내용을 참고해서, 방문자 입장에서 담백하고 자연스럽게 작성해야 해. 코멘트는 50자 내외로 해줘"


def try_click_tab_and_view_type(driver_: WebDriver) -> None:
    try_click_element(driver_, "button[data-click-area='ltb.post']")
    time.sleep(random.uniform(1, 2))
    try_click_element(driver_, "button[data-click-area='pls.card']")


def parse_post_first(driver_: WebDriver) -> dict[str, str]:
    post_element = WebDriverWait(driver_, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.card__reUkU")))
    title = post_element.find_element(By.CSS_SELECTOR, "strong.title__UUn4H").text
    link = post_element.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute("href")
    return {"link": link, "title": title}


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    configuration.set_browser_headless(True)
    driver = setup_firefox_profile_driver(configuration)
    try:
        move_to_buddy_added_scroll(driver, configuration, range_=50)
        buddies = get_buddies_by_added_with(driver)
        for index, buddy in enumerate(buddies):
            try:
                logging.info(f"Processing buddy {index + 1}/{len(buddies)}: {buddy['nick_name']}, 'link': {buddy['link']}")
                driver.get(buddy['link'])
                try_click_tab_and_view_type(driver)
                blog = parse_post_first(driver)
                driver.get(blog['link'])
                time.sleep(random.uniform(2, 3))
                if process_reply_and_is_limited(driver, blog, __prompt, configuration):
                    break
            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException):
                logging.error(f"Buddy {buddy['nick_name']} link {buddy['link']} not found or has no posts.")
                continue
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException) as exception:
        logging.error(f"Buddy blog move or scroll error: {exception}")
    finally:
        time.sleep(random.uniform(2, 10))
        driver.quit()
