import logging
import random
import re
import time

from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from blog import utils
from blog.utils import window_scroll_more
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)


def window_scroll(driver_, range_, x_coord, y_coord):
    for index in range(range_):
        driver_.execute_script(f"window.scrollBy({x_coord}, {y_coord});")
        time.sleep(random.uniform(0, 1))


def parse_post(post):
    try:
        link = post.find_element(By.CLASS_NAME, "link__A4O1D").get_attribute('href')
        name = post.find_element(By.CSS_SELECTOR, ".text__f81dq").text.strip()
        try:
            like_text = post.find_element(By.CSS_SELECTOR, ".like__vTXys").text.strip()
            likes = int(like_text) if like_text.isdigit() else 0
        except NoSuchElementException:
            logging.warning("Like count not found, defaulting to 0.")
            likes = 0
        return {'link': link, 'name': name, 'likes': likes}
    except NoSuchElementException:
        logging.error("Failed to parse post element.")
        return None


def parse_buddy(buddy):
    try:
        blog_name = buddy.find_element(By.CSS_SELECTOR, ".blogname__yjIQj.ell").text.strip()
        nick_name = buddy.find_element(By.CSS_SELECTOR, ".nickname__hHyXx.ell").text.strip()
        link = buddy.find_element(By.CSS_SELECTOR, "a.link__u0jKG").get_attribute('href')
        status = buddy.find_element(By.CSS_SELECTOR, ".add_buddy_btn__kDKdA").text.strip()
        return {"blog_name": blog_name, "nick_name": nick_name, "link": link, "status": status}
    except NoSuchElementException:
        logging.error("Failed to parse buddy element.")
        return None


def get_today_total_visitor_text(driver_):
    try:
        full_text = WebDriverWait(driver_, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.count__T3YO8"))).text
        parts = full_text.split()
        today_count_str = parts[1]
        total_count_str = parts[3]
        return int(today_count_str.replace(',', '')), int(total_count_str.replace(',', ''))
    except TimeoutException:
        logging.error("Failed to retrieve today's total visitor text.")
        return 0, 0


def get_buddy_count(driver_):
    try:
        buddy_count_text = WebDriverWait(driver_, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.buddy__fw6Uo"))).text
        match = re.search(r'[\d,]+', buddy_count_text)
        if match:
            return int(match.group(0).replace(',', ''))
        return 0
    except TimeoutException:
        logging.error("Failed to retrieve buddy count.")
        return 0


def get_buddy_subject(driver_):
    try:
        return WebDriverWait(driver_, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.subject__m4PT2"))).text.replace('ㆍ', '')
    except TimeoutException:
        logging.error("Failed to retrieve buddy subject.")
        return ""


if __name__ == '__main__':
    configuration = Configuration()
    driver = utils.setup_firefox_profile_driver(configuration)
    driver.set_window_position(0, 0)
    try:
        driver.get("https://m.blog.naver.com")
        logging.info(f"Page title is: {driver.title}")

        time.sleep(random.uniform(0, 1))
        recommend_link = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-click-area='lnb.rec']")))
        recommend_link.click()

        window_scroll_more(driver, 30, 0, 500, "button.button_show__VRCFg")
        logging.info("Scrolled down to load more posts.")
        post_list = driver.find_elements(By.CLASS_NAME, "postlist__qxOgF")
        top_post = max((post for post in (parse_post(p) for p in post_list) if post), key=lambda post: post['likes'], default=None)
        logging.info(f"Top post: {top_post}")

        time.sleep(random.uniform(0, 1))
        driver.get(top_post['link'])

        like_more = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_like_more")))
        driver.execute_script("arguments[0].click();", like_more)
        time.sleep(random.uniform(0, 1))

        window_scroll(driver, 20, 0, 500)
        buddy_list = driver.find_elements(By.CLASS_NAME, "sympathy_item__ghUVy")
        buddies = [parsed_buddy for buddy in buddy_list if (parsed_buddy := parse_buddy(buddy)) and parsed_buddy.get('status') == '이웃추가']
        logging.info(f"Found {len(buddies)} buddies.")

        for buddy in buddies:
            logging.info(f"Processing buddy: {buddy['nick_name']}")
            driver.get(buddy['link'])
            time.sleep(random.uniform(1, 2))
            try:
                today_total_visitor_count = get_today_total_visitor_text(driver)
                buddy_count = get_buddy_count(driver)
                subject = get_buddy_subject(driver)
                logging.info(f"Buddy: {buddy['nick_name']}, Subject: {subject}, Buddy Count: {buddy_count}, Today's Total Visitor Count: {today_total_visitor_count}")
                if not subject or buddy_count < 100 or today_total_visitor_count[0] < 10 or today_total_visitor_count[1] < 10000:
                    logging.info(f"{buddy['nick_name']} Skipping buddy due to insufficient conditions.")
                    continue

                buddy_add = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-click-area='ebc.add']")))
                driver.execute_script("arguments[0].click();", buddy_add)
                time.sleep(random.uniform(1, 2))
                try:
                    description_paragraph = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.desc__QgoUl")))
                    logging.info(f"Popup description text: {description_paragraph.text}")
                    if description_paragraph.text == "하루에 신청 가능한 이웃수가 초과되어 더이상 이웃을 추가할 수 없습니다.":
                        logging.info("Daily buddy limit reached, skipping further additions.")
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn__mjgk7"))).click()
                        break
                    if description_paragraph.text == "그룹이 꽉참":
                        logging.info(f"{buddy['nick_name']} has too many buddies, skipping.")
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "_alertLayerClose"))).click()
                        break
                    if description_paragraph.text == "서로이웃 신청 진행중입니다. 서로이웃<br>신청을 취소하시겠습니까?":
                        logging.info(f"Already a buddy with {buddy['nick_name']}, skipping.")
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn__mjgk7"))).click()
                        continue
                    if description_paragraph.text == "상대방의 이웃수가 5,000명이 초과되어 더 이상 이웃을 추가할 수 없습니다.":
                        logging.info(f"{buddy['nick_name']} has too many buddies, skipping.")
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "_alertLayerClose"))).click()
                        continue
                except TimeoutException:
                    logging.info(f"No alert for buddy: {buddy['nick_name']}")
                    pass
                buddy_button_radio = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, "bothBuddyRadio")))
                if buddy_button_radio.is_enabled():
                    buddy_button_radio.click()
                    time.sleep(random.uniform(1, 2))
                    textarea = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.textarea_t1")))
                    textarea.send_keys(f"안녕하세요! {buddy['nick_name']}님.\n{subject} 관련 블로그를 탐방하다가 방문하게 됐어요.\n소통하고 싶어서 서로이웃 신청합니다.\n행복한 하루 보내세요!")
                    time.sleep(random.uniform(1, 2))
                    ok_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_ok")))
                    ok_button.click()
                    logging.info(f"Added buddy: {buddy['nick_name']}")
                else:
                    logging.info(f"Buddy button for {buddy['nick_name']} is not enabled, skipping.")
                    close_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_close")))
                    close_button.click()
            except TimeoutException:
                logging.warning(f"Buddy add button not found for {buddy['nick_name']}, skipping.")
                pass
            time.sleep(random.uniform(1, 2))
    except Exception as exception:
        logging.error("An error occurred:", exception)
    finally:
        logging.info("Closing the driver.")
        time.sleep(random.uniform(1, 5))
        driver.quit()
