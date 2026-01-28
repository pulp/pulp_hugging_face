# Using with Hugging Face CLI

This guide explains how to use your Pulp Hugging Face cache with the official Hugging Face CLI
and Python libraries.

## Overview

The pulp_hugging_face plugin is designed to be compatible with Hugging Face tools. By setting
the `HF_ENDPOINT` environment variable, you can redirect all Hugging Face client requests
through your Pulp instance.

## Environment Setup

Set the `HF_ENDPOINT` environment variable to point to your Pulp distribution:

=== "Linux/macOS"

    ```bash
    export HF_ENDPOINT="http://your-pulp-instance/pulp/content/huggingface"
    ```

=== "Windows (PowerShell)"

    ```powershell
    $env:HF_ENDPOINT = "http://your-pulp-instance/pulp/content/huggingface"
    ```

=== "Windows (CMD)"

    ```cmd
    set HF_ENDPOINT=http://your-pulp-instance/pulp/content/huggingface
    ```

!!! tip "Persistent Configuration"
    Add the export command to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

## Using huggingface-cli

### Download Models

=== "Download Model"

    ```bash
    # Set endpoint
    export HF_ENDPOINT="http://your-pulp-instance/pulp/content/huggingface"
    
    # Download a model
    huggingface-cli download bert-base-uncased
    ```

=== "Download Specific Files"

    ```bash
    # Download only specific files
    huggingface-cli download bert-base-uncased config.json tokenizer.json
    ```

=== "Download to Specific Location"

    ```bash
    # Download to a specific directory
    huggingface-cli download bert-base-uncased --local-dir ./my-model
    ```

### Download Datasets

```bash
export HF_ENDPOINT="http://your-pulp-instance/pulp/content/huggingface"

# Download a dataset
huggingface-cli download --repo-type dataset squad
```

### Verify Cache Status

```bash
# Check what's in your local cache
huggingface-cli scan-cache
```

## Using with Transformers Library

### Loading Models

```python
import os

# Set the endpoint
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

from transformers import AutoModel, AutoTokenizer

# Load model - will use Pulp cache
model = AutoModel.from_pretrained("bert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
```

### Loading Pipelines

```python
import os
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

from transformers import pipeline

# Create a pipeline - model downloaded through Pulp
classifier = pipeline("sentiment-analysis")
result = classifier("I love using Pulp for model caching!")
```

## Using with Hugging Face Hub Library

```python
import os
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

from huggingface_hub import hf_hub_download, snapshot_download

# Download a single file
config_path = hf_hub_download(
    repo_id="bert-base-uncased",
    filename="config.json"
)

# Download entire repository
model_path = snapshot_download(repo_id="bert-base-uncased")
```

## Using with Datasets Library

```python
import os
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

from datasets import load_dataset

# Load a dataset - will use Pulp cache
dataset = load_dataset("squad")
```

## Using with Diffusers Library

```python
import os
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

from diffusers import DiffusionPipeline

# Load a diffusion model through Pulp
pipe = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
```

## Docker Configuration

When running containers, pass the environment variable:

=== "Docker Run"

    ```bash
    docker run -e HF_ENDPOINT="http://pulp-host/pulp/content/huggingface" my-ml-app
    ```

=== "Docker Compose"

    ```yaml
    version: '3.8'
    services:
      ml-app:
        image: my-ml-app
        environment:
          - HF_ENDPOINT=http://pulp-host/pulp/content/huggingface
    ```

=== "Kubernetes"

    ```yaml
    apiVersion: v1
    kind: Pod
    metadata:
      name: ml-app
    spec:
      containers:
      - name: ml-app
        image: my-ml-app
        env:
        - name: HF_ENDPOINT
          value: "http://pulp-service/pulp/content/huggingface"
    ```

## Offline Mode

Once models are cached in Pulp, you can use them even when the original Hugging Face Hub
is unavailable:

```python
import os

# Point to your Pulp instance
os.environ["HF_ENDPOINT"] = "http://your-pulp-instance/pulp/content/huggingface"

# Enable offline mode for transformers
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from transformers import AutoModel

# Will use locally cached content only
model = AutoModel.from_pretrained("bert-base-uncased")
```

!!! note
    Offline mode only works for content that has already been cached. If you request
    content that hasn't been cached yet, you'll get an error.

## Troubleshooting

### Connection Refused

If you get connection errors:

1. Verify Pulp is running and accessible
2. Check the distribution exists and has the correct base_path
3. Ensure there are no firewalls blocking the connection

```bash
# Test connectivity
curl -I http://your-pulp-instance/pulp/content/huggingface/api/models/bert-base-uncased
```

### SSL Certificate Errors

For self-signed certificates:

```python
import os

# Disable SSL verification (development only!)
os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"
os.environ["HF_ENDPOINT"] = "https://your-pulp-instance/pulp/content/huggingface"
```

!!! warning "Security"
    Disabling SSL verification is not recommended for production environments.

### Slow Downloads

If downloads are slow:

1. Check network connectivity between client and Pulp
2. Verify Pulp has adequate resources
3. Consider increasing `download_concurrency` on the remote

