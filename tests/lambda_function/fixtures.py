"""Non-pytest fixtures for tests."""

import json

with open("tests/lambda_function/kubernetes_openapi.json") as in_file:
    _SWAGGER = json.loads(in_file.read())

_GROUP_VERSION_KIND_KEY = "x-kubernetes-group-version-kind"
_PATHS = _SWAGGER["paths"]
GROUP_VERSIONS = []
GROUP_VERSION_KINDS = []
_SEEN_GROUP_VERSIONS = set()
_SEEN_GROUP_VERSION_KINDS = set()
for path in _PATHS:
    # Checking for DELETE and put DELETE and PUT
    if not all(key in _PATHS[path] for key in ["delete", "put"]):
        continue
    # Checking for POST on one level up
    expected_path_end = "/{name}"
    if not path.endswith(expected_path_end):
        continue
    parent_path = path[: -len(expected_path_end)]
    if not "post" in _PATHS[parent_path]:
        continue

    # Checking if the group, version and kind combination already exists
    group_version_kind = _PATHS[path]["delete"][_GROUP_VERSION_KIND_KEY]
    unique_key = "/".join(group_version_kind.values())
    if unique_key in _SEEN_GROUP_VERSION_KINDS:
        continue
    _SEEN_GROUP_VERSION_KINDS.add(unique_key)
    GROUP_VERSION_KINDS.append(group_version_kind)

    group_version = {
        key: value
        for key, value in group_version_kind.items()
        if key in {"group", "version"}
    }
    unique_key = "/".join(group_version.values())
    if unique_key in _SEEN_GROUP_VERSIONS:
        continue
    _SEEN_GROUP_VERSIONS.add(unique_key)
    GROUP_VERSIONS.append(group_version)
