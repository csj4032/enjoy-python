from typing import Any
from src.config.variables import Variables


class Configuration:
    def __init__(self, environment: str | None = None) -> None:
        self.variables = Variables(environment)
        self.variables.configure()
        self.environment = self.variables.environment
        self.gemini_api_key = self.variables.gemini_api_key
        self.gemini_model = self.variables.gemini_model
        self.ollama_api_url = self.variables.ollama_api_url
        self.ollama_default_model = self.variables.ollama_default_model
        self.google_trends_rss_url = self.variables.google_trends_rss_url
        self.x_api_key = self.variables.x_api_key
        self.x_api_key_secret = self.x_api_key_secret
        self.x_bearer_token = self.variables.x_bearer_token
        self.x_access_token = self.variables.x_access_token
        self.x_access_token_secret = self.variables.x_access_token_secret
        self.naver_api_client_id = self.variables.naver_api_client_id
        self.naver_api_client_secret = self.variables.naver_api_client_secret
        self.naver_api_search_url = self.variables.naver_api_search_url
        self.naver_api_search_display = self.variables.naver_api_search_display
        self.naver_api_search_page = self.variables.naver_api_search_page
        self.naver_api_search_sort = self.variables.naver_api_search_sort
        self.naver_mobile_url = self.variables.naver_mobile_url
        self.naver_blog_mobile_url = self.variables.naver_blog_mobile_url
        self.naver_blog_mobile_buddy_list_url = self.variables.naver_blog_mobile_buddy_list_url
        self.naver_blog_mobile_recommendation_url = self.variables.naver_blog_mobile_recommendation_url
        self.naver_blog_mobile_feed_list_url = self.variables.naver_blog_mobile_feed_list_url
        self.mmix_naver_blog_mobile_url = self.variables.mmix_naver_blog_mobile_url
        self.mmix_naver_blog_url = self.variables.mmix_naver_blog_url
        self.naver_blog_reply_limit_message = self.variables.naver_blog_reply_limit_message
        self.naver_blog_buddy_daily_add_limit_message = self.variables.naver_blog_buddy_daily_add_limit_message
        self.naver_blog_buddy_request_pending_cancel_message = self.variables.naver_blog_buddy_request_pending_cancel_message
        self.naver_blog_buddy_user_limit_reached_message = self.variables.naver_blog_buddy_user_limit_reached_message
        self.browser_configuration = BrowserConfiguration(self.variables)

    def __getattr__(self, item: str) -> Any:
        if hasattr(self.variables, item):
            return getattr(self.variables, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def set_browser_headless(self, headless: bool) -> None:
        self.browser_configuration.headless = headless

    def set_naver_api_search_display(self, display: int) -> None:
        self.naver_api_search_display = display

    def set_naver_api_search_page(self, page: int) -> None:
        self.naver_api_search_page = page

    def get_browser_headless(self) -> bool:
        return self.browser_configuration.headless

    def get_browser_firefox_profile_path(self) -> str | None:
        return self.browser_configuration.firefox_profile_path

    def get_browser_firefox_window_size(self) -> str | None:
        return self.browser_configuration.firefox_window_size

    def get_browser_edge_profile_path(self) -> str | None:
        return self.browser_configuration.edge_profile_path

    def get_browser_edge_profile(self) -> str | None:
        return self.browser_configuration.edge_profile

    def get_browser_edge_window_size(self) -> str | None:
        return self.browser_configuration.edge_window_size

    def get_browser_iphone_user_agent(self) -> str | None:
        return self.browser_configuration.iphone_user_agent

    def get_browser_geckodriver_path(self) -> str | None:
        return self.browser_configuration.geckodriver_path

    def get_browser_msedgedriver_path(self) -> str | None:
        return self.browser_configuration.msedgedriver_path


class BrowserConfiguration:
    def __init__(self, variables: Variables | None = None) -> None:
        self.variables = variables
        self.headless = True
        self.firefox_profile_path = self.variables.firefox_profile_path
        self.firefox_window_size = self.variables.firefox_window_size
        self.edge_profile_path = self.variables.edge_profile_path
        self.edge_profile = self.variables.edge_profile
        self.edge_window_size = self.edge_window_size
        self.iphone_user_agent = self.variables.iphone_user_agent
        self.geckodriver_path = self.variables.geckodriver_path
        self.msedgedriver_path = self.variables.msedgedriver_path

    def __getattr__(self, item: str) -> Any:
        if hasattr(self.variables, item):
            return getattr(self.variables, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
