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

logging.basicConfig(level=logging.WARNING, )


def parse_buddy(buddy_):
    try:
        blog_name = buddy_.find_element(By.CSS_SELECTOR, ".desc__mzlZG").text.strip()
        nick_name = buddy_.find_element(By.CSS_SELECTOR, ".name__jKV9Z").text.strip()
        link = buddy_.find_element(By.CSS_SELECTOR, "a.link__vh8uU").get_attribute('href')
        status = buddy_.find_element(By.CSS_SELECTOR, "button.btn__pqYzr").text.strip()
        return {"blog_name": blog_name, "nick_name": nick_name, "link": link, "status": status}
    except NoSuchElementException as exception:
        logging.error(f"Failed to parse buddy element. {exception}")
        return None


def get_neighbor(driver_):
    buddies = driver_.find_elements(By.CSS_SELECTOR, "li.item__FZ64x")
    neighbor_ = [parsed for buddy_ in buddies if (parsed := parse_buddy(buddy_)) is not None]
    logging.info(f"Found {len(neighbor_)} neighbors.")
    return random.sample(neighbor_, len(neighbor_))


def try_click_element(driver_, selector, timeout=3):
    try:
        WebDriverWait(driver_, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()
    except TimeoutException:
        logging.error(f"Element with selector '{selector}' not found or not clickable.")
        pass


def get_posts(driver_):
    try:
        posts_ = WebDriverWait(driver_, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card__reUkU")))
        logging.info(f"Found {len(posts_)} posts.")
        return posts_
    except TimeoutException:
        logging.error("Timeout while trying to find posts.")
        return []


def like_post(posts_, buddy_, limit=10):
    if not posts_:
        logging.warning(f"No posts found for {buddy_['nick_name']}.")
        return
    for index_, post in enumerate(posts_[:random.randint(1, limit)]):
        time.sleep(random.uniform(1, 2))
        try:
            post.find_element(By.CSS_SELECTOR, "a.u_likeit_list_btn._button.off").click()
            href_ = post.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute('href')
            logging.info(f"Liking post {index_ + 1}/{len(posts_)} for {buddy_['nick_name']} [{href_}]")
        except NoSuchElementException as exception:
            logging.error(f"Failed to like post {index_ + 1} for {buddy_['nick_name']}: {exception}")
            pass


if __name__ == '__main__':
    configuration = Configuration()
    driver = utils.setup_firefox_profile_driver(configuration)
    driver.set_window_position(0, 0)
    try:
        driver.get(configuration.naver_blog_mobile_buddy_list_url)
        you_add_to_click = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-click-area='ngr.youadd']")))
        you_add_to_click.click()
        time.sleep(random.uniform(1, 2))
        utils.window_scroll(driver, 200, 0, 500, 0, 1, configuration.naver_blog_mobile_buddy_list_url)
        neighbor = get_neighbor(driver)
        for index, buddy in enumerate(neighbor):
            logging.info(f"Processing buddy {index + 1}/{len(neighbor)}: {buddy['nick_name']} [{buddy['link']}]")
            driver.get(buddy['link'])
            time.sleep(random.uniform(1, 2))
            try_click_element(driver, "button[data-click-area='ltb.post']")
            time.sleep(random.uniform(1, 2))
            try_click_element(driver, "button[data-click-area='pls.card']")
            like_post(get_posts(driver), buddy)
            time.sleep(random.uniform(1, 2))
    except TimeoutException as e:
        logging.error(f"Timeout while trying to find elements: {e}")
    finally:
        time.sleep(random.uniform(1, 2))
        driver.quit()
        logging.info("Driver closed.")
