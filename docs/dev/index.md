# Welcome to Pulp Hugging Face for Developers!

Here you'll find information useful for the Hugging Face plugin developers.

If you just got here, consider exploring Pulpcore's [Developer Manual](site:pulpcore/docs/dev/), as it provides the common ground for developers for contributing to docs, to code and getting basic background on plugin development.

## Development Setup

### Prerequisites

- Python 3.9+
- A running Pulp development environment
- Git

### Clone and Install

```bash
git clone https://github.com/pulp/pulp_hugging_face.git
cd pulp_hugging_face
pip install -e .
```

### Running Tests

```bash
# Run unit tests
pytest pulp_hugging_face/tests/unit/

# Run functional tests (requires running Pulp)
pytest pulp_hugging_face/tests/functional/
```

## Architecture Overview

The pulp_hugging_face plugin implements a pull-through caching system for Hugging Face Hub content.

### Key Components

| Component | File | Description |
|-----------|------|-------------|
| **HuggingFaceContent** | `models.py` | Represents cached files from HF Hub |
| **HuggingFaceRemote** | `models.py` | Configuration for fetching from HF Hub |
| **HuggingFaceRepository** | `models.py` | Groups cached content |
| **HuggingFaceDistribution** | `models.py` | Serves content with pull-through caching |
| **Handler** | `handler.py` | Custom content handler for HF-compatible responses |

### Pull-through Caching Flow

1. Request arrives at the content handler
2. Handler checks if content exists locally
3. If not, fetches from Hugging Face Hub via the configured remote
4. Content is saved and streamed to the client
5. Future requests served from cache

### HF-Compatible Headers

The `HuggingFaceDistribution.content_headers_for()` method injects headers required by Hugging Face CLI tools:

- `X-Repo-Commit` - Git commit hash
- `X-Linked-ETag` - ETag for the content
- `Content-Disposition` - Filename header

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

See [CONTRIBUTING.md](https://github.com/pulp/pulp_hugging_face/blob/main/CONTRIBUTING.md) for detailed guidelines.

