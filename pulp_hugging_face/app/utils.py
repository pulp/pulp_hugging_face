"""
Utilities for interacting with Hugging Face Hub API.
"""

import httpx
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class HuggingFaceHubClient:
    """
    Client for interacting with Hugging Face Hub API.
    """

    def __init__(self, base_url: str = "https://huggingface.co", token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_base = f"{self.base_url}/api"
        self.token = token
        self.client = httpx.AsyncClient(timeout=30.0)

    def get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {"User-Agent": "Pulp-HuggingFace/1.0"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_repo_info(
        self, repo_id: str, repo_type: str = "models"
    ) -> Optional[Dict[str, Any]]:
        """
        Get repository information from Hugging Face Hub.

        Args:
            repo_id: Repository ID (e.g., 'microsoft/DialoGPT-medium')
            repo_type: Type of repository ('models', 'datasets', 'spaces')

        Returns:
            Repository information or None if not found
        """
        url = f"{self.api_base}/{repo_type}s/{repo_id}"

        try:
            response = await self.client.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get repo info for {repo_id}: {response.status_code}")
                return None
        except httpx.RequestError as e:
            logger.error(f"Error fetching repo info for {repo_id}: {e}")
            return None

    async def get_repo_tree(
        self, repo_id: str, revision: str = "main", repo_type: str = "models"
    ) -> List[Dict[str, Any]]:
        """
        Get file tree for a repository.

        Args:
            repo_id: Repository ID
            revision: Git revision/branch/tag
            repo_type: Type of repository

        Returns:
            List of file information
        """
        url = f"{self.api_base}/{repo_type}s/{repo_id}/tree/{revision}"

        try:
            response = await self.client.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get repo tree for {repo_id}: {response.status_code}")
                return []
        except httpx.RequestError as e:
            logger.error(f"Error fetching repo tree for {repo_id}: {e}")
            return []

    async def download_file(
        self, repo_id: str, filename: str, revision: str = "main", repo_type: str = "models"
    ) -> Optional[bytes]:
        """
        Download a file from a repository.

        Args:
            repo_id: Repository ID
            filename: Path to file within repository
            revision: Git revision/branch/tag
            repo_type: Type of repository

        Returns:
            File content as bytes or None if failed
        """
        url = f"{self.base_url}/{repo_id}/resolve/{revision}/{filename}"

        try:
            response = await self.client.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(
                    f"Failed to download {filename} from {repo_id}: {
                        response.status_code}"
                )
                return None
        except httpx.RequestError as e:
            logger.error(f"Error downloading {filename} from {repo_id}: {e}")
            return None

    async def stream_file(
        self, repo_id: str, filename: str, revision: str = "main", repo_type: str = "models"
    ):
        """
        Stream a file from a repository.

        Args:
            repo_id: Repository ID
            filename: Path to file within repository
            revision: Git revision/branch/tag
            repo_type: Type of repository

        Returns:
            httpx.Response object for streaming
        """
        url = f"{self.base_url}/{repo_id}/resolve/{revision}/{filename}"

        try:
            response = await self.client.get(url, headers=self.get_headers())
            return response
        except httpx.RequestError as e:
            logger.error(f"Error streaming {filename} from {repo_id}: {e}")
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


def parse_hf_path(path: str) -> Dict[str, str]:
    """
    Parse a Hugging Face path to extract components.

    Args:
        path: Path like 'models/microsoft/DialoGPT-medium/resolve/main/config.json'

    Returns:
        Dictionary with parsed components
    """
    path = path.strip("/")
    parts = path.split("/")

    result = {
        "repo_type": "models",
        "repo_id": "",
        "revision": "main",
        "filename": "",
        "is_api": False,
        "is_resolve": False,
    }

    if not parts:
        return result

    # Check if it's an API endpoint
    if parts[0] == "api":
        result["is_api"] = True
        if len(parts) > 1:
            # api/models/repo_id or api/datasets/repo_id
            if parts[1] in ["models", "datasets", "spaces"]:
                result["repo_type"] = parts[1].rstrip("s")  # Remove 's' suffix
                if len(parts) > 2:
                    result["repo_id"] = "/".join(parts[2:])
        return result

    # Check for resolve path: repo_id/resolve/revision/filename
    if "resolve" in parts:
        try:
            resolve_index = parts.index("resolve")
            result["is_resolve"] = True
            result["repo_id"] = "/".join(parts[:resolve_index])
            if resolve_index + 1 < len(parts):
                result["revision"] = parts[resolve_index + 1]
            if resolve_index + 2 < len(parts):
                result["filename"] = "/".join(parts[resolve_index + 2 :])
        except ValueError:
            pass

    # Try to infer repo type from path structure
    if parts[0] in ["models", "datasets", "spaces"]:
        result["repo_type"] = parts[0]
        if len(parts) > 1:
            result["repo_id"] = "/".join(parts[1:])
    else:
        # Assume it's a model repository
        result["repo_id"] = "/".join(parts)

    return result


def get_content_type_from_filename(filename: str) -> str:
    """
    Get MIME type based on file extension.

    Args:
        filename: Name of the file

    Returns:
        MIME type string
    """
    import os

    file_ext = os.path.splitext(filename.lower())[1]

    content_type_map = {
        ".json": "application/json",
        ".jsonl": "application/jsonlines",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".py": "text/x-python",
        ".yaml": "application/x-yaml",
        ".yml": "application/x-yaml",
        ".bin": "application/octet-stream",
        ".safetensors": "application/octet-stream",
        ".h5": "application/octet-stream",
        ".pkl": "application/octet-stream",
        ".parquet": "application/octet-stream",
        ".arrow": "application/octet-stream",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".zip": "application/zip",
        ".tar": "application/x-tar",
        ".gz": "application/gzip",
        ".gitattributes": "text/plain",
        ".gitignore": "text/plain",
    }

    return content_type_map.get(file_ext, "application/octet-stream")
