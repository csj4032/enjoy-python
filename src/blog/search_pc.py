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
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from blog import utils

logging.basicConfig(level=logging.INFO)

posts = [
    {"keywords": ["A+B"], "link": "https://blog.naver.com/csj4032/221651220532"},
    {"keywords": ["Adaptive Query Execution"], "link": "https://blog.naver.com/csj4032/223519550322"},
    {"keywords": ["돈의 심리학", "돈 심리학"], "link": "https://blog.naver.com/csj4032/223523078830"},
    {"keywords": ["칩워, 누가 반도체 전쟁의 최후 승자", "칩워 누가 반도체 전쟁"], "link": "https://blog.naver.com/csj4032/223520452563"},
    {"keywords": ["Slack 새 워크스페이스", "Slack 워크스페이스"], "link": "https://blog.naver.com/csj4032/223901622139"},
    {"keywords": ["신경 끄기 기술", "신경끄기기술"], "link": "https://blog.naver.com/csj4032/223914881533"},
    {"keywords": ["Iceberg Deltalake"], "link": "https://blog.naver.com/csj4032/223914908740"},
    {"keywords": ["30가지 패턴 분산 시스템", "패턴 분산 시스템"], "link": "https://blog.naver.com/csj4032/223915376396"},
    {"keywords": ["Java JDK", "Java JDK 설치"], "link": "https://blog.naver.com/csj4032/223915459310"},
    {"keywords": ["파이썬 설치", "파이썬설치"], "link": "https://blog.naver.com/csj4032/223915465848"},
    {"keywords": ["Java 개발환경 설정", "Java 개발환경"], "link": "https://blog.naver.com/csj4032/223915500234"},
    {"keywords": ["일과 일상 나"], "link": "https://blog.naver.com/csj4032/223915566048"},
    {"keywords": ["파이썬이란"], "link": "https://blog.naver.com/csj4032/223916421094"},
    {"keywords": ["팔란티어(Palantir), 팔란티어 Palantir"], "link": "https://blog.naver.com/csj4032/223916603908"},
    {"keywords": ["용기와 겁쟁이"], "link": "https://blog.naver.com/csj4032/223917250644"},
    {"keywords": ["파이썬 기초, 자료형", "파이썬 자료형"], "link": "https://blog.naver.com/csj4032/223920432120"},
    {"keywords": ["파이썬 제어"], "link": "https://blog.naver.com/csj4032/223920432120"},
    {"keywords": ["파이썬 입출"], "link": "https://blog.naver.com/csj4032/223920674251"},
    {"keywords": ["파이썬 반복", "파이썬 반복문"], "link": "https://blog.naver.com/csj4032/223920710832"},
    {"keywords": ["파이썬 Package"], "link": "https://blog.naver.com/csj4032/223921565651"},
    {"keywords": ["파이썬 Exception"], "link": "https://blog.naver.com/csj4032/223922827334"},
    {"keywords": ["Git", "Git이란"], "link": "https://blog.naver.com/csj4032/223922857147"},
    {"keywords": ["Autonomous Future"], "link": "https://blog.naver.com/csj4032/223922988417"},
    {"keywords": ["파이썬 둘러보기 Built-in"], "link": "https://blog.naver.com/csj4032/223923023951"},
    {"keywords": ["Tungsten UnsafeRow"], "link": "https://blog.naver.com/csj4032/223923130905"},
    {"keywords": ["파이썬 둘러보기 Standard"], "link": "https://blog.naver.com/csj4032/223924524629"},
    {"keywords": ["파이썬 둘러보기 Date"], "link": "https://blog.naver.com/csj4032/223924560646"},
    {"keywords": ["Airflow Architecture"], "link": "https://blog.naver.com/csj4032/223925152875"},
    {"keywords": ["런던베이글뮤지엄"], "link": "https://blog.naver.com/csj4032/223925476680"},
    {"keywords": ["네이버 개발자 센터 가입", "네이버개발자센터"], "link": "https://blog.naver.com/csj4032/223925844087"},
    {"keywords": ["Airflow ignore"], "link": "https://blog.naver.com/csj4032/223926096620"},
    {"keywords": ["Slack 리마인더", "Slack 리마인더 설정", "Slack 설정"], "link": "https://blog.naver.com/csj4032/223926096620"},
    {"keywords": ["Python List Comprehension", "Python Comprehension", "Python List"], "link": "https://blog.naver.com/csj4032/223927935180"},
    {"keywords": ["팔란티어(Palantir) RFx 블로그 시리즈", "팔란티어(Palantir) RFx", "팔란티어 블로그"], "link": "https://m.blog.naver.com/csj4032/223929117712"},
    {"keywords": ["Python 왈러스 연산자", "Python 왈러스", "Python 연산자"], "link": "https://m.blog.naver.com/csj4032/223930544260"},
    {"keywords": ["파이썬 왈러스 연산자", "파이썬 왈러스", "파이썬 연산자", "Python 왈러스"], "link": "https://blog.naver.com/csj4032/223930544260"},
    {"keywords": ["파이썬 Iteration Protocol", "파이썬 Iteration", "Python Iteration Protocol"], "link": "https://blog.naver.com/csj4032/223934421842"},
    {"keywords": ["제로 투 원 (Zero to One)", "제로투원 Zero to One", "Zero to One"], "link": "https://blog.naver.com/csj4032/223935057219"},
]


def setup_driver():
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
    # options.add_argument("--headless")
    service = FirefoxService(executable_path="/opt/homebrew/bin/geckodriver")
    return webdriver.Firefox(service=service, options=options)


def get_search_top(driver_, link_, keyword_, selector, match_element=""):
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
    shuffle_posts = random.sample(posts, len(posts))
    for post in shuffle_posts:
        keyword = random.choice(post["keywords"])
        link = post['link']
        driver = setup_driver()
        try:
            driver.set_window_size(1280, 1800)
            driver.set_window_position(-1280, 0)
            driver.get("https://www.naver.com")
            search_box = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "query")))
            search_box.send_keys(random.choice(post["keywords"]))
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(1, 3))

            matched_element = get_search_top(driver, link, keyword, "a.link_tit", "검색 최상단 매치")

            if matched_element is None:
                matched_element = get_search_top(driver, link, keyword, "a.title_link", "검색 인기글 매치")

            if matched_element is None:
                blog_tab = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "블로그")))
                blog_tab.click()
                time.sleep(random.uniform(1, 3))
                blog_elements = driver.find_elements(By.CSS_SELECTOR, "a.title_link")

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
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(matched_element)).click()
                time.sleep(random.uniform(1, 10))
                WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
                driver.switch_to.window(driver.window_handles[1])
                main_iframe = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "mainFrame")))
                driver.switch_to.frame(main_iframe)
                time.sleep(random.uniform(1, 10))
                logging.info(f"Successfully navigated to {keyword} post: {link}")
                utils.window_scroll(driver, 20, 0, random.uniform(100, 500), 25, 35, link)
                driver.switch_to.default_content()
                logging.info(f"Time taken to process '{keyword}': {time.time() - start_time:.2f} seconds")
            else:
                logging.info(f"No matching element found for '{keyword}' in search results.")
        except Exception as exception:
            logging.info(f"An error occurred: {exception}")
        finally:
            time.sleep(random.uniform(1, 10))
            driver.quit()
