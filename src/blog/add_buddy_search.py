import logging
import random
import re
import time
from typing import Tuple

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from common.search import get_naver_mobile_blog_by_trends
from common.webs import setup_edge_profile_driver
from config.configuration import Configuration


def window_scroll(driver_: WebDriver, range_, x_coord: int, y_coord: int) -> None:
    for index_ in range(range_):
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        time.sleep(random.uniform(0, 1))


def get_today_total_visitor_text(driver_: WebDriver) -> Tuple[int, int]:
    try:
        parts = WebDriverWait(driver_, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.count__T3YO8"))).text.split()
        return int(parts[1].replace(',', '')), int(parts[3].replace(',', ''))
    except TimeoutException:
        logging.error("Failed to retrieve today's total visitor text.")
        return 0, 0


def get_buddy_count(driver_: WebDriver) -> int:
    try:
        if match := re.search(r'[\d,]+', WebDriverWait(driver_, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, "span.buddy__fw6Uo"))).text):
            return int(match[0].replace(',', ''))
        return 0
    except TimeoutException:
        logging.error("Failed to retrieve buddy count.")
        return 0


def get_subject(driver_: WebDriver) -> str:
    try:
        return WebDriverWait(driver_, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, "span.subject__m4PT2"))).text.replace('ㆍ', '')
    except TimeoutException:
        logging.error("Failed to retrieve buddy subject.")
        return ""


def handle_buddy_popup(driver_, blog_, configuration_):
    try:
        desc_text = WebDriverWait(driver_, 1).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "p.desc__QgoUl"))
        ).text.strip()
        logging.info(f"Popup description text: {desc_text}")
        if desc_text == configuration_.naver_blog_buddy_daily_add_limit_message:
            logging.info("Daily buddy limit reached, skipping further additions.")
            WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button.btn__mjgk7"))).click()
            return "break"
        if desc_text == "그룹이 꽉참":
            logging.info(f"{blog_.nick_name} has too many buddies, skipping.")
            WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.ID, "_alertLayerClose"))).click()
            return "break"
        if desc_text in ("서로이웃 신청 진행중입니다. 서로이웃\n신청을 취소하시겠습니까?", "서로이웃 신청 진행중입니다. 서로이웃신청을 취소하시겠습니까?"):
            logging.info(f"Already a buddy with {blog_.nick_name}, skipping.")
            WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button.btn__mjgk7"))).click()
            return "continue"
        if desc_text == "상대방의 이웃수가 5,000명이 초과되어 더 이상 이웃을 추가할 수 없습니다.":
            logging.info(f"{blog.nick_name} has too many buddies, skipping.")
            WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.ID, "_alertLayerClose"))).click()
            return "continue"
    except TimeoutException:
        logging.info(f"No alert for buddy: {blog_.nick_name}")
    return None


def is_buddy_condition_met(subject_: str, buddy_count_: int, today_count: int, total_count: int) -> bool:
    return bool(subject_) and buddy_count_ >= 100 and today_count >= 10 and total_count >= 10000


def add_buddy_process(driver_: WebDriver, blog_, subject_: str) -> None:
    buddy_button_radio = WebDriverWait(driver_, 3).until(ec.presence_of_element_located((By.ID, "bothBuddyRadio")))
    if buddy_button_radio.is_enabled():
        buddy_button_radio.click()
        time.sleep(random.uniform(2, 3))
        textarea = WebDriverWait(driver_, 3).until(ec.presence_of_element_located((By.CSS_SELECTOR, "textarea.textarea_t1")))
        textarea.send_keys(f"안녕하세요! {blog_.nick_name}님.\n{subject_} 관련 블로그를 탐방하다가 방문하게 됐어요.\n소통하고 싶어서 서로이웃 신청합니다.\n행복한 하루 보내세요!")
        time.sleep(random.uniform(2, 3))
        ok_button = WebDriverWait(driver_, 3).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_ok")))
        ok_button.click()
        logging.info(f"Added buddy: {blog_.nick_name}")
    else:
        logging.info(f"Buddy button for {blog_.nick_name} is not enabled, skipping.")
        close_button = WebDriverWait(driver_, 3).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_close")))
        close_button.click()


def click_buddy_add_button(driver_: WebDriver) -> None:
    driver_.execute_script("arguments[0].click();", WebDriverWait(driver_, 1).until(ec.element_to_be_clickable((By.CSS_SELECTOR, "[data-click-area='ebc.add']"))))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    configuration = Configuration()
    blogs = get_naver_mobile_blog_by_trends(configuration)
    driver = setup_edge_profile_driver(configuration)
    driver.set_window_position(-500, 0)
    try:
        for index, blog in enumerate(blogs):
            logging.info(f"Processing {index + 1}/{len(blogs)}: {blog.nick_name}")
            time.sleep(random.uniform(2, 3))
            driver.get(blog.mobile_link)
            try:
                today_total_visitor_count = get_today_total_visitor_text(driver)
                buddy_count = get_buddy_count(driver)
                subject = get_subject(driver)
                logging.info(f"Blog: {blog.nick_name}, Subject: {subject}, Buddy Count: {buddy_count}, Today's Total Visitor Count: {today_total_visitor_count}")
                if not is_buddy_condition_met(subject, buddy_count, today_total_visitor_count[0], today_total_visitor_count[1]):
                    logging.info(f"{blog.nick_name} Skipping buddy due to insufficient conditions.")
                    continue
                click_buddy_add_button(driver)
                time.sleep(random.uniform(1, 3))
                result = handle_buddy_popup(driver, blog, configuration)
                if result == "break":
                    break
                elif result == "continue":
                    continue
                add_buddy_process(driver, blog, subject)
            except TimeoutException:
                logging.warning(f"Buddy add button not found for {blog.nick_name}, skipping.")
                pass
            time.sleep(random.uniform(1, 2))
    except Exception as exception:
        logging.error("An error occurred:", exception)
    finally:
        logging.info("Closing the driver.")
        time.sleep(random.uniform(1, 2))
        driver.quit()
