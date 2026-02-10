import logging
import random
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from common.utils import load_meta_posts
from common.webs import window_scroll


def setup_driver() -> WebDriver:
    random_browser = random.choice(["firefox"])
    if random_browser == "chrome":
        options = ChromeOptions()
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    elif random_browser == "safari":
        options = SafariOptions()
        service = SafariService(executable_path="/usr/bin/safaridriver")
        return webdriver.Safari(service=service, options=options)
    elif random_browser == "edge":
        options = EdgeOptions()
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    options = FirefoxOptions()
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


def get_search_top(driver_: WebDriver, link_: str, keyword_: str, selector: str, match_element: str = "") -> WebElement | None:
    for element_ in driver_.find_elements(By.CSS_SELECTOR, selector):
        try:
            href_ = element_.get_attribute("href")
            if href_ == link_:
                logging.info(f"'{keyword_}' {match_element}")
                return element_
        except NoSuchElementException:
            logging.error(f"Element with link {link_} not found in popular search results.")
            continue
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    posts = load_meta_posts()
    shuffle_posts = random.sample(posts, len(posts))
    for post in shuffle_posts:
        keyword = random.choice(post["keywords"])
        link = post['link']
        driver = setup_driver()
        try:
            driver.set_window_size(1280, 1800)
            driver.set_window_position(-1280, 0)
            driver.get("https://www.naver.com")
            search_box = WebDriverWait(driver, 1).until(ec.presence_of_element_located((By.ID, "query")))
            search_box.send_keys(random.choice(post["keywords"]))
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(1, 3))
            matched_element = get_search_top(driver, link, keyword, "a[data-heatmap-target='.link']", "검색 최상단 매치")
            if matched_element is None:
                matched_element = get_search_top(driver, link, keyword, "a[data-heatmap-target='.link']", "검색 인기글 매치")
            if matched_element is None:
                blog_tab = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.LINK_TEXT, "블로그")))
                blog_tab.click()
                time.sleep(random.uniform(1, 3))
                blog_elements = driver.find_elements(By.CSS_SELECTOR, "a[data-heatmap-target='.nblg']")

                for element in blog_elements:
                    try:
                        href = element.get_attribute("href")
                        if href == link:
                            matched_element = element
                            logging.info(f"'{keyword}' 블로그 검색 매치")
                            break
                    except NoSuchElementException:
                        continue

            if matched_element is not None:
                start_time = time.time()
                WebDriverWait(driver, 5).until(ec.element_to_be_clickable(matched_element)).click()
                time.sleep(random.uniform(1, 10))
                WebDriverWait(driver, 5).until(ec.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                main_iframe = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.ID, "mainFrame")))
                driver.switch_to.frame(main_iframe)
                time.sleep(random.uniform(1, 10))
                logging.info(f"Successfully navigated to {keyword} post: {link}")
                window_scroll(driver, 20, 0, random.uniform(100, 500), 25, 35, link)
                driver.switch_to.default_content()
                logging.info(f"Time taken to process '{keyword}': {time.time() - start_time:.2f} seconds")
            else:
                logging.info(f"No matching element found for '{keyword}' in search results.")
        except Exception as exception:
            logging.info(f"An error occurred: {exception}")
        finally:
            time.sleep(random.uniform(1, 10))
            driver.quit()
