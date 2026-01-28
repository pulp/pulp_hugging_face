# Content Access Patterns

This guide covers the various ways to access Hugging Face content through your Pulp instance.

## URL Structure

Content served by pulp_hugging_face follows this structure:

```
https://{pulp-host}/pulp/content/{base_path}/{huggingface_path}
```

Where:
- `{pulp-host}` is your Pulp server hostname
- `{base_path}` is the distribution's base_path
- `{huggingface_path}` is the standard Hugging Face URL path

## File Downloads

### Direct File Access

Download specific files using the resolve endpoint:

=== "Download File"

    ```bash
    # Pattern: /{repo_id}/resolve/{revision}/{filename}
    
    # Download model config
    curl -O http://your-pulp/pulp/content/hf/bert-base-uncased/resolve/main/config.json
    
    # Download model weights
    curl -O http://your-pulp/pulp/content/hf/bert-base-uncased/resolve/main/pytorch_model.bin
    
    # Download from specific revision
    curl -O http://your-pulp/pulp/content/hf/bert-base-uncased/resolve/v1.0/config.json
    ```

=== "Response Headers"

    ```http
    HTTP/1.1 200 OK
    Content-Type: application/octet-stream
    Content-Length: 570
    Content-Disposition: attachment; filename="config.json"
    X-Repo-Commit: a265f773a47193eed794233aa2a0f0bb6d3eaa63
    X-Linked-ETag: "a265f773a47193eed794233aa2a0f0bb6d3eaa63"
    ETag: "a265f773a47193eed794233aa2a0f0bb6d3eaa63"
    ```

### Nested File Paths

Access files in subdirectories:

```bash
# Download nested file
curl -O http://your-pulp/pulp/content/hf/org/model/resolve/main/subdir/file.txt
```

## API Endpoints

### Model Information

=== "Get Model Info"

    ```bash
    # Get model metadata
    curl http://your-pulp/pulp/content/hf/api/models/bert-base-uncased
    ```

=== "Response"

    ```json
    {
      "id": "bert-base-uncased",
      "modelId": "bert-base-uncased",
      "author": "google-bert",
      "sha": "a265f773...",
      "pipeline_tag": "fill-mask",
      "tags": ["pytorch", "tf", "bert", "fill-mask"],
      "downloads": 50000000,
      "library_name": "transformers"
    }
    ```

### Dataset Information

```bash
# Get dataset metadata
curl http://your-pulp/pulp/content/hf/api/datasets/squad
```

### Space Information

```bash
# Get space metadata
curl http://your-pulp/pulp/content/hf/api/spaces/gradio/hello_world
```

## Repository Tree Listing

List files in a repository at a specific revision:

=== "List Files"

    ```bash
    # List model files
    curl http://your-pulp/pulp/content/hf/api/models/bert-base-uncased/tree/main
    
    # List dataset files
    curl http://your-pulp/pulp/content/hf/api/datasets/squad/tree/main
    ```

=== "Response"

    ```json
    [
      {
        "type": "file",
        "path": "config.json",
        "size": 570
      },
      {
        "type": "file",
        "path": "pytorch_model.bin",
        "size": 440473133
      },
      {
        "type": "file",
        "path": "tokenizer.json",
        "size": 466062
      },
      {
        "type": "directory",
        "path": "onnx"
      }
    ]
    ```

### List Subdirectories

```bash
# List files in a subdirectory
curl http://your-pulp/pulp/content/hf/api/models/bert-base-uncased/tree/main/onnx
```

## LFS Content

Large files (using Git LFS) are handled automatically:

```bash
# Download LFS file - Pulp handles the LFS resolution
curl -O http://your-pulp/pulp/content/hf/bert-base-uncased/resolve/main/pytorch_model.bin
```

!!! note
    LFS files are fetched transparently. The initial request may take longer as Pulp
    retrieves the actual file content from Hugging Face's LFS storage.

## Revision Handling

### Using Branches

```bash
# Main branch (default)
curl http://your-pulp/pulp/content/hf/model/resolve/main/config.json

# Development branch
curl http://your-pulp/pulp/content/hf/model/resolve/dev/config.json
```

### Using Tags

```bash
# Specific version tag
curl http://your-pulp/pulp/content/hf/model/resolve/v1.0.0/config.json
```

### Using Commit SHA

```bash
# Specific commit
curl http://your-pulp/pulp/content/hf/model/resolve/a265f773a47193eed794233aa2a0f0bb6d3eaa63/config.json
```

## Content Types Supported

### Models

| Content | Example Path |
|---------|--------------|
| Config | `/model/resolve/main/config.json` |
| PyTorch Weights | `/model/resolve/main/pytorch_model.bin` |
| TensorFlow Weights | `/model/resolve/main/tf_model.h5` |
| Safetensors | `/model/resolve/main/model.safetensors` |
| Tokenizer | `/model/resolve/main/tokenizer.json` |
| ONNX | `/model/resolve/main/model.onnx` |

### Datasets

| Content | Example Path |
|---------|--------------|
| Data Files | `/dataset/resolve/main/data/train.parquet` |
| README | `/dataset/resolve/main/README.md` |
| Dataset Script | `/dataset/resolve/main/dataset.py` |

### Spaces

| Content | Example Path |
|---------|--------------|
| App Code | `/space/resolve/main/app.py` |
| Requirements | `/space/resolve/main/requirements.txt` |
| Static Files | `/space/resolve/main/static/style.css` |

## Caching Behavior

### First Request

1. Client requests content
2. Pulp checks local cache (miss)
3. Pulp fetches from Hugging Face Hub
4. Content is cached locally
5. Response sent to client

### Subsequent Requests

1. Client requests content
2. Pulp checks local cache (hit)
3. Response sent directly from cache

### Cache Headers

Responses include caching headers:

```http
ETag: "a265f773a47193eed794233aa2a0f0bb6d3eaa63"
X-Repo-Commit: a265f773a47193eed794233aa2a0f0bb6d3eaa63
```

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Content returned |
| 404 | Not Found | Check repository/file exists |
| 401 | Unauthorized | Verify HF token on remote |
| 403 | Forbidden | Check token permissions |
| 500 | Server Error | Check Pulp logs |

### Example Error Response

```json
{
  "error": "Repository not found",
  "detail": "The requested repository 'nonexistent/model' does not exist on Hugging Face Hub"
}
```

