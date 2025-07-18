import logging
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

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


@dataclass
class Item:
    title: str
    link: str
    description: str
    bloggername: str
    bloggerlink: str
    postdate: str

    @staticmethod
    def from_dict(data: Dict) -> 'Item':
        return Item(
            title=data.get("title", ""),
            link=data.get("link", ""),
            description=data.get("description", ""),
            bloggername=data.get("bloggername", ""),
            bloggerlink=data.get("bloggerlink", ""),
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


def get_google_trends(geo="KR") -> List:
    url = f"https://trends.google.com/trending/rss?geo={geo}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    all_trends = []
    for item in soup.find_all('item'):
        news_list = []
        for news_item_tag in item.find_all('ht:news_item'):
            news_item = NewsItem(
                title=news_item_tag.find('ht:news_item_title').text,
                url=news_item_tag.find('ht:news_item_url').text,
                picture=news_item_tag.find('ht:news_item_picture').text,
                source=news_item_tag.find('ht:news_item_source').text
            )
            news_list.append(news_item)

        trend_item = TrendItem(
            title=item.title.text,
            approx_traffic=item.find('ht:approx_traffic').text,
            pub_date=item.pubDate.text,
            picture=item.find('ht:picture').text,
            picture_source=item.find('ht:picture_source').text,
            news_items=news_list
        )
        all_trends.append(trend_item)
    return all_trends


def get_naver_search_results(query: str) -> List[NaverSearchResult]:
    url = "https://openapi.naver.com/v1/search/blog"
    params = {"query": f"{query}", "display": 10, "start": 1, "sort": "date"}
    results = []
    for page_no in range(1, 2):
        params["start"] = page_no * params["display"] - (params["display"] - 1)
        logging.info(f"Fetching page {page_no} with params: {params}")
        try:
            response = requests.get(url=url, headers=headers, params=params)
            response.raise_for_status()
            time.sleep(random.uniform(0, 1))
            if response.status_code == 200:
                results.append(NaverSearchResult.from_dict(response.json()))
            else:
                logging.error(f"Failed to fetch page {page_no}, status code: {response.status_code}")
        except Exception as e:
            logging.error(f"An error occurred while fetching page {page_no}: {e}")
            continue
    return [item for result_ in results for item in result_.items]


if __name__ == '__main__':
    trends = get_google_trends(geo="KR")
    logging.info(f"Fetched {trends} Google Trends items.")
    result = [{"keyword": trend.title, "blogs": get_naver_search_results(trend.title)} for trend in trends]
    exploded = [ {"keyword": item["keyword"], "blog": blog} for item in result for blog in item["blogs"]]
    logging.info(f"Fetched {len(result)} Naver search results for Google Trends.")
    for item in exploded:
        logging.info(f"Keyword: {item['keyword']}, Blog Title: {item['blog'].title}, Link: {item['blog'].link}")
