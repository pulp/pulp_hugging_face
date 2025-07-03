"""
Content handler for Hugging Face Hub compatibility.

This handler provides HF Hub-compatible headers for all HF file patterns,
ensuring the Hugging Face CLI works seamlessly.
"""

import logging
import re
import hashlib
from pulpcore.responses import ArtifactResponse
from pulpcore.app.models import ContentArtifact

logger = logging.getLogger(__name__)


def huggingface_content_handler(relative_path):
    """
    Content handler function for HuggingFace distributions.

    For HF file requests (resolve and blob patterns), it tries to return an ArtifactResponse
    with the required Hugging Face headers. If no artifact is found, it falls back to
    default Pulp behavior.

    Args:
        relative_path (str): The path relative to the distribution base path

    Returns:
        ArtifactResponse with HF headers or None for default handling
    """

    logger.info(f"HF content handler checking path: {relative_path}")

    # Combined regex to match both HF resolve and blob patterns
    HF_FILE_PATTERN = re.compile(
        r"^(?P<repo_id>[^/]+/[^/]+)/(?P<endpoint>resolve|blob)/"
        r"(?P<revision>[^/]+)/(?P<filename>.+)$"
    )

    # Also try patterns with repo type prefixes (models/, datasets/, spaces/)
    HF_FILE_PATTERN_WITH_TYPE = re.compile(
        r"^(?P<repo_type>models|datasets|spaces)/(?P<repo_id>[^/]+/[^/]+)/"
        r"(?P<endpoint>resolve|blob)/(?P<revision>[^/]+)/(?P<filename>.+)$"
    )

    # Check if this matches HF file pattern
    file_match = HF_FILE_PATTERN.match(relative_path)
    if not file_match:
        # Try with repo type prefix
        file_match = HF_FILE_PATTERN_WITH_TYPE.match(relative_path)
        if not file_match:
            logger.info(f"No HF pattern match for: {relative_path}")
            return None

    # Extract components
    logger.info(f"Matched HF file pattern: {file_match.groups()}")

    # Extract components (some may not be used but are available for future use)
    repo_id = file_match.group("repo_id")
    revision = file_match.group("revision")
    filename = file_match.group("filename")

    if revision == "main":
        commit_hash = hashlib.sha1(f"{repo_id}-main-branch".encode()).hexdigest()
    elif len(revision) >= 7 and all(c in "0123456789abcdef" for c in revision.lower()):
        commit_hash = revision
    else:
        commit_hash = hashlib.sha1(f"{repo_id}-{revision}".encode()).hexdigest()

    etag = f'"{commit_hash[:8]}-{hash(filename) & 0xFFFFFF:06x}"'

    logger.info(f"Generated commit_hash: {commit_hash[:8]}..., etag: {etag}")

    # Try to find the corresponding ContentArtifact and Artifact
    try:

        content_artifacts = ContentArtifact.objects.filter(
            relative_path=relative_path
        ).select_related("artifact")

        if not content_artifacts.exists():
            # Try alternative path formats
            alt_paths = [
                f"{repo_id}/resolve/{revision}/{filename}",
                f"{repo_id}/blob/{revision}/{filename}",
                f"models/{repo_id}/resolve/{revision}/{filename}",
                f"models/{repo_id}/blob/{revision}/{filename}",
            ]
            alt_paths = [p for p in alt_paths if p != relative_path]

            for alt_path in alt_paths:
                content_artifacts = ContentArtifact.objects.filter(
                    relative_path=alt_path
                ).select_related("artifact")
                if content_artifacts.exists():
                    logger.info(f"Found artifact using alternative path: {alt_path}")
                    break

        if content_artifacts.exists():
            content_artifact = content_artifacts.first()
            artifact = content_artifact.artifact

            logger.info(f"Found artifact: size={artifact.size}")

            # Prepare Hugging Face headers
            headers = {
                "X-Repo-Commit": commit_hash,
                "X-Linked-ETag": etag,
                "ETag": etag,
                "Accept-Ranges": "bytes",
                "Content-Security-Policy": "default-src 'none'; sandbox",
                "Vary": "Origin, Accept",
                "Access-Control-Expose-Headers": (
                    "X-Repo-Commit,X-Request-Id,X-Error-Code,X-Error-Message,"
                    "X-Total-Count,ETag,Link,Accept-Ranges,Content-Range,"
                    "X-Linked-Size,X-Linked-ETag,X-Xet-Hash"
                ),
                "Content-Disposition": (
                    f"inline; filename*=UTF-8''{filename}; " f'filename="{filename}";'
                ),
            }

            # Add size-related headers
            if artifact.size:
                headers["Content-Length"] = str(artifact.size)
                headers["X-Linked-Size"] = str(artifact.size)

            logger.info("Returning ArtifactResponse with HF headers")

            # Return ArtifactResponse with custom headers
            return ArtifactResponse(artifact=artifact, headers=headers)
        else:
            logger.warning("No artifact found for HF pattern, but we need to provide headers")

    except Exception as e:
        logger.error(f"Error finding artifact: {e}")

    logger.warning("No ContentArtifact found - relying on content_headers_for and Pulp's streaming")

    return None
