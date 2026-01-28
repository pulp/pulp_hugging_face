# Configuration Options

This guide covers the configuration options available for pulp_hugging_face remotes and distributions.

## Remote Configuration

A `HuggingFaceRemote` defines how Pulp connects to Hugging Face Hub.

### Creating a Remote

=== "Basic Remote"

    ```bash
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "name": "hf-remote",
        "url": "https://huggingface.co",
        "policy": "on_demand"
      }'
    ```

=== "Output"

    ```json
    {
      "pulp_href": "/pulp/api/v3/remotes/hugging_face/hugging-face/...",
      "pulp_created": "2024-01-15T10:30:00.000000Z",
      "name": "hf-remote",
      "url": "https://huggingface.co",
      "policy": "on_demand",
      "hf_hub_url": "https://huggingface.co",
      "hf_token": null
    }
    ```

### Remote Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | yes | - | Unique identifier for the remote |
| `url` | string | yes | - | Base URL (typically `https://huggingface.co`) |
| `policy` | string | no | `on_demand` | Download policy: `immediate`, `on_demand`, or `streamed` |
| `hf_hub_url` | string | no | `https://huggingface.co` | Hugging Face Hub base URL |
| `hf_token` | string | no | null | Authentication token for private repos |

### Download Policies

- **`on_demand`** (default): Content is fetched only when requested by clients. This enables pull-through caching and minimizes storage usage.

- **`immediate`**: All content is downloaded during sync operations. Not typically used for Hugging Face content due to the large size of repositories.

- **`streamed`**: Content is streamed through but not saved locally.

### Updating a Remote

=== "Update Remote"

    ```bash
    REMOTE_HREF="/pulp/api/v3/remotes/hugging_face/hugging-face/a1b2c3d4.../"
    
    curl -X PATCH https://your-pulp-instance.com${REMOTE_HREF} \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "hf_token": "hf_new_token_here"
      }'
    ```

## Distribution Configuration

A `HuggingFaceDistribution` defines how content is served to clients.

### Creating a Distribution

=== "With Remote (Pull-through)"

    ```bash
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "name": "hf-cache",
        "base_path": "huggingface",
        "remote": "/pulp/api/v3/remotes/hugging_face/hugging-face/..."
      }'
    ```

=== "With Publication"

    ```bash
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "name": "hf-published",
        "base_path": "huggingface-pub",
        "publication": "/pulp/api/v3/publications/hugging_face/hugging-face/..."
      }'
    ```

### Distribution Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | yes | - | Unique identifier for the distribution |
| `base_path` | string | yes | - | URL path where content is served |
| `remote` | string | no | null | Remote href for pull-through caching |
| `publication` | string | no | null | Publication href for serving published content |

!!! note
    For pull-through caching, set the `remote` field. For serving published content, set the `publication` field.

### Content URL Structure

Once a distribution is created, content is accessible at:

```
https://your-pulp-instance.com/pulp/content/{base_path}/{huggingface_path}
```

Examples:

- Model file: `/pulp/content/huggingface/microsoft/DialoGPT-medium/resolve/main/config.json`
- API endpoint: `/pulp/content/huggingface/api/models/microsoft/DialoGPT-medium`

## Listing Resources

### List All Remotes

```bash
curl https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
  -u admin:password
```

### List All Distributions

```bash
curl https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
  -u admin:password
```

## Deleting Resources

### Delete a Remote

```bash
REMOTE_HREF="/pulp/api/v3/remotes/hugging_face/hugging-face/..."
curl -X DELETE https://your-pulp-instance.com${REMOTE_HREF} \
  -u admin:password
```

### Delete a Distribution

```bash
DIST_HREF="/pulp/api/v3/distributions/hugging_face/hugging-face/..."
curl -X DELETE https://your-pulp-instance.com${DIST_HREF} \
  -u admin:password
```

