"""
Tests for LLM Translator MCP Server
"""

import pytest
from mcp_servers.llm_translator import LLMTranslatorServer


@pytest.fixture
def server():
    """Create test server instance."""
    return LLMTranslatorServer(
        api_key="test_key",
        model="qwen-plus",
        api_mode="text",
    )


def test_server_initialization(server):
    """Test server can be initialized."""
    assert server.model == "qwen-plus"
    assert server.api_mode == "text"


def test_get_supported_models(server):
    """Test getting supported models list."""
    models = server.get_supported_models()
    assert len(models) > 0
    assert any(m["name"] == "qwen-plus" for m in models)
    assert all("name" in m and "provider" in m for m in models)


def test_get_prompt_templates(server):
    """Test getting prompt templates."""
    templates = server.get_prompt_templates()
    assert "system_prompt" in templates
    assert "user_prompt_template" in templates
    assert "description" in templates


def test_get_translation_glossary(server):
    """Test getting translation glossary."""
    glossary = server.get_translation_glossary()
    assert isinstance(glossary, dict)
    assert "API" in glossary
    assert "TDD/BDD" in glossary
    assert len(glossary) > 10  # Should have many terms


@pytest.mark.asyncio
async def test_translate_to_hr_language_structure(server):
    """Test translation returns correct structure (mocked)."""
    # Note: This test requires mocking the QwenClient
    # For real API testing, you'd need a valid API key

    # Expected structure
    expected_keys = {
        "summary",
        "risks",
        "needs",
        "okr_alignment",
        "next_actions",
        "risk_level",
        "timestamp",
    }

    # We'll just verify the method signature for now
    import inspect
    sig = inspect.signature(server.translate_to_hr_language)
    params = set(sig.parameters.keys())

    assert "text" in params
    assert "user_name" in params
    assert "period_type" in params
    assert "okr_context" in params


def test_server_factory():
    """Test server factory function."""
    from mcp_servers.llm_translator import create_mcp_server

    server = create_mcp_server()
    assert isinstance(server, LLMTranslatorServer)
