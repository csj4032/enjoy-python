import logging
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from config.configuration import Configuration

logging.basicConfig(level=logging.INFO)


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
class Item:
    title: str
    feed_link: str
    description: str
    nick_name: str
    link: str
    mobile_link: str
    postdate: str

    @staticmethod
    def from_dict(data: Dict) -> 'Item':
        return Item(
            title=data.get("title", ""),
            feed_link=data.get("link", ""),
            description=data.get("description", ""),
            nick_name=data.get("bloggername", ""),
            link=f"https://{data.get("bloggerlink", "")}",
            mobile_link=f"https://{data.get("bloggerlink", "").replace('blog.naver.com', 'm.blog.naver.com')}",
            postdate=data.get("postdate", "")
        )


@dataclass
class NaverSearchResult:
    lastBuildDate: str
    total: int
    start: int
    display: int
    items: List[Item]

    @staticmethod
    def from_dict(data: Dict) -> 'NaverSearchResult':
        return NaverSearchResult(
            lastBuildDate=data.get("lastBuildDate", ""),
            total=data.get("total", 0),
            start=data.get("start", 0),
            display=data.get("display", 0),
            items=[Item.from_dict(item) for item in data.get("items", [])]
        )


def get_google_trends(google_trends_rss_url: str, geo="KR") -> List[TrendItem]:
    response = requests.get(f"{google_trends_rss_url}?geo={geo}")
    soup = BeautifulSoup(response.content, 'xml')
    return [TrendItem.from_xml(item) for item in soup.find_all('item')]


def get_naver_blog_results_by_trend(query: str, url: str, client_id: str, client_secret: str, display: int = 100, page: int = 2) -> List[NaverSearchResult]:
    return [NaverSearchResult.from_dict(get_naver_blog_api_response(query, url, client_id, client_secret, display, page_no * display - (display - 1), "date")) for page_no in range(1, page)]


def get_naver_blog_results_with_trends(configuration: Configuration) -> List[Dict[str, Item]]:
    trends = get_google_trends(configuration.google_trends_rss_url, geo="KR")
    result = [{"keyword": trend.title,
               "blogs": get_naver_blog_results_by_trend(trend.title, configuration.naver_api_search_blog_url, configuration.naver_api_client_id, configuration.naver_api_client_secret, configuration.naver_api_display)}
              for trend in trends]
    return [{"keyword": item["keyword"], "blog": blog_item} for item in result for naver_result in item["blogs"] for blog_item in naver_result.items]


def get_mobile_naver_blog_results_by_trend(configuration: Configuration) -> List[Item]:
    blogs = [value["blog"] for value in get_naver_blog_results_with_trends(configuration) if "m.blog.naver.com" in value["blog"].mobile_link]
    return random.sample(blogs, len(blogs))


def get_naver_blog_api_response(query: str, url: str, client_id: str, client_secret: str, display: int = 10, start: int = 1, sort: str = "sim") -> Optional[dict]:
    try:
        response = requests.get(url, headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}, params={"query": query, "display": display, "start": start, "sort": sort})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching Naver blog search results: {e} By query: {query}")
        return {}
