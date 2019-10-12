"""Helpers for lambda function."""

import re
import typing

from kubernetes import client

from . import exceptions


def calculate_client(*, api_version: str) -> str:
    """
    Calculate the name of the client based on the api version.

    Args:
        api_version: The Kubernetes API version from a yaml template.

    Returns:
        The name of the kubernetes client module to use for the template.

    """
    group, _, version = api_version.partition("/")
    # Checking for core group
    if version == "":
        version = group
        group = "core"
    # Remove .k8s.io
    group = "".join(group.rsplit(".k8s.io", 1))
    # Capitalize based on dots in group
    group = "".join(word.capitalize() for word in group.split("."))
    return f"{group}{version.capitalize()}Api"


def calculate_function_name(*, kind: str, operation: str, module_name: str) -> str:
    """
    Calculate the name of the function to invoke on a client.

    Args:
        kind: The kind of object to create.
        operation: The operation to perform.
        module_name: The name of the module for the kind.

    Returns:
        The name of the function to invoke.

    """
    # Translating from PascalCase to python_case
    kind = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", kind)
    kind = re.sub("([a-z0-9])([A-Z])", r"\1_\2", kind).lower()

    # Determining the client operation
    if operation == "update":
        operation = "replace"

    # Determining the function to use
    module = getattr(client, module_name)
    namespaced_function_name = f"{operation}_namespaced_{kind}"
    if hasattr(module, namespaced_function_name):
        return namespaced_function_name
    return f"{operation}_{kind}"


class GetFunctionReturn(typing.NamedTuple):
    """Structure of get function return value."""

    client_function: typing.Callable
    namespaced: bool


def get_function(*, api_version: str, kind: str, operation: str) -> GetFunctionReturn:
    """
    Get the function to return and whether it is namespaced.

    Args:
        api_version: The version of the api.
        kind: The kind of resource to create.
        operation: The operation to perform.

    Returns:
        The function to execute and whether it is namespaced.

    """
    client_module_name = calculate_client(api_version=api_version)
    function_name = calculate_function_name(
        kind=kind, operation=operation, module_name=client_module_name
    )
    client_module = getattr(client, client_module_name)
    client_function = getattr(client_module(), function_name)
    return GetFunctionReturn(client_function, "namespaced" in function_name)


def calculate_namespace(*, body: typing.Dict[str, typing.Any]) -> typing.Optional[str]:
    """
    Calculate the namespace to use based on the body.

    Args:
        body: The object for the body of the resource.

    Returns:
        The namespace argument value.

    """
    default_namespace = "default"
    metadata = body.get("metadata")
    if metadata is None:
        return default_namespace
    return metadata.get("namespace", default_namespace)


def get_api_version(*, body: typing.Dict[str, typing.Any]) -> str:
    """
    Get the api version from the body.

    Args:
        body: The body defining the resource.

    Returns:
        The api version for the body.

    """
    api_version = body.get("apiVersion")
    if api_version is None:
        raise exceptions.ApiVersionMissingError
    return api_version


def get_kind(*, body: typing.Dict[str, typing.Any]) -> str:
    """
    Get the kind from the body.

    Args:
        body: The body defining the resource.

    Returns:
        The kind for the body.

    """
    kind = body.get("kind")
    if kind is None:
        raise exceptions.KindMissingError
    return kind
