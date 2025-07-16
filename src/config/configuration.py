from src.config.variables import Variables


class Configuration:
    def __init__(self, environment: str = None):
        self.variables = Variables(environment)
        self.variables.configure()
        self.environment = self.variables.environment
        self.gemini_api_key = self.variables.gemini_api_key
        self.gemini_model = self.variables.gemini_model
        self.naver_mobile_url = self.variables.naver_mobile_url
        self.naver_blog_mobile_url = self.variables.naver_blog_mobile_url
        self.naver_blog_mobile_buddy_list_url = self.variables.naver_blog_mobile_buddy_list_url
        self.naver_blog_mobile_recommendation_url = self.variables.naver_blog_mobile_recommendation_url
        self.naver_blog_mobile_feed_list_url = self.variables.naver_blog_mobile_feed_list_url
        self.mmix_naver_blog_mobile_url = self.variables.mmix_naver_blog_mobile_url
        self.mmix_naver_blog_url = self.variables.mmix_naver_blog_url
        self.browser_configuration = BrowserConfiguration(self.variables)

    def __getattr__(self, item):
        if hasattr(self.variables, item):
            return getattr(self.variables, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def set_browser_headless(self, headless: bool):
        self.browser_configuration.headless = headless
        return self

    def get_browser_headless(self):
        return self.browser_configuration.headless

    def get_browser_firefox_profile_path(self):
        return self.browser_configuration.firefox_profile_path

    def get_browser_edge_profile_path(self):
        return self.browser_configuration.edge_profile_path

    def get_browser_edge_profile(self):
        return self.browser_configuration.edge_profile

    def get_browser_iphone_user_agent(self):
        return self.browser_configuration.iphone_user_agent

    def get_browser_geckodriver_path(self):
        return self.browser_configuration.geckodriver_path

    def get_browser_msedgedriver_path(self):
        return self.browser_configuration.msedgedriver_path


class BrowserConfiguration:
    def __init__(self, variables: Variables = None):
        self.variables = variables
        self.headless = True
        self.firefox_profile_path = self.variables.firefox_profile_path
        self.edge_profile_path = self.variables.edge_profile_path
        self.edge_profile = self.variables.edge_profile
        self.iphone_user_agent = self.variables.iphone_user_agent
        self.geckodriver_path = self.variables.geckodriver_path
        self.msedgedriver_path = self.variables.msedgedriver_path

    def __getattr__(self, item):
        if hasattr(self.variables, item):
            return getattr(self.variables, item)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")
