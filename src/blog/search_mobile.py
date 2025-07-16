import logging
import random
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from blog import utils
from blog.utils import setup_firefox_driver
from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)

posts = [
    {"keywords": ["A+B"], "link": "https://m.blog.naver.com/csj4032/221651220532"},
    {"keywords": ["Adaptive Query Execution"], "link": "https://m.blog.naver.com/csj4032/223519550322"},
    {"keywords": ["돈의 심리학", "돈 심리학"], "link": "https://m.blog.naver.com/csj4032/223523078830"},
    {"keywords": ["칩워, 누가 반도체 전쟁의 최후 승자", "칩워 누가 반도체 전쟁"], "link": "https://m.blog.naver.com/csj4032/223520452563"},
    {"keywords": ["Slack 새 워크스페이스", "Slack 워크스페이스"], "link": "https://m.blog.naver.com/csj4032/223901622139"},
    {"keywords": ["신경 끄기 기술", "신경끄기기술"], "link": "https://m.blog.naver.com/csj4032/223914881533"},
    {"keywords": ["Iceberg Deltalake"], "link": "https://m.blog.naver.com/csj4032/223914908740"},
    {"keywords": ["30가지 패턴 분산 시스템", "패턴 분산 시스템"], "link": "https://m.blog.naver.com/csj4032/223915376396"},
    {"keywords": ["Java JDK", "Java JDK 설치"], "link": "https://m.blog.naver.com/csj4032/223915459310"},
    {"keywords": ["파이썬 설치", "파이썬설치"], "link": "https://m.blog.naver.com/csj4032/223915465848"},
    {"keywords": ["Java 개발환경 설정", "Java 개발환경"], "link": "https://m.blog.naver.com/csj4032/223915500234"},
    {"keywords": ["일과 일상 나"], "link": "https://m.blog.naver.com/csj4032/223915566048"},
    {"keywords": ["파이썬이란"], "link": "https://m.blog.naver.com/csj4032/223916421094"},
    {"keywords": ["팔란티어(Palantir), 팔란티어 Palantir"], "link": "https://m.blog.naver.com/csj4032/223916603908"},
    {"keywords": ["용기와 겁쟁이"], "link": "https://m.blog.naver.com/csj4032/223917250644"},
    {"keywords": ["파이썬 기초, 자료형", "파이썬 자료형"], "link": "https://m.blog.naver.com/csj4032/223920432120"},
    {"keywords": ["파이썬 제어"], "link": "https://m.blog.naver.com/csj4032/223920432120"},
    {"keywords": ["파이썬 입출"], "link": "https://m.blog.naver.com/csj4032/223920674251"},
    {"keywords": ["파이썬 반복", "파이썬 반복문"], "link": "https://m.blog.naver.com/csj4032/223920710832"},
    {"keywords": ["파이썬 Package"], "link": "https://m.blog.naver.com/csj4032/223921565651"},
    {"keywords": ["파이썬 Exception"], "link": "https://m.blog.naver.com/csj4032/223922827334"},
    {"keywords": ["Git", "Git이란"], "link": "https://m.blog.naver.com/csj4032/223922857147"},
    {"keywords": ["Autonomous Future"], "link": "https://m.blog.naver.com/csj4032/223922988417"},
    {"keywords": ["파이썬 둘러보기 Built-in"], "link": "https://m.blog.naver.com/csj4032/223923023951"},
    {"keywords": ["Tungsten UnsafeRow"], "link": "https://m.blog.naver.com/csj4032/223923130905"},
    {"keywords": ["파이썬 둘러보기 Standard"], "link": "https://m.blog.naver.com/csj4032/223924524629"},
    {"keywords": ["파이썬 둘러보기 Date"], "link": "https://m.blog.naver.com/csj4032/223924560646"},
    {"keywords": ["Airflow Architecture"], "link": "https://m.blog.naver.com/csj4032/223925152875"},
    {"keywords": ["런던베이글뮤지엄"], "link": "https://m.blog.naver.com/csj4032/223925476680"},
    {"keywords": ["네이버 개발자 센터 가입", "네이버개발자센터"], "link": "https://m.blog.naver.com/csj4032/223925844087"},
    {"keywords": ["Airflow ignore"], "link": "https://m.blog.naver.com/csj4032/223926096620"},
    {"keywords": ["Slack 리마인더", "Slack 리마인더 설정", "Slack 설정"], "link": "https://m.blog.naver.com/csj4032/223926096620"},
    {"keywords": ["Python List Comprehension", "Python Comprehension", "Python List"], "link": "https://m.blog.naver.com/csj4032/223927935180"},
    {"keywords": ["팔란티어(Palantir) RFx 블로그 시리즈", "팔란티어(Palantir) RFx", "팔란티어 블로그"], "link": "https://m.blog.naver.com/csj4032/223929117712"},
    {"keywords": ["파이썬 왈러스 연산자", "파이썬 왈러스", "파이썬 연산자", "Python 왈러스"], "link": "https://m.blog.naver.com/csj4032/223930544260"},
    {"keywords": ["파이썬 Iteration Protocol", "파이썬 Iteration", "Python Iteration Protocol"], "link": "https://m.blog.naver.com/csj4032/223934421842"},
    {"keywords": ["제로 투 원 (Zero to One)", "제로투원 Zero to One", "Zero to One"], "link": "https://m.blog.naver.com/csj4032/223935057219"},
    {"keywords": ["파이썬 Iterator, Generator", "파이썬 Iterator", "파이썬 Coroutine"], "link": "https://m.blog.naver.com/csj4032/223936360808"},
]


def get_search(driver_, link_, keyword_, selector_, match_element="", timeout_=10):
    logging.info(f"Searching for '{keyword_}' in  {selector_},[{match_element}] with link: {link_}")
    try:
        title_elements = WebDriverWait(driver_, timeout_).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector_)))
        for element_ in title_elements:
            href_ = element_.get_attribute("href")
            if href_ == link_:
                logging.info(f"Matched for '{keyword_}' in  {selector_},[{match_element}] with link: {link_}")
                return element_
    except NoSuchElementException as exception_:
        logging.error(f"Element with selector '{selector_}' not found: {exception_}")
    return None


if __name__ == '__main__':
    configuration = Configuration()
    shuffle_posts = random.sample(posts, len(posts))
    for post in shuffle_posts:
        keyword = random.choice(post["keywords"])
        link = post['link']
        driver = setup_firefox_driver(configuration)
        try:
            driver.set_window_size(1280, 1800)
            driver.set_window_position(-1280, 0)
            driver.get(configuration.naver_mobile_url)
            time.sleep(random.uniform(1, 2))
            search_box = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "query")))
            search_box.send_keys(random.choice(post["keywords"]))
            search_box.send_keys(Keys.RETURN)
            matched_element = get_search(driver, link, keyword, "a.aEO4VwHkswcCgUXjRh6w.Lznm151o9qLNLUldttoM", "검색 최상단 영역")
            time.sleep(random.uniform(2, 2))
            if matched_element is None:
                matched_element = get_search(driver, link, keyword, "a.title_link", "인기글 영역")
            time.sleep(random.uniform(2, 2))
            if matched_element is None:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "블로그"))).click()
                logging.info(f"Clicked on '블로그' link to search in blog section.")
                matched_element = get_search(driver, link, keyword, "a.dsc_link", "블로그 영역")
            time.sleep(random.uniform(2, 2))
            if matched_element is not None:
                start_time = time.time()
                matched_element.click()
                utils.window_scroll(driver, int(random.uniform(25, 30)), 0, int(random.uniform(100, 500)), 20, 25, link)
                logging.info(f"Time taken to process '{keyword}': {time.time() - start_time:.2f} seconds")
        except Exception as exception:
            logging.info(f"An error occurred: {exception}")
        finally:
            time.sleep(random.uniform(1, 5))
            driver.quit()
