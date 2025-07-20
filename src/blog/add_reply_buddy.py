import logging
import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common.webs as utils
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)

__prompt = "'{0}' 이라는 제목의 블로그 글에 대한 코멘트를 하나만 간단하게 작성해줘. 아래 '{1}' 내용을 참고해서, 방문자 입장에서 담백하고 자연스럽게 작성해야 해. 코멘트는 50자 내외로 해줘"


def parse_post(post_: WebElement) -> dict | None:
    try:
        name = post_.find_element(By.CSS_SELECTOR, "strong.name__aDUPc").text.strip()
        title = post_.find_element(By.CSS_SELECTOR, "strong.title__UUn4H").text.strip()
        link = post_.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute('href')
        return {"name": name, "title": title, "link": link}
    except NoSuchElementException as exception_:
        logging.warning(f"Failed to parse post element. {exception_}")
    return None


def get_posts(driver_: WebDriver, selector: str = "div.card__reUkU") -> list[dict]:
    try:
        posts_ = WebDriverWait(driver_, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        return [parse_post(post_) for post_ in posts_ if parse_post(post_) is not None]
    except TimeoutException as exception_:
        logging.error(f"Error while getting feeds: {exception_}")
        return []


def get_ollama_comment(title: str, content_: str, model: str = 'gemma3:latest') -> str:
    response = utils.call_ollama_api(__prompt.format(title, content_), model=model)
    return response.strip() if response else ""


if __name__ == '__main__':
    configuration = Configuration()
    configuration.set_browser_headless(False)
    driver = utils.setup_firefox_profile_driver(configuration)
    try:
        driver.get(configuration.naver_blog_mobile_feed_list_url)
        driver.set_window_position(-1000, 0)
        time.sleep(random.uniform(1, 2))
        utils.window_scroll(driver, 20, 0, 500, scroll_random_start_time=0, scroll_random_end_time=1, link=configuration.naver_blog_mobile_feed_list_url)
        posts = get_posts(driver)
        posts_count = len(posts)
        for index, post in enumerate(posts):
            try:
                logging.info(f"Processing reply {index + 1}/{posts_count} Post: {post['name']}, Title: {post['title']}, Link: {post['link']}")
                driver.get(post['link'])
                time.sleep(random.uniform(2, 3))
                content = utils.get_content(driver)
                reply_button = utils.get_reply_button(driver)
                logging.info(f"Post: {post['name']}, Link: {post['link']}, Content length: {len(content)}, Reply button: {reply_button is not None}")
                if content and len(content) > 1000 and reply_button:
                    driver.execute_script("arguments[0].click();", reply_button)
                    time.sleep(random.uniform(2, 3))
                    is_exist_mmix_reply = utils.get_mmix_reply(driver)
                    logging.info(f"Processing reply {index + 1}/{posts_count} Post: {post['name']}, Title: {post['title']} MMIX reply exists: {is_exist_mmix_reply}")
                    if not is_exist_mmix_reply:
                        comment = get_ollama_comment(post['title'], content[:3000])
                        logging.info(f"Processing reply {index + 1}/{len(posts)}: Visiting post '{post['title']}', Generated reply: {comment}")
                        if comment and utils.write_comment(driver, comment) == "Limited":
                            break
                        time.sleep(random.uniform(2, 3))
            except Exception as exception:
                logging.error(f"Post: {post['name']}, Link: {post['link']}, Title: {post['title']} Error : {exception}")
                pass
            time.sleep(random.uniform(2, 2))
    except Exception as exception:
        logging.error(f"An error occurred: {exception}")
    finally:
        time.sleep(random.uniform(2, 10))
        driver.quit()


