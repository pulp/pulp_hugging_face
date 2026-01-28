# Welcome to Pulp Hugging Face for Admins!

Here you'll find information about Hugging Face-specific admin workflows.

If you just got here, consider following the top [Admin Manual](site:pulpcore/#admin) links, as it provides the common ground for setting up and configuring your Pulp deployment.

## Configuration

The pulp_hugging_face plugin currently uses standard pulpcore configuration. Key settings to consider:

- **CONTENT_ORIGIN**: The base URL for serving content
- **REMOTE_USER_ENVIRON_NAME**: For external authentication setups

See the [pulpcore settings documentation](site:pulpcore/docs/admin/reference/settings/) for details on these and other core settings.

## Access Control

The plugin uses pulpcore's standard Role Based Access Control (RBAC) system. Users with appropriate permissions can:

- Create and manage Hugging Face remotes
- Create and manage distributions for pull-through caching
- View cached content

Refer to the [pulpcore RBAC documentation](site:pulpcore/docs/admin/guides/rbac/) for information on managing permissions.

