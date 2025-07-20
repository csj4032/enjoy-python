from common.search import get_google_trends, get_naver_search_by_trends, get_naver_mobile_blog_by_trends
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
    configuration.set_naver_api_display(1)
    news = get_naver_search_by_trends(configuration, "news")
    print(news)


def test_get_naver_blog():
    configuration = Configuration()
    configuration.set_naver_api_display(1)
    blogs = get_naver_search_by_trends(configuration, "blog")
    print(blogs)


def test_get_naver_mobile_blog_by_trends():
    configuration = Configuration()
    configuration.set_naver_api_display(1)
    blogs_by_trends = get_naver_mobile_blog_by_trends(configuration)
    print(blogs_by_trends)
