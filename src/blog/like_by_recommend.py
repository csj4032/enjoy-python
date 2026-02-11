import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from common.webs import setup_firefox_profile_driver, window_scroll
from config.configuration import Configuration


def parse_post(post_):
    try:
        nick_name = post_.find_element(By.CSS_SELECTOR, "span.nickname__XgyBA").text.strip()
        title = post_.find_element(By.CSS_SELECTOR, "div.title__cQ_Ls").text.strip()
        link = post_.find_element(By.CSS_SELECTOR, "a.link__rlnCZ").get_attribute('href')
        return {"nick_name": nick_name, "title": title, "link": link}
    except NoSuchElementException as exception_:
        logging.warning(f"Failed to parse post element. {exception_}")
    return None


def get_recommend_posts(driver_, selector):
    try:
        posts_ = WebDriverWait(driver_, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        return [parsed for post_ in posts_ if (parsed := parse_post(post_)) is not None]
    except TimeoutException as exception_:
        logging.warning(f"Timeout while trying to find elements: {exception_}")
    return []


def get_like_element(driver_, selector="span.u_likeit_icon.__reaction__zeroface"):
    try:
        return WebDriverWait(driver_, 2).until(ec.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except TimeoutException as exception_:
        logging.warning(f"Like button not found or not clickable: {exception_}")
    return None


def handle_like_limit_popup(driver_, timeout=2) -> bool:
    try:
        alert = WebDriverWait(driver_, timeout).until(ec.alert_is_present())
        text = alert.text or ""
        if "더 이상 좋아요" in text or "해당 컨텐츠" in text:
            alert.accept()
            return True
        return False
    except TimeoutException:
        pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    configuration.set_browser_headless(False)
    driver = setup_firefox_profile_driver(configuration)
    driver.set_window_position(-1000, 0)
    try:
        driver.get(configuration.naver_blog_mobile_recommendation_url)
        window_scroll(driver, 10, 0, 500, 0, 1, configuration.naver_blog_mobile_recommendation_url)
        time.sleep(random.uniform(1, 2))
        posts = get_recommend_posts(driver, "li.item__Mfnij")
        post_count = len(posts)
        for index, post in enumerate(posts):
            driver.get(post['link'])
            logging.info(f"Processing {index + 1}/{post_count} Visiting post: {post['title']} by {post['nick_name']}")
            window_scroll(driver, 5, 0, 1000, 0, 1, post['link'])
            like_button = driver.find_element(By.CSS_SELECTOR, "a.u_likeit_list_button._button")
            if like_button is None:
                logging.info(f"Like button not found for post: {post['title']}")
                continue
            if like_button.get_attribute("aria-pressed") == "true":
                logging.info(f"Post already liked: {post['title']}")
                continue
            driver.execute_script("arguments[0].click();", like_button)
            if handle_like_limit_popup(driver, timeout=2):
                logging.info("Like limit popup handled (clicked OK).")
            time.sleep(random.uniform(1, 2))
    except TimeoutException as exception:
        logging.error(f"Timeout while trying to find elements: {exception}")
    finally:
        time.sleep(random.uniform(1, 2))
        driver.quit()
        logging.info("Driver closed.")
