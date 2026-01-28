# Welcome to Pulp Hugging Face

The `pulp_hugging_face` plugin extends pulpcore to support hosting and caching Hugging Face Hub content.
This plugin is a part of the Pulp Project, and assumes some familiarity with the
[pulpcore documentation](site:pulpcore/).

If you are just getting started, we recommend:

- [Getting Started with Hugging Face](site:pulp_hugging_face/docs/user/tutorials/getting_started/),
  for setting up your first pull-through cache for Hugging Face models.
- [Core Concepts](site:pulp_hugging_face/docs/user/learn/concepts/),
  to understand the plugin architecture and key terminology.

## Features

- **Pull-through Caching**: Automatically fetch and cache models, datasets, and spaces from Hugging Face Hub on first access
- **Authentication Support**: Use Hugging Face tokens to access private repositories
- **Full Compatibility**: Works seamlessly with `huggingface-cli`, transformers library, and other HF tools
- **All Content Types**: Support for models, datasets, and spaces
- **On-demand Downloads**: Reduce storage by only downloading content when requested
- **Versioned Repositories**: Every operation creates a restorable snapshot

## Documentation Sections

### For Users

- [User Guide](site:pulp_hugging_face/docs/user/) - Getting started and feature documentation
- [Tutorials](site:pulp_hugging_face/docs/user/tutorials/getting_started/) - Step-by-step guides
- [Guides](site:pulp_hugging_face/docs/user/guides/configuration/) - Detailed workflow documentation

### For Administrators

- [Admin Guide](site:pulp_hugging_face/docs/admin/) - Installation and configuration

### For Developers

- [Developer Guide](site:pulp_hugging_face/docs/dev/) - Contributing to the plugin

## Quick Start

1. Create a remote pointing to Hugging Face Hub:

```bash
curl -X POST https://pulp.example.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{"name": "hf-remote", "url": "https://huggingface.co", "policy": "on_demand"}'
```

2. Create a distribution for pull-through caching:

```bash
curl -X POST https://pulp.example.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{"name": "hf-cache", "base_path": "huggingface", "remote": "<remote_href>"}'
```

3. Access Hugging Face content through Pulp:

```bash
# Use with huggingface-cli
export HF_ENDPOINT="https://pulp.example.com/pulp/content/huggingface"
huggingface-cli download bert-base-uncased
```

