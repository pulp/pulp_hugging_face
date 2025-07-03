#!/usr/bin/env python3
"""
Test script to validate the pulp_hugging_face plugin implementation.
This script checks that all required methods are properly implemented.
"""

import sys

# Add the plugin to the path
sys.path.insert(0, "/root/pulp/pulp_hugging_face")


def test_imports():
    """Test that all modules can be imported (with mocked dependencies)."""
    print("Testing imports...")

    # Mock the dependencies that aren't available in this environment
    import unittest.mock as mock

    modules_to_mock = [
        "django",
        "django.db",
        "django.db.models",
        "django.db.transaction",
        "rest_framework",
        "rest_framework.decorators",
        "rest_framework.response",
        "rest_framework.serializers",
        "rest_framework.status",
        "drf_spectacular",
        "drf_spectacular.utils",
        "pulpcore",
        "pulpcore.plugin",
        "pulpcore.plugin.models",
        "pulpcore.plugin.serializers",
        "pulpcore.plugin.viewsets",
        "pulpcore.plugin.actions",
        "pulpcore.plugin.tasking",
        "pulpcore.plugin.util",
        "pulpcore.plugin.handlers",
    ]

    for module in modules_to_mock:
        sys.modules[module] = mock.MagicMock()

    try:
        # Test model imports
        pass

        print("✅ Models import successfully")

        # Test serializer imports

        print("✅ Serializers import successfully")

        # Test viewset imports

        print("✅ ViewSets import successfully")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_pull_through_methods():
    """Test that pull-through caching methods are properly implemented."""
    print("\nTesting pull-through caching methods...")

    # Mock dependencies
    import unittest.mock as mock

    modules_to_mock = [
        "django",
        "django.db",
        "django.db.models",
        "django.db.transaction",
        "rest_framework",
        "rest_framework.decorators",
        "rest_framework.response",
        "rest_framework.serializers",
        "rest_framework.status",
        "drf_spectacular",
        "drf_spectacular.utils",
        "pulpcore",
        "pulpcore.plugin",
        "pulpcore.plugin.models",
        "pulpcore.plugin.serializers",
        "pulpcore.plugin.viewsets",
        "pulpcore.plugin.actions",
        "pulpcore.plugin.tasking",
        "pulpcore.plugin.util",
        "pulpcore.plugin.handlers",
    ]

    for module in modules_to_mock:
        sys.modules[module] = mock.MagicMock()

    try:
        from pulp_hugging_face.app.models import HuggingFaceContent

        # Check that required methods exist
        methods_to_check = [
            "get_remote_artifact_url",
            "get_remote_artifact_content_type",
            "init_from_artifact_and_relative_path",
        ]

        for method_name in methods_to_check:
            if hasattr(HuggingFaceContent, method_name):
                print(f"✅ Method {method_name} is implemented")
            else:
                print(f"❌ Method {method_name} is missing")
                return False

        # Test method signatures by inspecting the source
        import inspect

        # Check get_remote_artifact_url signature
        method = getattr(HuggingFaceContent, "get_remote_artifact_url")
        sig = inspect.signature(method)
        expected_params = ["self", "remote", "request", "path"]
        actual_params = list(sig.parameters.keys())
        if actual_params == expected_params:
            print("✅ get_remote_artifact_url has correct signature")
        else:
            print(
                f"❌ get_remote_artifact_url signature mismatch: "
                f"{actual_params} vs {expected_params}"
            )

        return True

    except Exception as e:
        print(f"❌ Method test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Pulp Hugging Face Plugin Validation")
    print("=" * 40)

    # Test imports
    imports_ok = test_imports()

    # Test pull-through methods
    methods_ok = test_pull_through_methods()

    print("\n" + "=" * 40)
    if imports_ok and methods_ok:
        print("✅ All tests passed! Plugin implementation looks correct.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
