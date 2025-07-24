"""
Constants module for centralized management of prompts, models, and configurations.
"""


class Prompts:
    """Blog comment prompts for different use cases."""
    
    # Standard blog comment prompt (50 characters)
    BLOG_COMMENT = (
        "'{0}' 이라는 제목의 블로그 글에 대한 코멘트를 하나만 간단하게 작성해줘. "
        "아래 '{1}' 내용을 참고해서, 방문자 입장에서 담백하고 자연스럽게 작성해야 해. "
        "코멘트는 50자 내외로 해줘"
    )
    
    # Recommendation page comment prompt  
    RECOMMEND_COMMENT = (
        "'{0}' 이라는 제목의 블로그 포스트에 대한 코멘트를 하나만 간단하게 작성해줘 "
        "아래 '{1}' 내용을 바탕으로, 방문자 입장에서 담백하고 자연스럽게 작성해야 해. "
        "코멘트 길이는 50자 내외로 맞춰 줘."
    )
    
    # URL-based comment with category prompt
    URL_COMMENT = (
        "'{0}' 이라는 제목의 {1} 카테고리 블로그 글에 대한 코멘트를 작성해줘. "
        "아래 '{2}' 내용을 참고해서, 대한민국 남성 방문자 입장에서 자연스러운 한 문장으로 작성해야 해."
    )


class Models:
    """AI model constants."""
    
    # Gemini models
    GEMINI_DEFAULT = "gemini-2.0-flash"
    
    # Ollama models  
    OLLAMA_DEFAULT = "gemma3:latest"


class APIConfig:
    """API configuration constants."""
    
    # Gemini generation config
    GEMINI_GENERATION_CONFIG = {
        "temperature": 0.7,
        "max_output_tokens": 2048,
        "top_p": 1.0,
        "top_k": 32,
    }
    
    # Default API URLs
    OLLAMA_DEFAULT_URL = "http://localhost:11434/api/generate"


class Timeouts:
    """Timeout constants for web operations."""
    
    SHORT = 1
    DEFAULT = 5
    MEDIUM = 10
    LONG = 30


class Selectors:
    """Common CSS selectors."""
    
    # Blog post selectors
    POST_CARD = "div.card__reUkU"
    POST_TITLE = "strong.title__UUn4H"
    POST_LINK = "a.link__Awlz5"
    
    # Comment selectors
    REPLY_BUTTON = "a.btn_reply"
    COMMENT_TEXTAREA = "naverComment__write_textarea"
    COMMENT_SUBMIT = "button.u_cbox_btn_upload"
    
    # Navigation selectors
    MORE_BUTTON = "button.button_show__VRCFg"
    BUDDY_ADD_BUTTON = "[data-click-area='ebc.add']"