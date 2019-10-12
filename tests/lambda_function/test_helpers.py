"""Tests for helpers."""

import pytest
from kubernetes import client
from lambda_function import exceptions, helpers

from . import fixtures


@pytest.mark.parametrize("group_version", fixtures.GROUP_VERSIONS)
def test_calculate_client(group_version):
    """
    GIVEN combination of group and version
    WHEN calculate_client is called with the group and version separated by /
    THEN the returned module is available as a client.
    """
    if group_version["group"]:
        api_version = f"{group_version['group']}/{group_version['version']}"
    else:
        api_version = group_version["version"]

    module = helpers.calculate_client(api_version=api_version)

    assert hasattr(client, module)


@pytest.mark.parametrize("group_version_kind", fixtures.GROUP_VERSION_KINDS)
def test_calculate_client_kind(group_version_kind):
    """
    GIVEN combination of group, version and kind
    WHEN calculate_client is called with the kind and module name
    THEN the returned function name is available on the module.
    """
    for operation in ["create", "update", "delete"]:
        # Getting the expected client module name
        if group_version_kind["group"]:
            api_version = (
                f"{group_version_kind['group']}/{group_version_kind['version']}"
            )
        else:
            api_version = group_version_kind["version"]
        module_name = helpers.calculate_client(api_version=api_version)

        client_function = helpers.calculate_function_name(
            kind=group_version_kind["kind"],
            operation=operation,
            module_name=module_name,
        )

        module = getattr(client, module_name)
        assert hasattr(module, client_function)


@pytest.mark.parametrize(
    "body, expected_namespace",
    [
        ({}, None),
        ({"metadata": {}}, None),
        ({"metadata": {"namespace": "namespace 1"}}, "namespace 1"),
    ],
    ids=["empty", "metadata empty", "namespace in metadata"],
)
def test_calculate_namespace_empty(body, expected_namespace):
    """
    GIVEN body and expected namespace
    WHEN calculate_namespace is called with the body
    THEN the expected namespace is returned.
    """
    namespace = helpers.calculate_namespace(body=body)

    assert namespace == expected_namespace


@pytest.mark.parametrize(
    "api_version, kind, expected_function, expected_namespaced",
    [
        (
            "apps/v1",
            "deployment",
            client.AppsV1Api().create_namespaced_deployment,
            True,
        ),
        ("v1", "namespace", client.CoreV1Api().create_namespace, False),
    ],
)
def test_get_function(api_version, kind, expected_function, expected_namespaced):
    """
    GIVEN api version, kind, expected function and expected namespaced
    WHEN get_function is called with the api version, kind and create operation
    THEN the expected function is returned with the expected namespaced value.
    """
    client_function, namespaced = helpers.get_function(
        api_version=api_version, kind=kind, operation="create"
    )

    assert str(client_function)[:-11] == str(expected_function)[:-11]
    assert namespaced == expected_namespaced


def test_get_api_version_missing():
    """
    GIVEN empty dictionary
    WHEN get_api_version is called with the dictionary
    THEN ApiVersionMissingError is raised.
    """
    with pytest.raises(exceptions.ApiVersionMissingError):
        helpers.get_api_version(body={})


def test_get_api_version():
    """
    GIVEN dictionary with apiVersion
    WHEN get_api_version is called with the dictionary
    THEN the value of apiVersion is returned.
    """
    body = {"apiVersion": "version 1"}

    api_version = helpers.get_api_version(body=body)

    assert api_version == "version 1"


def test_get_kind_missing():
    """
    GIVEN empty dictionary
    WHEN get_kind is called with the dictionary
    THEN KindMissingError is raised.
    """
    with pytest.raises(exceptions.KindMissingError):
        helpers.get_kind(body={})


def test_get_kind():
    """
    GIVEN dictionary with kind
    WHEN get_kind is called with the dictionary
    THEN the value of kind is returned.
    """
    body = {"kind": "kind 1"}

    kind = helpers.get_kind(body=body)

    assert kind == "kind 1"
