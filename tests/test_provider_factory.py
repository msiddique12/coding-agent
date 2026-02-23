from unittest.mock import patch

from llm_providers import validate_provider_environment
from llm_providers.openai_provider import OpenAIProvider


def test_validate_provider_environment_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = validate_provider_environment("openai")
    assert result["ok"] is False
    assert result["missing_env"] == ["OPENAI_API_KEY"]


def test_validate_provider_environment_ok(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    result = validate_provider_environment("openai")
    assert result["ok"] is True
    assert result["missing_env"] == []


@patch("llm_providers.openai_provider.OpenAI")
def test_openai_provider_uses_env_api_key(mock_openai, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    provider = OpenAIProvider()

    mock_openai.assert_called_once_with(api_key="test-key")
    assert provider.model == "gpt-test"
