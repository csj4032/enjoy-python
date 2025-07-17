import os
import logging

from dotenv import load_dotenv


class Variables:
    def __init__(self, environment: str = None):
        self.environment = environment
        self.firefox_profile_path = None
        self.firefox_window_size = None
        self.edge_profile_path = None
        self.edge_profile = None
        self.edge_window_size = None
        self.gemini_api_key = None
        self.gemini_model = None
        self.iphone_user_agent = None
        self.naver_mobile_url = None
        self.naver_blog_mobile_url = None
        self.naver_blog_mobile_buddy_list_url = None
        self.naver_blog_mobile_recommendation_url = None
        self.naver_blog_mobile_feed_list_url = None
        self.mmix_naver_blog_mobile_url = None
        self.mmix_naver_blog_url = None
        self.geckodriver_path = None
        self.msedgedriver_path = None
        self.naver_blog_reply_limit_message = None
        self.naver_blog_buddy_daily_add_limit_message = None
        self.naver_blog_buddy_request_pending_cancel_message = None
        self.naver_blog_buddy_user_limit_reached_message = None

    def configure(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        logging.info(f"current_directory: {current_directory}")
        load_dotenv(dotenv_path=f"{current_directory}/envs/.env")
        self.environment = "local"
        self.edge_profile_path = os.getenv('EDGE_PROFILE_PATH')
        self.edge_profile = os.getenv('EDGE_PROFILE')
        self.edge_window_size = os.getenv('EDGE_WINDOW_SIZE', '480,1800')
        self.firefox_profile_path = os.getenv('FIREFOX_PROFILE_PATH')
        self.firefox_window_size = os.getenv('FIREFOX_WINDOW_SIZE', '480,1800')
        self.iphone_user_agent = os.getenv('IPHONE_USER_AGENT')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL')
        self.naver_mobile_url = os.getenv('NAVER_MOBILE_URL')
        self.naver_blog_mobile_url = os.getenv('NAVER_BLOG_MOBILE_URL')
        self.naver_blog_mobile_buddy_list_url = os.getenv('NAVER_BLOG_MOBILE_BUDDY_LIST_URL')
        self.naver_blog_mobile_recommendation_url = os.getenv('NAVER_BLOG_MOBILE_RECOMMENDATION_URL')
        self.naver_blog_mobile_feed_list_url = os.getenv('NAVER_BLOG_MOBILE_FEED_LIST_URL')
        self.mmix_naver_blog_mobile_url = os.getenv('MMIX_NAVER_BLOG_MOBILE_URL')
        self.mmix_naver_blog_url = os.getenv('MMIX_NAVER_BLOG_URL')
        self.geckodriver_path = os.getenv('GECKODRIVER_PATH')
        self.msedgedriver_path = os.getenv('MSEDGEDRIVER_PATH')
        self.naver_blog_reply_limit_message = os.getenv('NAVER_BLOG_REPLY_LIMIT_MESSAGE')
        self.naver_blog_buddy_daily_add_limit_message = os.getenv('NAVER_BLOG_BUDDY_DAiLY_ADD_LIMIT_MESSAGE')
        self.naver_blog_buddy_request_pending_cancel_message = os.getenv('NAVER_BLOG_BUDDY_REQUEST_PENDING_CANCEL_MESSAGE')
        self.naver_blog_buddy_user_limit_reached_message = os.getenv('NAVER_BLOG_BUDDY_USER_LIMIT_REACHED_MESSAGE')
