# Project Overview

**Pulp Hugging Face Plugin** - A Pulp plugin for managing Hugging Face Hub content with pull-through caching support.

## Key Features
- Pull-through caching for Hugging Face content (models, datasets, spaces)
- Authentication support via HF tokens for private repositories
- API proxying to forward requests to Hugging Face Hub
- File download caching and serving

## Technology Stack
- **Framework**: Django-based Pulp plugin
- **Python**: 3.9-3.12
- **Core Dependencies**: pulpcore (3.100.0-3.115), httpx
- **Version**: 0.4.0.dev

## Project Structure

```
pulp_hugging_face/
├── app/
│   ├── models.py         - Core models (Content, Remote, Repository, Distribution)
│   ├── viewsets.py       - REST API viewsets
│   ├── serializers.py    - API serializers
│   ├── handler.py        - Custom content handler
│   ├── tasks/            - Async tasks (sync, publish)
│   └── migrations/       - Database migrations
└── tests/                - Test suite structure (functional, unit, performance)
```

## Main Components

1. **HuggingFaceContent** - Represents cached files from HF Hub
2. **HuggingFaceRemote** - Configuration for fetching from HF Hub
3. **HuggingFaceDistribution** - Serves content with pull-through caching
4. **HuggingFaceRepository** - Groups cached content

## Current Status
- REST API fully functional
- Pull-through caching implemented
- CLI support planned but not yet implemented
- Active development (version 0.4.0.dev)

## Workflow
1. Create a remote pointing to huggingface.co
2. Create a distribution with the remote for pull-through caching
3. Access HF content through Pulp (automatically cached on first request)
4. Subsequent requests served from cache

## Implementation Details

The plugin uses custom handlers to inject HF-compatible headers and manage the caching lifecycle. The `HuggingFaceDistribution` model includes a custom `content_headers_for()` method that adds Hugging Face Hub compatible headers like `X-Repo-Commit`, `X-Linked-ETag`, and proper `Content-Disposition` headers to ensure compatibility with HF CLI tools.
