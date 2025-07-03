"""
Tests for Hugging Face pull-through caching functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from pulp_hugging_face.app.models import HuggingFaceContent, HuggingFaceRemote
from pulp_hugging_face.app.utils import parse_hf_path, get_content_type_from_filename


class TestHuggingFaceModels:
    """Test Hugging Face model functionality."""

    def test_hugging_face_content_str(self):
        """Test string representation of HuggingFaceContent."""
        content = HuggingFaceContent(
            repo_id="microsoft/DialoGPT-medium",
            repo_type="models",
            relative_path="config.json",
            revision="main",
        )
        expected = "models/microsoft/DialoGPT-medium:main/config.json"
        assert str(content) == expected

    def test_hugging_face_remote_get_remote_artifact_url(self):
        """Test getting remote artifact URL."""
        remote = HuggingFaceRemote(hf_hub_url="https://huggingface.co")

        # Test with models path
        url = remote.get_remote_artifact_url(
            "models/microsoft/DialoGPT-medium/resolve/main/config.json"
        )
        expected = (
            "https://huggingface.co/models/microsoft/DialoGPT-medium/resolve/main/config.json"
        )
        assert url == expected

        # Test with path without prefix
        url = remote.get_remote_artifact_url("microsoft/DialoGPT-medium/resolve/main/config.json")
        expected = (
            "https://huggingface.co/models/microsoft/DialoGPT-medium/resolve/main/config.json"
        )
        assert url == expected

    def test_hugging_face_remote_get_remote_artifact_content_type(self):
        """Test getting content type class for different file types."""
        remote = HuggingFaceRemote()

        # Test file download path - should return HuggingFaceContent
        content_class = remote.get_remote_artifact_content_type(
            "microsoft/DialoGPT-medium/resolve/main/config.json"
        )
        assert content_class == HuggingFaceContent

        # Test API endpoint - should return None (metadata only)
        content_class = remote.get_remote_artifact_content_type(
            "api/models/microsoft/DialoGPT-medium"
        )
        assert content_class is None

        # Test HTTP content type helper
        content_type = remote.get_http_content_type("config.json")
        assert content_type == "application/json"

        content_type = remote.get_http_content_type("pytorch_model.bin")
        assert content_type == "application/octet-stream"

    @patch("pulp_hugging_face.app.models.Artifact")
    def test_hugging_face_content_init_from_artifact_and_relative_path(self, mock_artifact):
        """Test initializing content from artifact and relative path."""
        mock_artifact.size = 1024

        # Test with resolve path
        relative_path = "models/microsoft/DialoGPT-medium/resolve/main/config.json"
        content = HuggingFaceContent.init_from_artifact_and_relative_path(
            mock_artifact, relative_path
        )

        assert content.repo_id == "microsoft/DialoGPT-medium"
        assert content.repo_type == "model"
        assert content.relative_path == "config.json"
        assert content.revision == "main"
        assert content.size == 1024


class TestHuggingFaceUtils:
    """Test utility functions."""

    def test_parse_hf_path_resolve(self):
        """Test parsing resolve paths."""
        path = "microsoft/DialoGPT-medium/resolve/main/config.json"
        result = parse_hf_path(path)

        assert result["repo_id"] == "microsoft/DialoGPT-medium"
        assert result["revision"] == "main"
        assert result["filename"] == "config.json"
        assert result["is_resolve"] is True
        assert result["is_api"] is False

    def test_parse_hf_path_api(self):
        """Test parsing API paths."""
        path = "api/models/microsoft/DialoGPT-medium"
        result = parse_hf_path(path)

        assert result["repo_id"] == "microsoft/DialoGPT-medium"
        assert result["repo_type"] == "model"
        assert result["is_api"] is True
        assert result["is_resolve"] is False

    def test_parse_hf_path_with_namespace(self):
        """Test parsing paths with organization namespace."""
        path = "microsoft/DialoGPT-medium/resolve/v1.0/config.json"
        result = parse_hf_path(path)

        assert result["repo_id"] == "microsoft/DialoGPT-medium"
        assert result["revision"] == "v1.0"
        assert result["filename"] == "config.json"

    def test_get_content_type_from_filename(self):
        """Test content type detection from filename."""
        assert get_content_type_from_filename("config.json") == "application/json"
        assert get_content_type_from_filename("README.md") == "text/markdown"
        assert get_content_type_from_filename("model.bin") == "application/octet-stream"
        assert get_content_type_from_filename("data.csv") == "text/csv"
        assert get_content_type_from_filename("unknown.xyz") == "application/octet-stream"


@pytest.mark.asyncio
class TestHuggingFaceHubClient:
    """Test Hugging Face Hub client functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock HTTP client for testing."""
        with patch("pulp_hugging_face.app.utils.httpx.AsyncClient") as mock:
            yield mock

    async def test_get_repo_info_success(self, mock_client):
        """Test successful repository info retrieval."""
        from pulp_hugging_face.app.utils import HuggingFaceHubClient

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "microsoft/DialoGPT-medium",
            "modelId": "microsoft/DialoGPT-medium",
            "author": "microsoft",
        }

        mock_client.return_value.get = AsyncMock(return_value=mock_response)

        client = HuggingFaceHubClient()
        result = await client.get_repo_info("microsoft/DialoGPT-medium")

        assert result["id"] == "microsoft/DialoGPT-medium"
        assert result["author"] == "microsoft"

    async def test_get_repo_info_not_found(self, mock_client):
        """Test repository info retrieval for non-existent repo."""
        from pulp_hugging_face.app.utils import HuggingFaceHubClient

        mock_response = Mock()
        mock_response.status_code = 404

        mock_client.return_value.get = AsyncMock(return_value=mock_response)

        client = HuggingFaceHubClient()
        result = await client.get_repo_info("nonexistent/repo")

        assert result is None
