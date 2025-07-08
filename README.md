# Pulp Hugging Face Plugin

A Pulp plugin for managing Hugging Face Hub content with pull-through caching support.

## Features

- **Pull-through caching**: Automatically fetch and cache content from Hugging Face Hub on first access
- **Support for all Hugging Face content types**: Models, datasets, and spaces
- **Authentication support**: Use Hugging Face tokens for private repositories
- **API proxying**: Forward API requests to Hugging Face Hub for metadata operations
- **File downloads**: Cache and serve model files, configuration files, and other artifacts

## Installation

```bash
pip install pulp-hugging-face
```

## Usage

### Setting up a Remote

First, create a Hugging Face remote that points to the Hugging Face Hub using the REST API:

```bash
# Using curl (REST API)
curl -X POST https://your-pulp-instance.com/api/pulp/public-domain-name/api/v3/remotes/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "name": "hf-remote",
    "url": "https://huggingface.co",
    "policy": "on_demand"
  }'
```

For private repositories, include your Hugging Face token:

```bash
# Using curl with authentication token
curl -X POST https://your-pulp-instance.com/api/pulp/public-domain-name/api/v3/remotes/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "name": "hf-private",
    "url": "https://huggingface.co",
    "policy": "on_demand",
    "hf_token": "YOUR_HF_TOKEN"
  }'
```

### Creating a Distribution with Pull-through Caching

Create a distribution that uses the remote for pull-through caching:

```bash
# First get the remote href
REMOTE_HREF=$(curl -s https://your-pulp-instance.com/api/pulp/public-domain-name/api/v3/remotes/hugging_face/hugging-face/ -u admin:password | jq -r '.results[] | select(.name=="hf-remote") | .pulp_href')

# Create distribution
curl -X POST https://your-pulp-instance.com/api/pulp/public-domain-name/api/v3/distributions/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d "{
    \"name\": \"hf-proxy\",
    \"base_path\": \"huggingface\",
    \"remote\": \"$REMOTE_HREF\"
  }"

https://cert.console.redhat.com/api/pulp-content/public-ytrahnov/huggingface/
```

> **Note**: CLI support (`pulp hugging-face` commands) is planned but not yet implemented. Currently, you need to use the REST API directly or create a simple script for automation.

### Accessing Content

Once configured, you can access Hugging Face content through your Pulp instance:

```bash
# Download a model file
curl http://your-pulp-instance/api/pulp-content/public-domain-name/huggingface/microsoft/DialoGPT-medium/resolve/main/config.json

# Access API endpoints
curl http://your-pulp-instance/api/pulp-content/public-domain-name/huggingface/api/models/microsoft/DialoGPT-medium

# List repository files
curl http://your-pulp-instance/api/pulp-content/public-domain-name/huggingface/models/microsoft/DialoGPT-medium/tree/main

#If you want to use it with the huggingface-cli
export HF_ENDPOINT="http://your-pulp-instance/api/pulp-content/public-domain-name/huggingface"
huggingface-cli download hf-internal-testing/tiny-random-bert
```

### How Pull-through Caching Works

1. **First request**: When content is requested but not available locally, Pulp fetches it from Hugging Face Hub
2. **Caching**: The content is stored locally and associated with the appropriate metadata
3. **Subsequent requests**: Future requests for the same content are served from the local cache
4. **API forwarding**: API requests are forwarded to Hugging Face Hub for real-time metadata

### Supported URL Patterns

The plugin supports the standard Hugging Face Hub URL patterns:

- **File downloads**: `/{repo_id}/resolve/{revision}/{filename}`
- **API endpoints**: `/api/models/{repo_id}`, `/api/datasets/{repo_id}`, `/api/spaces/{repo_id}`
- **Repository trees**: `/api/{repo_type}s/{repo_id}/tree/{revision}`
- **Git LFS**: `/api/{repo_type}s/{repo_id}/git/lfs/*`

### Configuration Options

#### Remote Configuration

- `hf_hub_url`: Base URL for Hugging Face Hub (default: https://huggingface.co)
- `hf_token`: Authentication token for private repositories
- `policy`: Set to `on_demand` to enable pull-through caching

#### Content Types

The plugin handles various Hugging Face content types:

- **Models**: PyTorch models, TensorFlow models, configuration files
- **Datasets**: Training data, evaluation data, data descriptions
- **Spaces**: Gradio apps, Streamlit apps, static sites

## Development

### Setting up Development Environment

```bash
git clone https://github.com/pulp/pulp_hugging_face.git
cd pulp_hugging_face
pip install -e .
```


### CLI Support (TODO)

CLI support for this plugin is planned but not yet implemented. The plugin currently supports:

- ✅ **REST API**: Full functionality via `/pulp/api/v3/`
- ❌ **CLI Commands**: `pulp hugging-face` commands not yet available

To add CLI support, the following would need to be implemented:
1. CLI command definitions in a `cli/` directory
2. Client library generation
3. Integration with `pulp-cli` package

For now, use the REST API directly or the provided example script for automation.

## How to File an Issue

File through this project's GitHub issues and appropriate labels.

> **WARNING** Is this security related? If so, please follow the [Security Disclosures](https://docs.pulpproject.org/pulpcore/bugs-features.html#security-bugs) procedure.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

## License

This project is licensed under the GNU General Public License v2.0 or later.
