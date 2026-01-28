# Welcome to Pulp Hugging Face!

The pulp_hugging_face plugin extends pulpcore to support hosting and caching Hugging Face Hub content.

If you just got here, you should take our [Getting Started with Hugging Face](site:pulp_hugging_face/docs/user/tutorials/getting_started/) tutorial to set up your first pull-through cache for Hugging Face content.
We also recommend that you read the [Basic Concepts](site:pulp_hugging_face/docs/user/learn/concepts/) section before diving into the workflows and reference material.

## Features

- **Pull-through caching**:
    * Automatically fetch and cache content from Hugging Face Hub on first access
    * Support for on-demand content fetching to reduce disk space
    * Cache models, datasets, and spaces from Hugging Face Hub
- **Authentication support**:
    * Use Hugging Face tokens for accessing private repositories
    * Seamless integration with HF Hub authentication
- **Full Hugging Face Hub compatibility**:
    * Support for all Hugging Face URL patterns
    * API proxying for metadata operations
    * Compatible with `huggingface-cli` and transformers library
- **Content Types**:
    * Models: PyTorch, TensorFlow, ONNX, and other model formats
    * Datasets: Training data, evaluation data, data descriptions
    * Spaces: Gradio apps, Streamlit apps, static sites
- **Versioned Repositories** so every operation is a restorable snapshot
- **De-duplication** of all saved content
- **Host content** either locally or on S3

