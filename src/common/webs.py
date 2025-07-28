import logging
import random
import time
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, UnexpectedAlertPresentException, InvalidSessionIdException
from selenium.webdriver.common.by import By
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

from common.llm import call_ollama_api
from common.search import Blog
from config.configuration import Configuration


def set_firefox_driver(configuration: Configuration, options: FirefoxOptions) -> WebDriver:
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
    return set_firefox_driver(configuration, options)


def setup_edge_profile_driver(configuration: Configuration) -> WebDriver:
    options = EdgeOptions()
    configuration.get_browser_headless() and options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={configuration.get_browser_edge_profile_path()}")
    options.add_argument(f"profile-directory={configuration.get_browser_edge_profile()}")
    options.add_argument(f"--window-size={configuration.get_browser_edge_window_size()}")
    service = EdgeService(executable_path=configuration.get_browser_msedgedriver_path())
    return webdriver.Edge(service=service, options=options)


def setup_safari_profile_driver(configuration: Configuration) -> WebDriver:
    options = SafariOptions()
    options.add_argument("--headless") if configuration.get_browser_headless() else None
    service = SafariService(executable_path='/usr/bin/safaridriver')
    driver = webdriver.Safari(service=service, options=options)
    driver.set_window_size(550, 1580)
    return driver


def window_scroll(driver_: WebDriver, range_: int, x_coord: int, y_coord: int, scroll_random_start_time: float = 0, scroll_random_end_time: float = 10, link: str = "") -> None:
    for index_ in range(range_):
        logging.info(f"Scrolling {index_ + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))


def window_scroll_more(driver_: WebDriver, range_: int, x_coord: int, y_coord: int, selector: str = "button.button_show__VRCFg", scroll_random_start_time: float = 0, scroll_random_end_time: float = 10, link: str = "") -> None:
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            more_button = WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            more_button.click()
            logging.info(f"Clicked more button {index + 1}/{range_} times. link : {link}")
            time.sleep(random.uniform(scroll_random_start_time, scroll_random_end_time))
        except TimeoutException:
            pass


def window_scroll_top(driver_: WebDriver, range_: int, x_coord: int, y_coord: int, selector: str = "button.button_show__VRCFg", link: str = "") -> None:
    for index in range(range_):
        logging.info(f"Scrolling {index + 1}/{range_} times. link : {link}")
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        try:
            top_button = WebDriverWait(driver_, 0.5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            if top_button is not None:
                break
        except TimeoutException:
            pass


def get_content(driver_: WebDriver) -> str:
    try:
        content_elements = WebDriverWait(driver_, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "p.se-text-paragraph")))
        return " ".join([element.text for element in content_elements])
    except TimeoutException:
        logging.error("Content element not found or timeout occurred.")
        return ""


def get_reply_button(driver_: WebDriver) -> WebElement | None:
    try:
        return WebDriverWait(driver_, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_reply")))
    except TimeoutException:
        logging.error("Reply content not found or timeout occurred.")
        return None


def get_mmix_reply(driver_: WebDriver) -> bool | None:
    try:
        name_elements = WebDriverWait(driver_, 5).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "a.u_cbox_name")))
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
        time.sleep(random.uniform(1, 2))
        driver_.find_element(By.ID, "naverComment__write_textarea").send_keys(comment_)
        time.sleep(random.uniform(1, 2))
        driver_.find_element(By.CSS_SELECTOR, "button.u_cbox_btn_upload").click()
        time.sleep(random.uniform(1, 2))
        try:
            alert = WebDriverWait(driver_, 5).until(ec.alert_is_present())
            if alert:
                logging.info(f"Alert text after posting comment: {alert.text}")
                time.sleep(random.uniform(1, 2))
                alert.accept()
                return "Limited"
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException):
            pass
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException):
        logging.error("Comment textarea not found.")
        return "Failed"
    return "Success"


def get_ollama_comment(prompt: str, title: str, content_: str, model: str, url: str) -> str:
    response = call_ollama_api(prompt.format(title, content_), model=model, url=url)
    return response.strip() if response else ""


def is_valid_post(content_: str, reply_button_: WebElement | None) -> bool:
    return bool(content_) and len(content_) > 1000 and reply_button_ is not None


def is_limited_comment(driver_: WebDriver, comment_: str) -> bool:
    return write_comment(driver_, comment_) == "Limited"


def process_reply_and_is_limited(driver_: WebDriver, post_: dict[str, str], prompt: str, config: Configuration) -> bool:
    content = get_content(driver_)
    reply_button = get_reply_button(driver_)
    if is_valid_post(content, reply_button):
        driver_.execute_script("arguments[0].click();", reply_button)
        time.sleep(random.uniform(2, 3))
        is_exist_mmix_reply = get_mmix_reply(driver_)
        if not is_exist_mmix_reply:
            comment = get_ollama_comment(prompt, post_['title'], content[:3000], model=config.ollama_default_model, url=config.ollama_api_url)
            if is_limited_comment(driver_, comment):
                logging.info("Comment is limited, stopping further processing.")
                return True
    return False


def try_click_element(driver_: WebDriver, selector: str, timeout: int = 3) -> None:
    try:
        WebDriverWait(driver_, timeout).until(ec.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException):
        pass


def move_to_buddy_added_scroll(driver_: WebDriver, configuration_: Configuration, range_: int = 200, x_coord: int = 0, y_coord: int = 500, scroll_randon_start_time: float = 0, scroll_randon_end_time: float = 1, selector: str = "button[data-click-area='ngr.youadd']") -> None:
    logging.info(f"Navigating to {configuration_.naver_blog_mobile_buddy_list_url} to move to buddy added scroll.")
    driver_.get(configuration_.naver_blog_mobile_buddy_list_url)
    you_add_to_click = WebDriverWait(driver_, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    you_add_to_click.click()
    time.sleep(random.uniform(1, 2))
    window_scroll(driver_, range_, x_coord, y_coord, scroll_randon_start_time, scroll_randon_end_time, configuration_.naver_blog_mobile_buddy_list_url)


def parse_buddy_by_added(buddy_: WebElement) -> dict[str, str] | None:
    try:
        blog_name = buddy_.find_element(By.CSS_SELECTOR, "div.desc__mzlZG").text.strip()
        nick_name = buddy_.find_element(By.CSS_SELECTOR, "strong.name__jKV9Z").text.strip()
        link = buddy_.find_element(By.CSS_SELECTOR, "a.link__vh8uU").get_attribute('href')
        status = buddy_.find_element(By.CSS_SELECTOR, "button[data-click-area='ngr.change']").text.strip()
        return {"blog_name": blog_name, "nick_name": nick_name, "link": link, "status": status}
    except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException) as exception:
        logging.error(f"Failed to parse buddy element. {exception}")
        return None


def get_buddies_by_added(driver_: WebDriver, selector: str = "div.buddy_item__evaoI") -> list[dict[str, str]]:
    buddies_ = driver_.find_elements(By.CSS_SELECTOR, selector)
    neighbor_ = [parsed for buddy_ in buddies_ if (parsed := parse_buddy_by_added(buddy_)) is not None]
    return random.sample(neighbor_, len(neighbor_))


def get_buddies_by_added_with(driver_: WebDriver, selector: str = "div.buddy_item__evaoI") -> list[dict[str, str]]:
    buddies_ = driver_.find_elements(By.CSS_SELECTOR, selector)
    neighbor_ = [parsed for buddy_ in buddies_ if (parsed := parse_buddy_by_added(buddy_)) is not None and parsed['status'] == '서로이웃']
    return random.sample(neighbor_, len(neighbor_))


def parse_post(post_element: WebElement, link_selector: str, name_selector: str, title_selector: str) -> dict[str, str] | None:
    try:
        link = post_element.find_element(By.CSS_SELECTOR, link_selector).get_attribute('href')
        name = post_element.find_element(By.CSS_SELECTOR, name_selector).text
        title = post_element.find_element(By.CSS_SELECTOR, title_selector).text
        return {"link": link, "name": name, "title": title}
    except NoSuchElementException as e:
        logging.error(f"Failed to parse post element: {e}")
        return None


def get_posts(driver: WebDriver, post_selector: str, link_selector: str, name_selector: str, title_selector: str) -> list[dict[str, str]]:
    try:
        post_elements = WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, post_selector)))
        return [parsed for post in post_elements if (parsed := parse_post(post, link_selector, name_selector, title_selector)) is not None]
    except TimeoutException:
        logging.error("No posts found or timeout occurred.")
        return []


def like_post(driver_: WebDriver, posts_: list[WebElement], blog: Blog, limit: int = 10) -> None:
    if not posts_:
        logging.warning(f"No posts found for {blog.nick_name}.")
        return
    for index_, post in enumerate(posts_[:random.randint(5, limit)]):
        try:
            time.sleep(random.uniform(3, 5))
            like_button = WebDriverWait(driver_, 5).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a.u_likeit_list_btn._button.off")))
            driver_.execute_script("arguments[0].scrollIntoView({block: 'center'});", like_button)
            time.sleep(random.uniform(3, 5))
            driver_.execute_script("arguments[0].click();", like_button)
            href_ = post.find_element(By.CSS_SELECTOR, "a.link__Awlz5").get_attribute('href')
            logging.info(f"Liking post {index_ + 1}/{len(posts_)} for {blog.nick_name} [{href_}]")
        except (NoSuchElementException, ElementClickInterceptedException, TimeoutException, UnexpectedAlertPresentException, InvalidSessionIdException):
            logging.error("WebDriver session is invalid or browser is closed.")
            break
