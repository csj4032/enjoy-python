import logging
import random
from datetime import timedelta, datetime

from dateutil.tz import tz

from common.llm import call_ollama_api
from common.search import get_naver_search_by_trends, get_naver_search_by_query, get_naver_news_by_from_to
from config.configuration import Configuration


def test_get_post_content_by_query():
    configuration = Configuration()
    configuration.set_naver_api_search_display(10)
    configuration.set_naver_api_search_page(1)
    query = "팔린티어"
    _to_datetime = datetime.now(tz=tz.gettz("Asia/Seoul"))
    _from_datetime = _to_datetime - timedelta(days=10)
    news_ = get_naver_news_by_from_to(configuration, query, _from_datetime, _to_datetime)
    for news in news_:
        logging.info(f"Title: {news.title}, Link: {news.link}, Naver Date: {news.public_datetime}, Article Date: {news.public_article_datetime}")
    system_prompt = f"{query}에 대한 블로그 컨텐츠를 아래 기사 제목과 내용을 바탕으로 마크다운 형식으로 작성해주세요. 그리고 SEO 검색엔진최적화 시켜서 작성해주세요, 최대한 자연스럽게 정리해서 문단별로 1000-1500 글자로 작성하고 이미지링크를 문단 아래 넣어주세요.\n"
    prompt = system_prompt + "".join([f"제목:{news.title} \n내용: {news.article.strip()} \n이미지링크: {news.top_image}\n" for news in news_])
    logging.info(f"Prompt: {prompt}")
    contents = call_ollama_api(prompt[:20000])
    logging.info(f"Generated contents: {contents}")


def test_get_post_content_by_trends():
    configuration = Configuration()
    configuration.set_naver_api_search_display(3)
    configuration.set_naver_api_search_page(1)
    trends_results = get_naver_search_by_trends(configuration, "news")
    logging.info("Fetched trends results:")
    for trend in trends_results[:1]:
        system_prompt = f"{trend['title']}대한 블로그 컨텐츠를 아래 기사 제목과 내용을 바탕으로 마크다운 형식으로 작성해주세요. 그리고 SEO 검색엔진최적화 시켜서 작성해주세요, 최대한 자연스럽게 정리해서 문단별로 1000-1500 글자로 작성하고 이미지링크를 문단 아래 넣어주세요.\n"
        prompt = system_prompt + "".join([f"제목:{item.title} \n내용: {item.article} \n이미지링크: {item.top_image}\n" for item in trend['items']])
        logging.info(f"Processing {trend['title']} prompt: {prompt}")
        contents = call_ollama_api(prompt)
        logging.info(f"Generated {trend['title']} contents:{contents}")
