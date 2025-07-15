import pytest

from src.config.configuration import Configuration


def test_configuration():
    configuration = Configuration()
    assert configuration.environment == "local"
    assert configuration.kafka_property.get_bootstrap_servers() == "localhost:9092"


def test_configuration_production():
    configuration = Configuration("production")
    assert configuration.environment == "production"
    assert configuration.kafka_property.get_bootstrap_servers() == "production-kafka:9092"
