"""Kubernetes operations."""

import typing

import kubernetes

from . import exceptions, helpers


class CreateReturn(typing.NamedTuple):
    """
    Structure of the create return value.

    Attrs:
        status: The status of the operation. Is SUCCESS or FAILURE.
        reason: If the status is FAILURE, the reason for the failure.
        physical_name: If the status is success, the physical name of the created
            resource in the form [<namespace>/]<name> where the namespace is included
            if the operation is namespaced.

    """

    status: str
    reason: typing.Optional[str]
    physical_name: typing.Optional[str]


def create(*, body: typing.Dict[str, typing.Any]) -> CreateReturn:
    """
    Execute create command.

    Args:
        body: The body to create.

    Returns:
        Information about the outcome of the operation.

    """
    try:
        api_version = helpers.get_api_version(body=body)
        kind = helpers.get_kind(body=body)
    except exceptions.ParentError as exc:
        return CreateReturn("FAILURE", str(exc), None)
    client_function, namespaced = helpers.get_function(
        api_version=api_version, kind=kind, operation="create"
    )

    # Handling non-namespaced cases
    if not namespaced:
        try:
            response = client_function(body=body)
            return CreateReturn("SUCCESS", None, response.metadata.name)
        except kubernetes.client.rest.ApiException as exc:
            return CreateReturn("FAILURE", str(exc), None)

    # Handling namespaced
    namespace = helpers.calculate_namespace(body=body)
    try:
        response = client_function(body=body, namespace=namespace)
        return CreateReturn(
            "SUCCESS", None, f"{response.metadata.namespace}/{response.metadata.name}"
        )
    except kubernetes.client.rest.ApiException as exc:
        return CreateReturn("FAILURE", str(exc), None)
