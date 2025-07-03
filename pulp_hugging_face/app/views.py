"""
Views for Hugging Face Hub compatibility.

These views handle file downloads with HF Hub-compatible redirect patterns
to ensure the Hugging Face CLI works seamlessly with Pulp's pull-through caching.
"""

import logging
import httpx
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import HuggingFaceDistribution

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def file_download_redirect(request, base_path, repo_id, revision, filename):
    """
    Handle file download requests with HF Hub-compatible redirects.

    This view mimics HuggingFace Hub's behavior by returning 307 redirects
    to resolve-cache endpoints instead of serving files directly.

    Simplified approach to avoid race conditions - always redirect with
    basic ETag derived from revision and filename.
    """

    logger.info(f"HF file download request: {base_path}/{repo_id}/{revision}/{filename}")

    try:
        # Find the distribution (just to validate it exists)
        distribution = get_object_or_404(HuggingFaceDistribution, base_path=base_path)

        if not distribution.remote:
            raise Http404("No remote configured for this distribution")

        # Create simple, deterministic ETag - no race conditions
        etag = f'"{revision[:8]}-{hash(filename) & 0xFFFFFF:06x}"'

        # Create redirect URL to resolve-cache API
        resolve_cache_url = (
            f"/pulp/api/v3/content/huggingface/resolve-cache/models/"
            f"{repo_id}/{revision}/{filename}/"
        )

        logger.info(f"Redirecting to: {resolve_cache_url}")
        logger.info(f"X-Repo-Commit: {revision}")
        logger.info(f"X-Linked-ETag: {etag}")

        # Create 307 redirect response with HF Hub compatible headers
        response = HttpResponse(
            content=f"Redirecting to cached file: {resolve_cache_url}",
            status=307,
            content_type="text/plain; charset=utf-8",
        )

        # Add required HF Hub headers
        response["Location"] = resolve_cache_url
        response["X-Repo-Commit"] = revision
        response["X-Linked-ETag"] = etag
        response["Accept-Ranges"] = "bytes"
        response["Content-Disposition"] = (
            f"inline; filename*=UTF-8''{filename}; filename=\"{filename}\";"
        )
        response["Content-Security-Policy"] = "default-src 'none'; sandbox"
        response["Vary"] = "Origin, Accept"
        response["Access-Control-Expose-Headers"] = (
            "X-Repo-Commit,X-Request-Id,X-Error-Code,X-Error-Message,"
            "X-Total-Count,ETag,Link,Accept-Ranges,Content-Range,"
            "X-Linked-Size,X-Linked-ETag,X-Xet-Hash"
        )

        return response

    except Exception as e:
        logger.error(f"Error in file download redirect: {e}")
        raise Http404(f"File not found: {e}")


@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def resolve_cache_file(request, repo_id, revision, filename):
    """
    Handle resolve-cache API calls - serve actual file content.

    This endpoint is where the redirects point to and serves the actual
    file content using Pulp's pull-through caching.

    Simplified approach: always redirect to Pulp content handler with proper headers.
    """

    logger.info(f"Resolve-cache request: {repo_id}/{revision}/{filename}")

    try:
        # Find a distribution that can serve this content
        # Look for the distribution with a remote (should be huggingface-1751051062)
        distributions = HuggingFaceDistribution.objects.filter(remote__isnull=False)

        if not distributions.exists():
            logger.error("No HuggingFace distribution with remote found")
            return HttpResponse("No HuggingFace distribution with remote configured", status=502)

        distribution = distributions.first()
        relative_path = f"{repo_id}/resolve/{revision}/{filename}"

        # Build the standard Pulp content URL and redirect to it
        # This will trigger Pulp's pull-through caching mechanism
        pulp_content_url = f"/pulp/content/{distribution.base_path}/{relative_path}"

        logger.info(f"Using distribution: {distribution.name} ({distribution.base_path})")
        logger.info(f"Redirecting to Pulp content: {pulp_content_url}")

        # Redirect to Pulp's content handler with required headers
        response = HttpResponse(status=307)
        response["Location"] = pulp_content_url
        response["X-Repo-Commit"] = revision
        response["Accept-Ranges"] = "bytes"

        return response

    except Exception as e:
        logger.error(f"Error in resolve-cache: {e}")
        return HttpResponse(f"Error: {str(e)}", status=500)


@csrf_exempt
@require_http_methods(["GET", "HEAD", "POST"])
def api_proxy_view(request, path):
    """
    Proxy API requests to upstream Hugging Face Hub.

    API requests should not be cached and should return live metadata.
    This ensures the HF CLI gets fresh repository information.
    """
    try:
        # Find the distribution for this request
        # We need to extract the base_path from the request path
        full_path = request.path

        # Find matching distribution
        distribution = None
        for dist in HuggingFaceDistribution.objects.filter(remote__isnull=False):
            if full_path.startswith(f"/pulp/content/{dist.base_path}/"):
                distribution = dist
                break

        if not distribution or not distribution.remote:
            return HttpResponse("No remote configured", status=502)

        # Get the upstream URL
        upstream_url = distribution.remote.get_remote_artifact_url(
            relative_path=f"api/{path}", request=request
        )

        if not upstream_url:
            return HttpResponse("Cannot resolve upstream URL", status=502)

        # Forward the request to upstream
        with httpx.Client(timeout=30.0) as client:
            # Prepare headers (remove hop-by-hop headers)
            headers = {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["host", "content-length", "connection"]
            }

            # Add authentication if available
            if hasattr(distribution.remote, "hf_token") and distribution.remote.hf_token:
                headers["Authorization"] = f"Bearer {distribution.remote.hf_token}"

            # Forward the request
            if request.method == "GET":
                response = client.get(upstream_url, headers=headers, params=request.GET)
            elif request.method == "HEAD":
                response = client.head(upstream_url, headers=headers, params=request.GET)
            elif request.method == "POST":
                body = request.body
                response = client.post(upstream_url, headers=headers, content=body)

            # Create Django response
            django_response = HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get("content-type", "application/json"),
            )

            # Forward important headers
            for key, value in response.headers.items():
                if key.lower() not in ["content-encoding", "transfer-encoding", "connection"]:
                    django_response[key] = value

            return django_response

    except Exception as e:
        logger.error(f"Error proxying API request {path}: {e}")
        return HttpResponse(f"Proxy error: {str(e)}", status=500)


def _get_content_type(filename):
    """Get appropriate content type for filename."""
    if filename.endswith(".json"):
        return "application/json"
    elif filename.endswith(".bin"):
        return "application/octet-stream"
    elif filename.endswith(".txt"):
        return "text/plain"
    elif filename.endswith(".md"):
        return "text/markdown"
    elif filename.endswith(".py"):
        return "text/x-python"
    elif filename.endswith(".yml") or filename.endswith(".yaml"):
        return "application/x-yaml"
    else:
        return "application/octet-stream"
