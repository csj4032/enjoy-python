import logging
import random
import time
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.configuration import Configuration


def set_firefox_driver(configuration, options) -> WebDriver:
    configuration.get_browser_headless() and options.add_argument("--headless")
    options.add_argument(f"--window-size={configuration.get_browser_firefox_window_size()}")
    options.set_preference("general.useragent.override", configuration.get_browser_iphone_user_agent())
    service = FirefoxService(executable_path=configuration.get_browser_geckodriver_path())
    return webdriver.Firefox(service=service, options=options)


def setup_firefox_driver(configuration: Configuration) -> WebDriver:
    options = FirefoxOptions()
    return set_firefox_driver(configuration, options)


def setup_firefox_profile_driver(configuration: Configuration) -> WebDriver:
    options = FirefoxOptions()
    options.add_argument("-profile")
    options.add_argument(configuration.get_browser_firefox_profile_path())
    options.add_argument("--window-size=450,1200")
    return set_firefox_driver(configuration, options)


def setup_edge_profile_driver(configuration: Configuration) -> WebDriver:
    options = EdgeOptions()
    configuration.get_browser_headless() and options.add_argument("--headless")
    options.add_argument(f"--user-data-dir={configuration.get_browser_edge_profile_path()}")
    options.add_argument(f"profile-directory={configuration.get_browser_edge_profile()}")
    options.add_argument(f"--window-size={configuration.get_browser_edge_window_size()}")
    service = EdgeService(executable_path=configuration.get_browser_msedgedriver_path())
    return webdriver.Edge(service=service, options=options)


def setup_safari_profile_driver(configuration: Configuration):
    options = SafariOptions()
    options.add_argument("--headless") if configuration.get_browser_headless() else None
    service = SafariService(executable_path='/usr/bin/safaridriver')
    driver = webdriver.Safari(service=service, options=options)
    driver.set_window_size(550, 1580)
    return driver


def window_scroll(driver_: WebDriver, range_, x_coord, y_coord, scroll_random_start_time=0, scroll_random_end_time=10, link=""):
    for index_ in range(range_):
        logging.info(f"Scrolling {index_ + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))


def window_scroll_more(driver_: WebDriver, range_, x_coord, y_coord, selector="button.button_show__VRCFg", scroll_random_start_time=0, scroll_random_end_time=10, link="") -> None:
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            more_button = WebDriverWait(driver_, 1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            more_button.click()
            logging.info(f"Clicked more button {index + 1}/{range_} times. link : {link}")
            time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))
        except TimeoutException:
            pass


def window_scroll_top(driver_: WebDriver, range_, x_coord, y_coord, selector="button.button_show__VRCFg", link="") -> None:
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            top_button = WebDriverWait(driver_, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            if top_button is not None:
                break
        except TimeoutException:
            pass


def get_content(driver_: WebDriver) -> str:
    try:
        content_elements = WebDriverWait(driver_, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "p.se-text-paragraph")))
        return " ".join([element.text for element in content_elements])
    except TimeoutException:
        logging.error("Content element not found or timeout occurred.")
        return ""


def get_reply_button(driver_: WebDriver) -> WebElement | None:
    try:
        return WebDriverWait(driver_, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_reply")))
    except TimeoutException:
        logging.error("Reply content not found or timeout occurred.")
        return None


def get_mmix_reply(driver_: WebDriver) -> bool | None:
    try:
        name_elements = WebDriverWait(driver_, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.u_cbox_name")))
        for name in name_elements:
            href = name.get_attribute("href")
            parameter = parse_qs(urlparse(href).query).get('blogId', [])
            if 'csj4032' in parameter:
                return True
        return False
    except TimeoutException:
        pass


def write_comment(driver_: WebDriver, comment_: str) -> str:
    try:
        driver_.find_element(By.ID, "naverComment__write_textarea").send_keys(comment_)
        time.sleep(random.uniform(1, 2))
        driver_.find_element(By.CSS_SELECTOR, "button.u_cbox_btn_upload").click()
        time.sleep(random.uniform(1, 2))
        try:
            alert = WebDriverWait(driver_, 3).until(EC.alert_is_present())
            if alert:
                logging.info(f"Alert text after posting comment: {alert.text}")
                time.sleep(random.uniform(1, 2))
                alert.accept()
                return "Limited"
        except TimeoutException:
            pass
    except (TimeoutException, NoSuchElementException):
        logging.error("Comment textarea not found.")
        pass
    return "Success"


def parse_post(post_element, link_selector, name_selector, title_selector):
    try:
        link = post_element.find_element(By.CSS_SELECTOR, link_selector).get_attribute('href')
        name = post_element.find_element(By.CSS_SELECTOR, name_selector).text
        title = post_element.find_element(By.CSS_SELECTOR, title_selector).text
        return {"link": link, "name": name, "title": title}
    except NoSuchElementException as e:
        logging.error(f"Failed to parse post element: {e}")
        return None


def get_posts(driver, post_selector, link_selector, name_selector, title_selector):
    try:
        post_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, post_selector))
        )
        logging.info(f"Found {len(post_elements)} posts.")
        return [parsed for post in post_elements if (parsed := parse_post(post, link_selector, name_selector, title_selector)) is not None]
    except TimeoutException:
        logging.error("No posts found or timeout occurred.")
        return []
