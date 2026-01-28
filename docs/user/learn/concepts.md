# Core Hugging Face Concepts

## Content

`HuggingFaceContent` represents any file cached from Hugging Face Hub. This includes model weights,
configuration files, tokenizer files, dataset files, and any other artifacts stored on the Hub.

Each content unit is uniquely identified by:

- **repo_id**: The full path to the repository (e.g., `microsoft/DialoGPT-medium`)
- **repo_type**: The type of repository (`models`, `datasets`, or `spaces`)
- **relative_path**: The file path within the repository
- **revision**: The git reference (branch, tag, or commit SHA)

Additional metadata stored:

- **size**: File size in bytes
- **etag**: ETag from Hugging Face Hub
- **last_modified**: Last modified timestamp

## Remote

A `HuggingFaceRemote` defines the connection to Hugging Face Hub for fetching content.

Key configuration options:

- **url**: Base URL for Hugging Face Hub (typically `https://huggingface.co`)
- **hf_hub_url**: Alternative Hugging Face Hub URL
- **hf_token**: Authentication token for accessing private repositories
- **policy**: Download policy - `on_demand` for pull-through caching (default)

!!! note
    The `on_demand` policy is essential for pull-through caching. It means content is only
    downloaded when first requested by a client, rather than being synced upfront.

## Repository

A `HuggingFaceRepository` is a versioned collection of cached Hugging Face content.
Each time content is added or removed, a new immutable repository version is created.

Repositories in pulp_hugging_face are primarily used to track what content has been cached
through pull-through operations.

## Distribution

A `HuggingFaceDistribution` serves content to clients and handles pull-through caching.
When configured with a remote, it will automatically fetch and cache content that isn't
already available locally.

Key features:

- **Pull-through caching**: Fetches content from Hugging Face Hub on first request
- **Content serving**: Serves cached content directly from Pulp's content app
- **Header injection**: Adds Hugging Face-compatible headers for client compatibility

The distribution's `content_headers_for()` method injects headers required by Hugging Face CLI tools:

- `X-Repo-Commit`: Git commit hash for the revision
- `X-Linked-ETag`: ETag for cache validation
- `Content-Disposition`: Proper filename headers

## Pull-through Caching

Pull-through caching is the primary workflow for pulp_hugging_face:

1. **Client Request**: A client requests content through the Pulp distribution
2. **Cache Check**: Pulp checks if the content is already cached
3. **Fetch if Missing**: If not cached, Pulp fetches from Hugging Face Hub
4. **Cache & Serve**: Content is cached locally and served to the client
5. **Future Requests**: Subsequent requests are served directly from cache

## URL Patterns

The plugin supports standard Hugging Face Hub URL patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| `/{repo_id}/resolve/{revision}/{filename}` | Download specific file | `/microsoft/DialoGPT-medium/resolve/main/config.json` |
| `/api/models/{repo_id}` | Model metadata API | `/api/models/microsoft/DialoGPT-medium` |
| `/api/datasets/{repo_id}` | Dataset metadata API | `/api/datasets/squad` |
| `/api/spaces/{repo_id}` | Space metadata API | `/api/spaces/gradio/hello_world` |
| `/api/{type}s/{repo_id}/tree/{revision}` | List repository files | `/api/models/bert-base-uncased/tree/main` |

## Repository Types

### Models

Machine learning models in various formats:

- **PyTorch models**: `.bin`, `.pt`, `.pth` files
- **TensorFlow models**: `.h5`, SavedModel directories
- **ONNX models**: `.onnx` files
- **Safetensors**: `.safetensors` files
- **Configuration**: `config.json`, `tokenizer.json`, etc.

### Datasets

Training and evaluation data:

- **Data files**: Parquet, JSON, CSV, Arrow formats
- **Dataset cards**: README.md with metadata
- **Data scripts**: Python scripts for dataset loading

### Spaces

Interactive applications:

- **Gradio apps**: Python-based ML demos
- **Streamlit apps**: Data applications
- **Static sites**: HTML/CSS/JS applications

