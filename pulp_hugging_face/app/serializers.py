"""
Check `Plugin Writer's Guide`_ for more details.

.. _Plugin Writer's Guide:
    https://pulpproject.org/pulpcore/docs/dev/
"""

from gettext import gettext as _

from rest_framework import serializers

from pulpcore.plugin import serializers as platform
from pulpcore.plugin.serializers import DetailRelatedField
from pulpcore.plugin.models import Remote

from . import models


class HuggingFaceContentSerializer(platform.SingleArtifactContentSerializer):
    """
    A Serializer for HuggingFaceContent.
    """

    repo_id = serializers.CharField(
        help_text=_("The Hugging Face repository ID (e.g., 'microsoft/DialoGPT-medium')")
    )
    repo_type = serializers.ChoiceField(
        choices=[("models", "Models"), ("datasets", "Datasets"), ("spaces", "Spaces")],
        default="models",
        help_text=_("The type of Hugging Face repository"),
    )
    relative_path = serializers.CharField(help_text=_("The relative path within the repository"))
    revision = serializers.CharField(default="main", help_text=_("The git revision/branch/tag"))
    size = serializers.IntegerField(
        required=False, allow_null=True, help_text=_("File size in bytes")
    )
    etag = serializers.CharField(
        required=False, allow_null=True, help_text=_("ETag from Hugging Face")
    )
    last_modified = serializers.DateTimeField(
        required=False, allow_null=True, help_text=_("Last modified timestamp")
    )

    class Meta:
        fields = platform.SingleArtifactContentSerializer.Meta.fields + (
            "repo_id",
            "repo_type",
            "relative_path",
            "revision",
            "size",
            "etag",
            "last_modified",
        )
        model = models.HuggingFaceContent


class HuggingFaceRemoteSerializer(platform.RemoteSerializer):
    """
    A Serializer for HuggingFaceRemote with Hugging Face specific configuration.
    """

    hf_hub_url = serializers.URLField(
        default="https://huggingface.co", help_text=_("Base URL for Hugging Face Hub")
    )

    hf_token = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        style={"input_type": "password"},
        help_text=_("Hugging Face authentication token for private repositories"),
    )

    policy = serializers.ChoiceField(
        help_text=_(
            "The policy to use when downloading content. The possible values include: "
            "'immediate', 'on_demand', and 'streamed'. 'on_demand' enables pull-through caching."
        ),
        choices=Remote.POLICY_CHOICES,
        default=Remote.ON_DEMAND,
    )

    class Meta:
        fields = platform.RemoteSerializer.Meta.fields + ("hf_hub_url", "hf_token")
        model = models.HuggingFaceRemote


class HuggingFaceRepositorySerializer(platform.RepositorySerializer):
    """
    A Serializer for HuggingFaceRepository.

    Add any new fields if defined on HuggingFaceRepository.
    Similar to the example above, in HuggingFaceContentSerializer.
    Additional validators can be added to the parent validators list

    For example::

    class Meta:
        validators = platform.RepositorySerializer.Meta.validators + [myValidator1, myValidator2]
    """

    class Meta:
        fields = platform.RepositorySerializer.Meta.fields
        model = models.HuggingFaceRepository


class HuggingFacePublicationSerializer(platform.PublicationSerializer):
    """
    A Serializer for HuggingFacePublication.

    Add any new fields if defined on HuggingFacePublication.
    Similar to the example above, in HuggingFaceContentSerializer.
    Additional validators can be added to the parent validators list

    For example::

    class Meta:
        validators = platform.PublicationSerializer.Meta.validators + [myValidator1, myValidator2]
    """

    class Meta:
        fields = platform.PublicationSerializer.Meta.fields
        model = models.HuggingFacePublication


class HuggingFaceDistributionSerializer(platform.DistributionSerializer):
    """
    A Serializer for HuggingFaceDistribution with pull-through caching support.
    """

    publication = platform.DetailRelatedField(
        required=False,
        help_text=_("Publication to be served"),
        view_name_pattern=r"publications(-.*/.*)?-detail",
        queryset=models.Publication.objects.exclude(complete=False),
        allow_null=True,
    )

    remote = DetailRelatedField(
        required=False,
        help_text=_("Remote that can be used to fetch content when using pull-through caching."),
        view_name_pattern=r"remotes(-.*/.*)?-detail",
        queryset=Remote.objects.all(),  # Accept any remote type
        allow_null=True,
    )

    class Meta:
        fields = platform.DistributionSerializer.Meta.fields + ("publication", "remote")
        model = models.HuggingFaceDistribution
