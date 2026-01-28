# Getting Started with Pull-through Caching

This tutorial walks you through setting up a pull-through cache for Hugging Face Hub content.
By the end, you'll be able to download models through your Pulp instance with automatic caching.

## Prerequisites

- A running Pulp instance with the `pulp_hugging_face` plugin installed
- Access to the Pulp REST API (admin credentials or appropriate permissions)
- (Optional) A Hugging Face token for accessing private repositories

## Create a Hugging Face Remote

First, create a remote that points to Hugging Face Hub. The `on_demand` policy enables
pull-through caching - content will be fetched only when requested.

=== "Create Remote"

    ```bash
    # Create a remote with pull-through caching enabled
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
      "pulp_href": "/pulp/api/v3/remotes/hugging_face/hugging-face/a1b2c3d4-e5f6-7890-abcd-ef1234567890/",
      "pulp_created": "2024-01-15T10:30:00.000000Z",
      "name": "hf-remote",
      "url": "https://huggingface.co",
      "policy": "on_demand",
      "hf_token": null
    }
    ```

### Remote Configuration Options

- **name**: A unique identifier for this remote
- **url**: Base URL for Hugging Face Hub (default: `https://huggingface.co`)
- **policy**: Set to `on_demand` for pull-through caching
- **hf_token**: Optional authentication token for private repositories

## Create a Distribution

A distribution defines how content is served to clients. When configured with a remote,
it enables pull-through caching.

=== "Create Distribution"

    ```bash
    # Get the remote href from the previous step
    REMOTE_HREF="/pulp/api/v3/remotes/hugging_face/hugging-face/a1b2c3d4-e5f6-7890-abcd-ef1234567890/"

    # Create a distribution with the remote
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d "{
        \"name\": \"hf-cache\",
        \"base_path\": \"huggingface\",
        \"remote\": \"$REMOTE_HREF\"
      }"
    ```

=== "Output"

    ```json
    {
      "pulp_href": "/pulp/api/v3/distributions/hugging_face/hugging-face/f1e2d3c4-b5a6-7890-abcd-ef0987654321/",
      "pulp_created": "2024-01-15T10:35:00.000000Z",
      "name": "hf-cache",
      "base_path": "huggingface",
      "base_url": "https://your-pulp-instance.com/pulp/content/huggingface/",
      "remote": "/pulp/api/v3/remotes/hugging_face/hugging-face/a1b2c3d4-e5f6-7890-abcd-ef1234567890/"
    }
    ```

## Access Hugging Face Content

Now you can access Hugging Face content through your Pulp instance. The first request
will fetch from Hugging Face Hub; subsequent requests are served from cache.

### Download a Model File

=== "Download File"

    ```bash
    # Download a model configuration file
    curl -O http://your-pulp-instance/pulp/content/huggingface/microsoft/DialoGPT-medium/resolve/main/config.json
    ```

=== "Output"

    ```json
    {
      "architectures": ["GPT2LMHeadModel"],
      "bos_token_id": 50256,
      "eos_token_id": 50256,
      "model_type": "gpt2",
      "n_ctx": 1024,
      "n_embd": 1024,
      "n_head": 16,
      "n_layer": 24,
      "vocab_size": 50257
    }
    ```

### Query Model Metadata

=== "Get Model Info"

    ```bash
    # Get model metadata via the API proxy
    curl http://your-pulp-instance/pulp/content/huggingface/api/models/microsoft/DialoGPT-medium
    ```

=== "Output"

    ```json
    {
      "id": "microsoft/DialoGPT-medium",
      "modelId": "microsoft/DialoGPT-medium",
      "author": "microsoft",
      "sha": "8bada3b4...",
      "pipeline_tag": "text-generation",
      "tags": ["pytorch", "gpt2", "text-generation", "conversational"],
      "downloads": 500000,
      "library_name": "transformers"
    }
    ```

### List Repository Files

=== "List Files"

    ```bash
    # List files in a model repository
    curl http://your-pulp-instance/pulp/content/huggingface/api/models/bert-base-uncased/tree/main
    ```

=== "Output"

    ```json
    [
      {"path": "config.json", "type": "file", "size": 570},
      {"path": "pytorch_model.bin", "type": "file", "size": 440473133},
      {"path": "tokenizer.json", "type": "file", "size": 466062},
      {"path": "tokenizer_config.json", "type": "file", "size": 28},
      {"path": "vocab.txt", "type": "file", "size": 231508}
    ]
    ```

## Using with Hugging Face CLI

You can configure the `huggingface-cli` to use your Pulp instance as the endpoint:

```bash
# Set the HF endpoint to your Pulp distribution
export HF_ENDPOINT="http://your-pulp-instance/pulp/content/huggingface"

# Download a model using the HF CLI
huggingface-cli download hf-internal-testing/tiny-random-bert

# Or use it with the transformers library
python -c "
from transformers import AutoModel
model = AutoModel.from_pretrained('bert-base-uncased')
"
```

## Accessing Private Repositories

For private Hugging Face repositories, create a remote with your HF token:

=== "Create Authenticated Remote"

    ```bash
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "name": "hf-private",
        "url": "https://huggingface.co",
        "policy": "on_demand",
        "hf_token": "hf_YOUR_TOKEN_HERE"
      }'
    ```

!!! warning "Security Note"
    Store your Hugging Face tokens securely. Consider using environment variables
    or a secrets manager rather than hardcoding tokens in scripts.

## Next Steps

- Learn about [Core Concepts](site:pulp_hugging_face/docs/user/learn/concepts/) to understand the plugin architecture
- Explore [Configuration Options](site:pulp_hugging_face/docs/user/guides/configuration/) for advanced setup
- Set up [Authentication](site:pulp_hugging_face/docs/user/guides/authentication/) for private repositories

