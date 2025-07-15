import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from blog import utils
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)


def parse_post(post_):
    try:
        nick_name = post_.find_element(By.CSS_SELECTOR, "span.text__f81dq").text.strip()
        title = post_.find_element(By.CSS_SELECTOR, "strong.title__Hj5DO").text.strip()
        link = post_.find_element(By.CSS_SELECTOR, "a.link__A4O1D").get_attribute('href')
        return {"nick_name": nick_name, "title": title, "link": link}
    except NoSuchElementException as exception_:
        logging.warning(f"Failed to parse post element. {exception_}")
    return None


def get_recommend_posts(driver_, selector):
    try:
        posts_ = WebDriverWait(driver_, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        return [parsed for post_ in posts_ if (parsed := parse_post(post_)) is not None]
    except TimeoutException as exception_:
        logging.warning(f"Timeout while trying to find elements: {exception_}")
    return []


def get_like_button(driver_, selector="a.u_likeit_list_btn._button.off"):
    try:
        return WebDriverWait(driver_, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except TimeoutException as exception_:
        logging.warning(f"Like button not found or not clickable: {exception_}")
    return None


if __name__ == '__main__':
    configuration = Configuration()
    driver = utils.setup_firefox_profile_driver(configuration)
    driver.set_window_position(-450, 0)
    try:
        driver.get(configuration.naver_blog_mobile_recommendation_url)
        utils.window_scroll_more(driver, 100, 0, 500, "button.button_show__VRCFg", 0, 1, configuration.naver_blog_mobile_recommendation_url)
        time.sleep(random.uniform(1, 2))
        posts = get_recommend_posts(driver, "div.item__PxpH8")
        post_count = len(posts)
        for index, post in enumerate(posts):
            driver.get(post['link'])
            logging.info(f"Processing {index + 1}/{post_count} Visiting post: {post['title']} by {post['nick_name']}")
            time.sleep(random.uniform(1, 2))
            if get_like_button(driver, "a.u_likeit_list_btn._button.on") is not None:
                logging.info(f"Post already liked: {post['title']}")
                continue
            utils.window_scroll_more(driver, 5, 0, 1000, "button.button_show__VRCFg", 0, 1, post['link'])
            driver.execute_script("arguments[0].click();", get_like_button(driver, "a.u_likeit_list_btn._button.off"))
            time.sleep(random.uniform(1, 2))
    except TimeoutException as exception:
        logging.error(f"Timeout while trying to find elements: {exception}")
    finally:
        time.sleep(random.uniform(1, 2))
        driver.quit()
        logging.info("Driver closed.")
