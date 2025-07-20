from unittest.mock import patch, MagicMock

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from src.common.webs import get_reply_button, get_mmix_reply, call_ollama_api


@patch('src.common.webs.WebDriverWait')
def test_get_reply_button(mock_wait):
    """
    get_reply_button 함수가 클릭 가능한 댓글 버튼을 올바르게 반환하거나,
    TimeoutException 발생 시 None을 반환하는지 테스트합니다.
    """
    driver = MagicMock(spec=WebDriver)
    mock_button = MagicMock()
    mock_wait.return_value.until.return_value = mock_button

    result = get_reply_button(driver)
    assert result == mock_button

    mock_wait.return_value.until.side_effect = TimeoutException
    result = get_reply_button(driver)
    assert result is None


@patch('src.common.webs.WebDriverWait')
def test_get_mmix_reply(mock_wait):
    """
    get_mmix_reply 함수가 유효한 blogId를 올바르게 식별하고,
    유효하지 않은 경우 False를 반환하며,
    TimeoutException을 적절히 처리하는지 테스트합니다.
    """
    driver = MagicMock(spec=WebDriver)
    mock_element = MagicMock()

    # 테스트 케이스 1: 유효한 blogId
    mock_element.get_attribute.return_value = "https://m.blog.naver.com?blogId=csj4032"
    mock_wait.return_value.until.return_value = [mock_element]
    result = get_mmix_reply(driver)
    assert result is True, "유효한 blogId에 대해 True를 반환해야 합니다."

    # 테스트 케이스 2: 유효하지 않은 blogId
    mock_element.get_attribute.return_value = "https://m.blog.naver.com?blogId=other"
    result = get_mmix_reply(driver)
    assert result is False, "유효하지 않은 blogId에 대해 False를 반환해야 합니다."

    # 테스트 케이스 3: TimeoutException
    mock_wait.return_value.until.side_effect = TimeoutException
    result = get_mmix_reply(driver)
    assert result is False, "TimeoutException 발생 시 False를 반환해야 합니다."


@patch('src.common.webs.requests.post')
def test_call_ollama_api_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "Generated response"}
    mock_post.return_value = mock_response

    result = call_ollama_api("Test prompt")
    assert result == "Generated response"
    mock_post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={"model": "gemma3:latest", "prompt": "Test prompt", "stream": False},
    )


@patch('src.common.webs.requests.post')
def test_call_ollama_api_failure(mock_post):
    # Mock failed response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as excinfo:
        call_ollama_api("Test prompt")

    assert "Request failed: 500 - Internal Server Error" in str(excinfo.value)
    mock_post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={"model": "gemma3:latest", "prompt": "Test prompt", "stream": False},
    )
