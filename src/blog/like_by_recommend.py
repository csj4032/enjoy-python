import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from common.webs import setup_firefox_profile_driver, window_scroll
from config.configuration import Configuration

recommend_post_selector = "li.item__Mfnij"
nick_selector = "span.nickname__XgyBA"
title_selector = "div.title__cQ_Ls"
link_selector = "a.link__rlnCZ"

like_button_selector = "a.u_likeit_list_button"
like_on_selector = "a.u_likeit_list_button._button.on"
like_off_selector = "a.u_likeit_list_button._button.off"


def wait_page_ready(driver_, timeout=10):
    WebDriverWait(driver_, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")


def parse_post(post_):
    try:
        nick_name = post_.find_element(By.CSS_SELECTOR, nick_selector).text.strip()
        title = post_.find_element(By.CSS_SELECTOR, title_selector).text.strip()
        link = post_.find_element(By.CSS_SELECTOR, link_selector).get_attribute("href")
        return {"nick_name": nick_name, "title": title, "link": link}
    except NoSuchElementException as exception:
        logging.warning(f"Failed to parse post element. {exception}")
        return None


def get_recommend_posts(driver_, selector=recommend_post_selector):
    try:
        posts_ = WebDriverWait(driver_, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        return [item for p in posts_ if (item := parse_post(p))]
    except TimeoutException as exception:
        logging.warning(f"Timeout while trying to find elements: {exception}")
        return []


def handle_like_limit_popup(driver_, timeout=2) -> bool:
    try:
        alert = WebDriverWait(driver_, timeout).until(ec.alert_is_present())
        return ("더 이상 좋아요" in (alert.text or "") or "해당 컨텐츠" in (alert.text or "")) \
            and not alert.accept()
    except TimeoutException:
        return False


def get_like_state(driver_, timeout=2):
    try:
        WebDriverWait(driver_, timeout).until(ec.presence_of_element_located((By.CSS_SELECTOR, like_button_selector)))
    except TimeoutException:
        return None
    if driver_.find_elements(By.CSS_SELECTOR, like_on_selector):
        return "ON"
    if driver_.find_elements(By.CSS_SELECTOR, like_off_selector):
        return "OFF"
    return None


def click_like_if_possible(driver_):
    state_ = get_like_state(driver_, timeout=2)
    if state_ is None:
        return "NO_BUTTON"
    if state_ == "ON":
        return "ALREADY_LIKED"
    try:
        btn = WebDriverWait(driver_, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, like_off_selector)))
        driver_.execute_script("arguments[0].click();", btn)
        return "LIKED"
    except TimeoutException:
        return "CLICK_FAILED"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    configuration.set_browser_headless(False)
    driver = setup_firefox_profile_driver(configuration)
    driver.set_window_position(-1000, 0)
    try:
        driver.get(configuration.naver_blog_mobile_recommendation_url)
        wait_page_ready(driver, 10)
        window_scroll(driver, 100, 0, 500, 0, 1, configuration.naver_blog_mobile_recommendation_url)
        time.sleep(random.uniform(0.6, 1.2))
        posts = get_recommend_posts(driver)
        post_count = len(posts)
        for index, post in enumerate(posts, start=1):
            driver.get(post["link"])
            wait_page_ready(driver, 10)
            logging.info(f"Processing {index}/{post_count} Visiting: {post['title']} by {post['nick_name']}")
            state = get_like_state(driver, timeout=2)
            if state is None:
                logging.info(f"No like button: {post['title']}")
                continue
            if state == "ON":
                logging.info(f"Already liked: {post['title']}")
                continue
            window_scroll(driver, 5, 0, 800, 0, 1, post["link"])
            result = click_like_if_possible(driver)
            if result == "LIKED":
                if handle_like_limit_popup(driver, timeout=2):
                    logging.info("Like limit popup handled (clicked OK).")
            elif result == "CLICK_FAILED":
                logging.warning(f"Like click failed: {post['title']}")
            time.sleep(random.uniform(1, 2))
            logging.info(f"Processing {index}/{post_count} Completed: {post['title']} by {post['nick_name']} - Result: {result}")
    except TimeoutException as e:
        logging.error(f"Timeout while trying to find elements: {e}")
    finally:
        time.sleep(random.uniform(0.6, 1.2))
        driver.quit()
        logging.info("Driver closed.")
