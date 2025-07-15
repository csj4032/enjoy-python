import logging
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from blog.utils import setup_firefox_driver, window_scroll_top

logging.basicConfig(level=logging.INFO)

__blog_url = "https://m.blog.naver.com/csj4032"


def parse_post(post_element):
    try:
        title = post_element.find_element(By.CSS_SELECTOR, "strong.title__UUn4H").text
        link = post_element.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute("href")
        return {"title": title, "link": link}
    except Exception as exception:
        logging.error(f"Error parsing post: {exception}")
        return None


def get_posts(driver_, timeout=1, selector="div.card__reUkU"):
    try:
        posts_ = WebDriverWait(driver_, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        return [parse_post(post_) for post_ in posts_ if post_.is_displayed()]
    except Exception as e:
        logging.error(f"Error while fetching posts: {e}")
        return []


if __name__ == '__main__':
    driver = setup_firefox_driver()
    driver.get(__blog_url)
    window_scroll_top(driver, 10, 0, 1000, selector="div.scroll_top__YuIw9", link=__blog_url)
    posts = get_posts(driver)
    logging.info(f"Found {len(posts)} posts on the page.")
    for post in posts:
        logging.info(f"Title: {post['title']}, Link: {post['link']}")
        driver.get(post['link'])
        time.sleep(random.uniform(1, 3))
