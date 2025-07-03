"""
URL patterns for Hugging Face plugin.

These patterns handle HF Hub-compatible redirects to ensure
the Hugging Face CLI works seamlessly with Pulp's pull-through caching.
"""

from django.urls import re_path
from . import views

# Content URL patterns that match HF Hub patterns
content_urlpatterns = [
    # Handle file downloads with HF Hub-compatible redirects
    # Pattern: /pulp/content/{base_path}/{repo_id}/resolve/{revision}/{filename}
    re_path(
        r"^(?P<base_path>[^/]+)/(?P<repo_id>[^/]+/[^/]+)/resolve/"
        r"(?P<revision>[^/]+)/(?P<filename>.+)$",
        views.file_download_redirect,
        name="file_download_redirect",
    ),
    # Handle API requests (forward to upstream)
    # Pattern: /pulp/content/{base_path}/api/{path}
    re_path(r"^[^/]+/api/(?P<path>.*)$", views.api_proxy_view, name="api_proxy"),
]

# API URL patterns for resolve-cache endpoints
api_urlpatterns = [
    # Handle resolve-cache API calls
    # Pattern:
    # /pulp/api/v3/content/huggingface/resolve-cache/models/{repo_id}/{revision}/{filename}/
    re_path(
        r"^content/huggingface/resolve-cache/models/"
        r"(?P<repo_id>[^/]+/[^/]+)/(?P<revision>[^/]+)/(?P<filename>.+)/$",
        views.resolve_cache_file,
        name="resolve_cache_file",
    ),
]

# Only register API patterns - content patterns are handled by the content app
urlpatterns = api_urlpatterns
