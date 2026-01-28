# Authentication for Private Repositories

This guide explains how to configure authentication for accessing private Hugging Face repositories through Pulp.

## Overview

Hugging Face Hub uses bearer token authentication for private repositories. To access private
content through Pulp, you need to provide your Hugging Face token when creating a remote.

## Obtaining a Hugging Face Token

1. Log in to your [Hugging Face account](https://huggingface.co/login)
2. Navigate to **Settings** > **Access Tokens**
3. Click **New token**
4. Choose the appropriate permissions:
   - **Read**: For accessing private repositories (recommended for caching)
   - **Write**: For publishing content (not needed for pull-through caching)
5. Copy the generated token

!!! warning "Token Security"
    - Never commit tokens to version control
    - Use environment variables or secrets management
    - Rotate tokens periodically
    - Use read-only tokens when possible

## Creating an Authenticated Remote

=== "Create Remote with Token"

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

=== "Using Environment Variable"

    ```bash
    # Store token in environment variable
    export HF_TOKEN="hf_YOUR_TOKEN_HERE"
    
    curl -X POST https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d "{
        \"name\": \"hf-private\",
        \"url\": \"https://huggingface.co\",
        \"policy\": \"on_demand\",
        \"hf_token\": \"$HF_TOKEN\"
      }"
    ```

## Token Permissions

Hugging Face tokens can have different permission levels:

| Permission | Use Case | Notes |
|------------|----------|-------|
| **Read** | Pull-through caching | Recommended for most use cases |
| **Write** | Publishing models | Not needed for caching |
| **Fine-grained** | Specific repos only | Best for security |

### Fine-grained Access Tokens

For enhanced security, create tokens with access to specific repositories only:

1. In Hugging Face Settings > Access Tokens
2. Click **New token** and select **Fine-grained**
3. Select specific repositories to grant access
4. Set expiration date (recommended)

## Updating Token on Existing Remote

If you need to rotate or update your token:

=== "Update Token"

    ```bash
    REMOTE_HREF="/pulp/api/v3/remotes/hugging_face/hugging-face/..."
    
    curl -X PATCH https://your-pulp-instance.com${REMOTE_HREF} \
      -H "Content-Type: application/json" \
      -u admin:password \
      -d '{
        "hf_token": "hf_NEW_TOKEN_HERE"
      }'
    ```

=== "Output"

    ```json
    {
      "pulp_href": "/pulp/api/v3/remotes/hugging_face/hugging-face/...",
      "name": "hf-private",
      "url": "https://huggingface.co",
      "policy": "on_demand",
      "hf_token": "hf_NEW_TOKEN_HERE"
    }
    ```

## Multiple Remotes for Different Access Levels

You can create multiple remotes with different authentication configurations:

```bash
# Public remote - no authentication
curl -X POST https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "name": "hf-public",
    "url": "https://huggingface.co",
    "policy": "on_demand"
  }'

# Private remote - with authentication
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

Then create separate distributions for each:

```bash
# Distribution for public content
curl -X POST https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "name": "hf-public-dist",
    "base_path": "hf-public",
    "remote": "/pulp/api/v3/remotes/hugging_face/hugging-face/PUBLIC_REMOTE_HREF/"
  }'

# Distribution for private content
curl -X POST https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "name": "hf-private-dist",
    "base_path": "hf-private",
    "remote": "/pulp/api/v3/remotes/hugging_face/hugging-face/PRIVATE_REMOTE_HREF/"
  }'
```

## Accessing Private Content

Once configured, accessing private content works the same as public content:

```bash
# Access private model through authenticated distribution
curl http://your-pulp-instance/pulp/content/hf-private/your-org/private-model/resolve/main/config.json
```

## Troubleshooting Authentication Issues

### Common Errors

**401 Unauthorized**
: Token is invalid, expired, or doesn't have access to the requested repository

**403 Forbidden**
: Token has insufficient permissions for the requested operation

**404 Not Found**
: Repository doesn't exist or token doesn't have access

### Verification Steps

1. **Test token directly with Hugging Face:**
   ```bash
   curl -H "Authorization: Bearer $HF_TOKEN" \
     https://huggingface.co/api/models/your-org/private-model
   ```

2. **Check remote configuration:**
   ```bash
   curl https://your-pulp-instance.com/pulp/api/v3/remotes/hugging_face/hugging-face/ \
     -u admin:password | jq '.results[] | {name, hf_token}'
   ```

3. **Verify distribution is using correct remote:**
   ```bash
   curl https://your-pulp-instance.com/pulp/api/v3/distributions/hugging_face/hugging-face/ \
     -u admin:password | jq '.results[] | {name, remote}'
   ```

