import logging

import tweepy
import pytest
import os
from unittest.mock import patch, MagicMock

from config.configuration import Configuration


@patch('tweepy.Client')
def test_x_connection(mock_client):
    mock_instance = MagicMock()
    mock_client.return_value = mock_instance
    mock_instance.get_me.return_value = {"data": {"id": "123456789", "name": "Test User", "username": "testuser"}}
    config = MagicMock()
    config.x_bearer_token = "mocked_bearer_token"
    client = tweepy.Client(bearer_token=config.x_bearer_token)
    response = client.get_me()
    assert response["data"]["id"] == "123456789"
    assert response["data"]["name"] == "Test User"
    assert response["data"]["username"] == "testuser"
    mock_instance.get_me.assert_called_once()


def test_x_actual_connection():
    config = Configuration()
    x_api_key = config.x_api_key
    x_api_key_secret = config.x_api_key_secret
    x_bearer_token = config.x_bearer_token
    x_access_token = config.x_access_token
    x_access_token_secret = config.x_access_token_secret
    client = tweepy.Client(bearer_token=x_bearer_token, consumer_key=x_api_key, consumer_secret=x_api_key_secret, access_token=x_access_token, access_token_secret=x_access_token_secret)
    response = client.get_me()
    assert response.data is not None, "X API connection failed or returned no data"
    logging.info(f"X API connection successful: {response.data.id}, {response.data.name}, {response.data.username}")


def test_x_get_place_trends():
    config = Configuration()
    consumer_key = config.x_api_key
    consumer_secret = config.x_api_key_secret
    access_token = config.x_access_token
    access_token_secret = config.x_access_token_secret
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api_v1 = tweepy.API(auth)
    korea_woeid = 23424868
    trends_result = api_v1.get_place_trends(id=korea_woeid)
    for trend in trends_result[0]['trends']:
        trend_name = trend['name']
        tweet_volume = trend['tweet_volume']
        if tweet_volume:
            print(f"주제: {trend_name} (트윗 수: {tweet_volume:,})")
        else:
            print(f"주제: {trend_name} (트윗 수: 정보 없음)")
