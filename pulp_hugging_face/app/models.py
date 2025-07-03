"""
Check `Plugin Writer's Guide`_ for more details.

.. _Plugin Writer's Guide:
    https://pulpproject.org/pulpcore/docs/dev/
"""

from logging import getLogger

from django.db import models

from pulpcore.plugin.models import (
    Content,
    Remote,
    Repository,
    Publication,
    Distribution,
)
from pulpcore.plugin.util import get_domain_pk

logger = getLogger(__name__)


class HuggingFaceContent(Content):
    """
    The "hugging-face" content type.

    Represents content from Hugging Face Hub including models, datasets, and spaces.
    """

    TYPE = "hugging-face"

    # Repository information
    repo_id = models.CharField(
        max_length=255,
        help_text="The Hugging Face repository ID (e.g., 'microsoft/DialoGPT-medium')",
    )
    repo_type = models.CharField(
        max_length=20,
        choices=[("models", "Models"), ("datasets", "Datasets"), ("spaces", "Spaces")],
        default="models",
        help_text="The type of Hugging Face repository",
    )

    # File information
    relative_path = models.TextField(help_text="The relative path within the repository")
    revision = models.CharField(
        max_length=255, default="main", help_text="The git revision/branch/tag"
    )

    # File metadata
    size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    etag = models.CharField(
        max_length=255, null=True, blank=True, help_text="ETag from Hugging Face"
    )
    last_modified = models.DateTimeField(null=True, blank=True, help_text="Last modified timestamp")

    _pulp_domain = models.ForeignKey("core.Domain", default=get_domain_pk, on_delete=models.PROTECT)

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"
        unique_together = ("repo_id", "repo_type", "relative_path", "revision", "_pulp_domain")

    @classmethod
    def init_from_artifact_and_relative_path(cls, artifact, relative_path):
        """
        Initialize a HuggingFaceContent instance from an artifact and relative path.

        This method is called during pull-through caching to create content instances
        from downloaded artifacts.

        Args:
            artifact: The downloaded Artifact instance
            relative_path: The relative path of the content
        """
        # Parse the relative path to extract repository information
        # Expected formats:
        # - owner/repo/resolve/revision/filepath (most common)
        # - models/owner/repo/resolve/revision/filepath (explicit type)
        # - datasets/owner/repo/resolve/revision/filepath (explicit type)
        # - spaces/owner/repo/resolve/revision/filepath (explicit type)

        path_parts = relative_path.strip("/").split("/")

        # Check if first part is a repo type
        if len(path_parts) >= 1 and path_parts[0] in ("models", "datasets", "spaces"):
            # Format: models/owner/repo/resolve/revision/filepath
            if len(path_parts) < 5:
                raise ValueError(f"Invalid relative path format: {relative_path}")

            repo_type = path_parts[0]
            repo_id = f"{path_parts[1]}/{path_parts[2]}"

            # Skip 'resolve' or 'blob' part (convert blob to resolve for upstream)
            if path_parts[3] in ("resolve", "blob"):
                revision = path_parts[4] if len(path_parts) > 4 else "main"
            else:
                # Handle cases where 'resolve' might be missing
                revision = path_parts[3] if len(path_parts) > 4 else "main"
        else:
            # Format: owner/repo/resolve/revision/filepath (default to models)
            if len(path_parts) < 4:
                raise ValueError(f"Invalid relative path format: {relative_path}")

            repo_type = "models"  # default type
            repo_id = f"{path_parts[0]}/{path_parts[1]}"

            # Skip 'resolve' or 'blob' part (convert blob to resolve for upstream)
            if path_parts[2] in ("resolve", "blob"):
                revision = path_parts[3] if len(path_parts) > 3 else "main"
            else:
                # Handle cases where 'resolve' might be missing
                revision = path_parts[2] if len(path_parts) > 3 else "main"

        return cls(
            repo_id=repo_id,
            repo_type=repo_type,
            relative_path=relative_path,
            revision=revision,
            size=artifact.size if artifact else None,
            # Extract metadata from artifact if available
            last_modified=getattr(artifact, "last_modified", None) if artifact else None,
        )

    def __str__(self):
        return f"{self.repo_type}/{self.repo_id}:{self.revision}/{self.relative_path}"


class HuggingFacePublication(Publication):
    """
    A Publication for HuggingFaceContent.

    Define any additional fields for your new publication if needed.
    """

    TYPE = "hugging-face"

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"


class HuggingFaceRemote(Remote):
    """
    A Remote for HuggingFaceContent with pull-through caching support.
    """

    TYPE = "hugging-face"

    # Hugging Face Hub configuration
    hf_hub_url = models.URLField(
        default="https://huggingface.co", help_text="Base URL for Hugging Face Hub"
    )

    # Authentication token for private repositories
    hf_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Hugging Face authentication token for private repositories",
    )

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"

    def get_remote_artifact_url(self, relative_path=None, request=None):
        """
        Get the URL for downloading an artifact from Hugging Face Hub.

        This method is called during pull-through caching to determine
        where to download content from.

        Args:
            relative_path: The relative path being requested
            request: The HTTP request (optional)
        """
        # Handle case where path is None
        if not relative_path:
            return None

        # Ensure we have a clean base URL
        base_url = self.hf_hub_url.rstrip("/")

        # Clean up the relative path
        if relative_path.startswith("/"):
            relative_path = relative_path[1:]

        # Handle API endpoints differently than file downloads
        if relative_path.startswith("api/"):
            # API calls should go directly to Hugging Face
            return f"{base_url}/{relative_path}"
        else:
            # File downloads - ensure proper format for HF Hub
            # Convert: owner/repo/resolve/revision/file
            # To: owner/repo/resolve/revision/file (same format)
            return f"{base_url}/{relative_path}"

    def get_remote_artifact_content_type(self, relative_path=None):
        """
        Get the type of content that should be available at the relative path.

        For pull-through caching, this should return the Content class
        or None if the path is for metadata only.
        """
        if relative_path is None:
            return None

        # Handle API endpoints - these should be streamed but not cached as content
        if relative_path.startswith("api/"):
            return None  # Stream API responses but don't save as content

        # Check if this is a file download path
        if "resolve" in relative_path:
            return HuggingFaceContent

        # Default: assume it's downloadable content that should be cached
        return HuggingFaceContent

    def get_downloader(self, remote_artifact=None, url=None, download_factory=None, **kwargs):
        """
        Get a downloader configured with Hugging Face authentication and improved timeouts.
        """
        # Add Hugging Face specific headers
        if self.hf_token:
            extra_kwargs = kwargs.get("extra_data", {})
            headers = extra_kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self.hf_token}"
            headers["User-Agent"] = "Pulp-HuggingFace/1.0"
            extra_kwargs["headers"] = headers
            kwargs["extra_data"] = extra_kwargs

        # Increase timeouts for large file downloads
        kwargs.setdefault("connect_timeout", 30)  # 30 seconds to connect
        kwargs.setdefault("sock_read_timeout", 300)  # 5 minutes for reading
        kwargs.setdefault("total_timeout", 3600)  # 1 hour total timeout

        return super().get_downloader(
            remote_artifact=remote_artifact, url=url, download_factory=download_factory, **kwargs
        )


class HuggingFaceRepository(Repository):
    """
    A Repository for HuggingFaceContent.

    Define any additional fields for your new repository if needed.
    """

    TYPE = "hugging-face"

    CONTENT_TYPES = [HuggingFaceContent]

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"


class HuggingFaceDistribution(Distribution):
    """
    A Distribution for HuggingFaceContent with pull-through caching support.

    The base Distribution class already provides the 'remote' field needed
    for pull-through caching functionality.
    """

    TYPE = "hugging-face"

    @property
    def content_handler(self):
        """Return the custom handler for HF Hub-compatible redirects."""
        from .handler import huggingface_content_handler

        return huggingface_content_handler

    def content_headers_for(self, path):
        """
        Override content headers to inject Hugging Face Hub compatible headers.

        This method is called by Pulp's content handler to get headers for the response.
        We use it to inject the required HF headers that the CLI expects.

        Args:
            path (str): The path being requested

        Returns:
            dict: Dictionary with HTTP Response header/value pairs.
        """
        import re
        import hashlib
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"content_headers_for called for path: {path}")

        # Get the default headers from the parent class
        headers = super().content_headers_for(path)
        logger.info(f"Default headers: {headers}")

        # Check if this is an HF request that needs HF headers (both resolve and blob)
        HF_FILE_PATTERN = re.compile(
            r"^(?P<repo_id>[^/]+/[^/]+)/(?P<endpoint>resolve|blob)/"
            r"(?P<revision>[^/]+)/(?P<filename>.+)$"
        )

        # Also try patterns with repo type prefixes
        HF_FILE_PATTERN_WITH_TYPE = re.compile(
            r"^(?P<repo_type>models|datasets|spaces)/(?P<repo_id>[^/]+/[^/]+)/"
            r"(?P<endpoint>resolve|blob)/(?P<revision>[^/]+)/(?P<filename>.+)$"
        )

        file_match = HF_FILE_PATTERN.match(path)
        if not file_match:
            file_match = HF_FILE_PATTERN_WITH_TYPE.match(path)

        if file_match:
            logger.info(f"Found HF file pattern match: {file_match.groups()}")

            # Extract components
            repo_id = file_match.group("repo_id")
            endpoint = file_match.group("endpoint")  # 'resolve' or 'blob'
            revision = file_match.group("revision")
            filename = file_match.group("filename")

            # Create a realistic commit hash for the revision
            if revision == "main":
                commit_hash = hashlib.sha1(f"{repo_id}-main-branch".encode()).hexdigest()
            elif len(revision) >= 7 and all(c in "0123456789abcdef" for c in revision.lower()):
                commit_hash = revision
            else:
                commit_hash = hashlib.sha1(f"{repo_id}-{revision}".encode()).hexdigest()

            # Create simple, deterministic ETag
            etag = f'"{commit_hash[:8]}-{hash(filename) & 0xFFFFFF:06x}"'

            logger.info(f"Generated commit_hash: {commit_hash}")
            logger.info(f"Generated etag: {etag}")

            # Add/override Hugging Face headers
            headers["X-Repo-Commit"] = commit_hash
            headers["X-Linked-ETag"] = etag
            headers["ETag"] = etag  # Override Pulp's ETag with HF format
            headers["Accept-Ranges"] = "bytes"
            headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
            headers["Vary"] = "Origin, Accept"
            headers["Access-Control-Expose-Headers"] = (
                "X-Repo-Commit,X-Request-Id,X-Error-Code,X-Error-Message,"
                "X-Total-Count,ETag,Link,Accept-Ranges,Content-Range,"
                "X-Linked-Size,X-Linked-ETag,X-Xet-Hash"
            )
            headers["Content-Disposition"] = (
                f"inline; filename*=UTF-8''{filename}; " f'filename="{filename}";'
            )

            # Handle size headers - try to get the size from HuggingFace directly
            size_found = False

            # Try to get size from existing headers first
            if "X-PULP-ARTIFACT-SIZE" in headers:
                size = headers["X-PULP-ARTIFACT-SIZE"]
                headers["Content-Length"] = size
                headers["X-Linked-Size"] = size
                size_found = True
                logger.info(
                    f"Added Content-Length and X-Linked-Size from X-PULP-ARTIFACT-SIZE: {size}"
                )
            elif "Content-Length" in headers:
                size = headers["Content-Length"]
                headers["X-Linked-Size"] = size
                size_found = True
                logger.info(f"Added X-Linked-Size from existing Content-Length: {size}")

            # If no size found yet, try to get it from HuggingFace with a HEAD request
            if not size_found:
                try:
                    import requests

                    # Build the HuggingFace URL
                    hf_url = f"https://huggingface.co/{repo_id}/{endpoint}/{revision}/{filename}"
                    logger.info(f"Making HEAD request to HF to get size: {hf_url}")

                    # Make a quick HEAD request to get Content-Length
                    # Use a short timeout to avoid blocking the response
                    response = requests.head(hf_url, timeout=2, allow_redirects=True)

                    if response.status_code == 200:
                        content_length = response.headers.get("Content-Length")
                        if content_length:
                            headers["Content-Length"] = content_length
                            headers["X-Linked-Size"] = content_length
                            size_found = True
                            logger.info(f"Got size from HF HEAD request: {content_length}")
                        else:
                            logger.info("HF HEAD request successful but no Content-Length header")
                    else:
                        logger.warning(
                            f"HEAD failed: {response.status_code}"
                        )

                except Exception as e:
                    logger.warning(f"Could not get size from HF HEAD request: {e}")

            if not size_found:
                logger.info(
                    "No size information available - Pulp will set X-PULP-ARTIFACT-SIZE later"
                )

            logger.info(f"Added HF headers for {endpoint} request")
        else:
            logger.info(f"No HF pattern match for: {path}")

        logger.info(f"Final headers: {headers}")
        return headers

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"
