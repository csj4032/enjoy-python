from common.search import get_google_trends, get_naver_search_by_trends, get_naver_mobile_blog_by_trends, get_naver_news_article_by_trends
from config.configuration import Configuration


def test_get_google_trend():
    configuration = Configuration()
    configuration.set_browser_headless(True)
    trend = get_google_trends(configuration.google_trends_rss_url)
    assert trend is not None, "Failed to fetch Google Trends"
    assert isinstance(trend, list), "Trend should be a list"
    assert len(trend) > 0, "Trend list should not be empty"


def test_get_naver_news():
    configuration = Configuration()
    configuration.set_naver_api_search_display(100)
    configuration.set_naver_api_search_page(2)
    news_by_trends = get_naver_search_by_trends(configuration, "news")
    for trend in news_by_trends:
        for result in trend['results']:
            for item in result.items:
                print(f"trends: {trend['trend']} - {item.title} - {item.link} - {item.description}")


def test_get_naver_news_article_by_trends():
    configuration = Configuration()
    configuration.set_naver_api_search_display(10)
    configuration.set_naver_api_search_page(1)
    news_contents = get_naver_news_article_by_trends(configuration)
    for news in news_contents:
        print(f"news: {news}")


def test_get_naver_blog():
    configuration = Configuration()
    configuration.set_naver_api_search_display(1)
    blogs = get_naver_search_by_trends(configuration, "blog")
    print(blogs)


def test_get_naver_mobile_blog_by_trends():
    configuration = Configuration()
    configuration.set_naver_api_search_display(1)
    configuration.set_naver_api_search_page(3)
    blogs_by_trends = get_naver_mobile_blog_by_trends(configuration)
    for trend in blogs_by_trends:
        print(trend)
