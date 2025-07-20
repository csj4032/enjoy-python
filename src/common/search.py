import logging
import random
from dataclasses import dataclass, field
from typing import Optional
from typing import Type, TypeVar, List, Dict, Any

import requests
from bs4 import BeautifulSoup

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
    description: str
    pub_datetime: str

    @staticmethod
    def from_dict(data: Dict) -> 'News':
        return News(
            title=data.get("title", ""),
            original_link=data.get("originallink", ""),
            link=data.get("link", ""),
            description=data.get("description", ""),
            pub_datetime=data.get("pubDate", "")
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
            items=[News.from_dict(item) for item in data.get("items", [])]
        )
        return result


def get_google_trends(google_trends_rss_url: str, geo="KR") -> List[TrendItem]:
    response = requests.get(f"{google_trends_rss_url}?geo={geo}")
    soup = BeautifulSoup(response.content, 'xml')
    logging.info(f"Fetched Google Trends RSS feed for geo: {geo}, total items: {len(soup.find_all('item'))}")
    return [TrendItem.from_xml(item) for item in soup.find_all('item')]


def get_naver_api_response(query: str, url: str, client_id: str, client_secret: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[dict]:
    try:
        response = requests.get(url, headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}, params={"query": query, "display": display, "start": start, "sort": sort})
        response.raise_for_status()
        result = response.json()
        logging.info(f"Fetched Naver API results for query: {query}, total items: {result.get('total', 0)}")
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


def get_naver_search_by_query(configuration: Configuration, type_: str, query: str, page: int = 2) -> List[T]:
    url = f"{configuration.naver_api_search_url}/{type_}"
    class_ = get_class_type(type_)
    client_id = configuration.naver_api_client_id
    client_secret = configuration.naver_api_client_secret
    display = configuration.naver_api_search_display
    return [class_.from_dict(get_naver_api_response(query, url, client_id, client_secret, display, page_no * display - (display - 1), "date")) for page_no in range(1, page)]


def get_naver_search_by_trends(configuration: Configuration, type_: str) -> List[Dict[str, Any]]:
    return [{"trend": trend.title, "results": get_naver_search_by_query(configuration, type_, trend.title)} for trend in get_google_trends(configuration.google_trends_rss_url, geo="KR")]


def get_naver_mobile_blog_by_trends(configuration: Configuration) -> List[Blog]:
    return [blog for trend in get_naver_search_by_trends(configuration, "blog") for result in trend.get("results", []) for blog in result.items if "m.blog.naver.com" in blog.mobile_link]
