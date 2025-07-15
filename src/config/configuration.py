from src.config.variables import Variables


class Configuration:
    def __init__(self, environment: str = None):
        self.variables = Variables(environment)
        self.variables.configure()
        self.environment = self.variables.environment
        self.firefox_profile_path = self.variables.firefox_profile_path
        self.edge_profile_path = self.variables.edge_profile_path
        self.gemini_api_key = self.variables.gemini_api_key
        self.gemini_model = self.variables.gemini_model
        self.naver_mobile_url = self.variables.naver_mobile_url
        self.naver_blog_mobile_url = self.variables.naver_blog_mobile_url
        self.naver_blog_mobile_buddy_list_url = self.variables.naver_blog_mobile_buddy_list_url
        self.naver_blog_mobile_recommendation_url = self.variables.naver_blog_mobile_recommendation_url
        self.naver_blog_mobile_feed_list_url = self.variables.naver_blog_mobile_feed_list_url
        self.iphone_user_agent = self.variables.iphone_user_agent

    def __getattr__(self, item):
        if hasattr(self.variables, item):
            return getattr(self.variables, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
