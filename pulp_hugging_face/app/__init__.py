from pulpcore.plugin import PulpPluginAppConfig


class PulpHuggingFacePluginAppConfig(PulpPluginAppConfig):
    """Entry point for the hugging_face plugin."""

    name = "pulp_hugging_face.app"
    label = "hugging_face"
    version = "0.1.1.dev"
    python_package_name = "pulp_hugging_face"
    domain_compatible = True
