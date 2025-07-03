#!/usr/bin/env python3
"""
Test script to demonstrate using Hugging Face Hub library with Pulp pull-through cache.
"""

import os
from huggingface_hub import hf_hub_download, snapshot_download

# Your Pulp distribution endpoint
PULP_ENDPOINT = "http://localhost:5001/pulp/content/huggingface-1751051062/"


def test_single_file_download():
    """Test downloading a single file through Pulp cache."""
    print("Testing single file download...")

    try:
        # Download a single file
        file_path = hf_hub_download(
            repo_id="microsoft/DialoGPT-medium", filename="config.json", endpoint=PULP_ENDPOINT
        )
        print(f"✅ Downloaded: {file_path}")

        # Check file exists and show size
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   File size: {size} bytes")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_snapshot_download():
    """Test downloading entire model snapshot through Pulp cache."""
    print("\nTesting snapshot download...")

    try:
        # Download specific files only (to avoid downloading the large model file)
        snapshot_path = snapshot_download(
            repo_id="microsoft/DialoGPT-medium",
            allow_patterns=["*.json", "*.txt", "README.md"],  # Skip large .bin files
            endpoint=PULP_ENDPOINT,
        )
        print(f"✅ Downloaded snapshot to: {snapshot_path}")

        # List downloaded files
        if os.path.exists(snapshot_path):
            files = os.listdir(snapshot_path)
            print(f"   Files: {files}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("Testing Hugging Face CLI with Pulp Pull-Through Cache")
    print(f"Endpoint: {PULP_ENDPOINT}")
    print("=" * 60)

    test_single_file_download()
    test_snapshot_download()

    print("\n" + "=" * 60)
    print("For CLI usage, set:")
    print(f"export HF_ENDPOINT={PULP_ENDPOINT}")
