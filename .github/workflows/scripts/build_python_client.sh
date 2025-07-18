#!/bin/bash

# This script expects all <app_label>-api.json files to exist in the plugins root directory.
# It produces a <app_label>-python-client.tar and <app_label>-python-client-docs.tar file in the plugins root directory.

# WARNING: DO NOT EDIT!
#
# This file was generated by plugin_template, and is managed by it. Please use
# './plugin-template --github pulp_hugging_face' to update this file.
#
# For more info visit https://github.com/pulp/plugin_template

set -mveuo pipefail

# make sure this script runs at the repo root
cd "$(dirname "$(realpath -e "$0")")"/../../..

pushd ../pulp-openapi-generator
rm -rf "pulp_hugging_face-client"

./gen-client.sh "../pulp_hugging_face/hugging_face-api.json" "hugging_face" python "pulp_hugging_face"

pushd pulp_hugging_face-client
python setup.py sdist bdist_wheel --python-tag py3

twine check "dist/pulp_hugging_face_client-"*"-py3-none-any.whl"
twine check "dist/pulp_hugging_face-client-"*".tar.gz"

tar cvf "../../pulp_hugging_face/hugging_face-python-client.tar" ./dist

find ./docs/* -exec sed -i 's/Back to README/Back to HOME/g' {} \;
find ./docs/* -exec sed -i 's/README//g' {} \;
cp README.md docs/index.md
sed -i 's/docs\///g' docs/index.md
find ./docs/* -exec sed -i 's/\.md//g' {} \;

cat >> mkdocs.yml << DOCSYAML
---
site_name: PulpHuggingFace Client
site_description: HuggingFace bindings
site_author: Pulp Team
site_url: https://docs.pulpproject.org/pulp_hugging_face_client/
repo_name: pulp/pulp_hugging_face
repo_url: https://github.com/pulp/pulp_hugging_face
theme: readthedocs
DOCSYAML

# Building the bindings docs
mkdocs build

# Pack the built site.
tar cvf ../../pulp_hugging_face/hugging_face-python-client-docs.tar ./site
popd
popd
