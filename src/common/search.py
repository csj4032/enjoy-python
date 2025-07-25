import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from typing import Type, TypeVar, List, Dict, Any

import requests
from bs4 import BeautifulSoup
from newspaper import Article

from config.configuration import Configuration

T = TypeVar("T")


@dataclass
class NewsItem:
    title: Optional[str] = None
    snippet: Optional[str] = None
    url: Optional[str] = None
    picture: Optional[str] = None
    source: Optional[str] = None


@dataclass
class TrendItem:
    title: Optional[str] = None
    approx_traffic: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    pub_date: Optional[str] = None
    picture: Optional[str] = None
    picture_source: Optional[str] = None
    news_items: List[NewsItem] = field(default_factory=list)

    @staticmethod
    def from_xml(item) -> 'TrendItem':
        return TrendItem(
            title=item.title.text if item.title else None,
            approx_traffic=item.find('ht:approx_traffic').text if item.find('ht:approx_traffic') else None,
            pub_date=item.pubDate.text if item.pubDate else None,
            picture=item.find('ht:picture').text if item.find('ht:picture') else None,
            picture_source=item.find('ht:picture_source').text if item.find('ht:picture_source') else None,
            news_items=[
                NewsItem(
                    title=news_item_tag.find('ht:news_item_title').text if news_item_tag.find('ht:news_item_title') else None,
                    url=news_item_tag.find('ht:news_item_url').text if news_item_tag.find('ht:news_item_url') else None,
                    picture=news_item_tag.find('ht:news_item_picture').text if news_item_tag.find('ht:news_item_picture') else None,
                    source=news_item_tag.find('ht:news_item_source').text if news_item_tag.find('ht:news_item_source') else None
                )
                for news_item_tag in item.find_all('ht:news_item')
            ]
        )


@dataclass
class Blog:
    title: str
    feed_link: str
    description: str
    nick_name: str
    link: str
    mobile_link: str
    postdate: str

    def __init__(self, nick_name: str, mobile_link: str, title: str = None, feed_link: str = None, description: str = None, link: str = None, postdate: str = None) -> None:
        self.nick_name = nick_name
        self.mobile_link = mobile_link
        self.title = title
        self.feed_link = feed_link
        self.description = description
        self.link = link
        self.postdate = postdate

    @staticmethod
    def from_dict(data: Dict) -> 'Blog':
        return Blog(
            title=data.get("title", ""),
            feed_link=data.get("link", ""),
            description=data.get("description", ""),
            nick_name=data.get("bloggername", ""),
            link=f"https://{data.get("bloggerlink", "")}",
            mobile_link=f"https://{data.get("bloggerlink", "").replace('blog.naver.com', 'm.blog.naver.com')}",
            postdate=data.get("postdate", "")
        )


@dataclass
class NaverSearchBlogResult:
    lastBuildDate: str
    total: int
    start: int
    display: int
    items: List[Blog]

    @staticmethod
    def from_dict(data: Dict) -> 'NaverSearchBlogResult':
        return NaverSearchBlogResult(
            lastBuildDate=data.get("lastBuildDate", ""),
            total=data.get("total", 0),
            start=data.get("start", 0),
            display=data.get("display", 0),
            items=[Blog.from_dict(item) for item in data.get("items", [])]
        )


@dataclass
class News:
    title: str
    original_link: str
    link: str
    article: str
    top_image: str
    images: list[str]
    authors: list[str]
    description: str
    public_datetime: datetime
    public_article_datetime: str

    @staticmethod
    def from_dict(data: Dict) -> 'News':
        article = get_article(data.get("originallink", ""))
        return News(
            title=data.get("title", ""),
            original_link=data.get("originallink", ""),
            link=data.get("link", ""),
            article=re.sub(r'(\n|<br\s*/?>)', '', article.text) if article and hasattr(article, "text") else "",
            top_image=article.top_image if article else "",
            images=article.images if article else [],
            authors=article.authors if article else [],
            description=data.get("description", ""),
            public_datetime=datetime.strptime(data.get("pubDate", ""), "%a, %d %b %Y %H:%M:%S %z"),
            public_article_datetime=article.publish_date if article else ""
        )


@dataclass
class NaverSearchNewsResult:
    lastBuildDate: str
    total: int
    start: int
    display: int
    items: List[News]

    @staticmethod
    def from_dict(data: Dict) -> 'NaverSearchNewsResult':
        result = NaverSearchNewsResult(
            lastBuildDate=data.get("lastBuildDate", ""),
            total=data.get("total", 0),
            start=data.get("start", 0),
            display=data.get("display", 0),
            items=[News.from_dict(item) for item in data.get("items", []) if item["originallink"] != ""]
        )
        return result


def get_google_trends(google_trends_rss_url: str, geo="KR") -> List[TrendItem]:
    response = requests.get(f"{google_trends_rss_url}?geo={geo}")
    soup = BeautifulSoup(response.content, 'xml')
    return [TrendItem.from_xml(item) for item in soup.find_all('item')]


def get_naver_api_response(query: str, url: str, client_id: str, client_secret: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[dict]:
    time.sleep(random.uniform(0.5, 1.5))
    try:
        response = requests.get(url, headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}, params={"query": query, "display": display, "start": start, "sort": sort})
        response.raise_for_status()
        result = response.json()
        logging.info(f"Fetched Naver API results for query: {query}, Total items: {len(result.get('items', []))}")
        return result
    except Exception as e:
        logging.error(f"Error fetching Naver API results: {e} By query: {query}")
        return {}


def get_class_type(type_: str) -> Type[T]:
    if type_ == "blog":
        return NaverSearchBlogResult
    elif type_ == "news":
        return NaverSearchNewsResult
    else:
        raise ValueError(f"Unknown type: {type_}")


def get_article(url: str, language: str = "ko") -> Article | None:
    try:
        article = Article(url, language=language)
        article.download()
        article.parse()
        return article
    except Exception as exception:
        logging.error(f"Error fetching article from {url}: {exception}")
        return None


def deduplicate_by_attr(items: list, attr: str) -> list:
    seen = set()
    return [item for item in items if (v := getattr(item, attr, None)) and not (v in seen or seen.add(v))]


def get_naver_search_by_query(configuration: Configuration, type_: str, query: str) -> List[T]:
    url = f"{configuration.naver_api_search_url}/{type_}"
    class_ = get_class_type(type_)
    client_id = configuration.naver_api_client_id
    client_secret = configuration.naver_api_client_secret
    display = configuration.naver_api_search_display
    page = configuration.naver_api_search_page
    sort = configuration.naver_api_search_sort
    return deduplicate_by_attr([item for page_no in range(page) for item in class_.from_dict(get_naver_api_response(query, url, client_id, client_secret, display, (page_no + 1) * display - (display - 1), sort)).items], "link")


def get_naver_search_by_trends(configuration: Configuration, type_: str) -> List[Dict[str, Any]]:
    return [{"title": trend.title, "items": get_naver_search_by_query(configuration, type_, trend.title)} for trend in get_google_trends(configuration.google_trends_rss_url, geo="KR")]


def get_naver_news_article_by_trends(configuration: Configuration) -> List[News]:
    return [news for trend in get_naver_search_by_trends(configuration, "news") for news in trend.get("items", [])]


def get_naver_mobile_blog_by_trends(configuration: Configuration) -> list[Blog]:
    return [blog for trend in get_naver_search_by_trends(configuration, "blog") for blog in trend.get("items", []) if "m.blog.naver.com" in blog.mobile_link]


def get_naver_news_by_from_to(configuration: Configuration, query: str, from_datetime: datetime, to_datetime: datetime) -> List[News]:
    return [news for news in get_naver_search_by_query(configuration, "news", query=query) if from_datetime < news.public_datetime < to_datetime]
