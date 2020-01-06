"""Handle CloudFormation requests."""

import dataclasses
import json
import typing

import urllib3

from . import exceptions
from . import operations

# A physical name used for when failures occur
FAIL_PHYSICAL_NAME_PREFIX = "[FAIL]"


@dataclasses.dataclass
class Parameters:
    """Expected parameters for the lambda function."""

    request_type: str
    resource_properties: typing.Dict[str, typing.Any]
    response_url: str
    stack_id: str
    request_id: str
    logical_resource_id: str
    physical_resource_id: typing.Optional[str]


def parameters_from_event(*, event: typing.Dict[str, typing.Any]) -> Parameters:
    """
    Construct Parameters from lambda event.

    Raise MalformedEventError if a required property is missing.

    Args:
        event: The details for the lambda event.

    Returns:
        The Parameters initialized using the event.

    """
    request_type = event.get("RequestType")
    if request_type is None:
        raise exceptions.MalformedEventError(
            "RequestType is a required property in the event."
        )
    resource_properties = event.get("ResourceProperties")
    if resource_properties is None:
        raise exceptions.MalformedEventError(
            "ResourceProperties is a required property in the event."
        )
    response_url = event.get("ResponseURL")
    if response_url is None:
        raise exceptions.MalformedEventError(
            "ResponseURL is a required property in the event."
        )
    stack_id = event.get("StackId")
    if stack_id is None:
        raise exceptions.MalformedEventError(
            "StackId is a required property in the event."
        )
    request_id = event.get("RequestId")
    if request_id is None:
        raise exceptions.MalformedEventError(
            "RequestId is a required property in the event."
        )
    logical_resource_id = event.get("LogicalResourceId")
    if logical_resource_id is None:
        raise exceptions.MalformedEventError(
            "LogicalResourceId is a required property in the event."
        )
    physical_resource_id = event.get("PhysicalResourceId")

    return Parameters(
        request_type,
        resource_properties,
        response_url,
        stack_id,
        request_id,
        logical_resource_id,
        physical_resource_id,
    )


def lambda_handler(event, _context):
    """Handle CLoudFormation custom resource requests."""
    # Checking that required keys are in the event
    parameters = parameters_from_event(event=event)
    response_body: typing.Dict[str, str] = {
        "StackId": parameters.stack_id,
        "RequestId": parameters.request_id,
        "LogicalResourceId": parameters.logical_resource_id,
    }

    if parameters.request_type == "Create":
        _handle_create(parameters=parameters, response_body=response_body)
    elif parameters.request_type == "Update":
        _handle_update(parameters=parameters, response_body=response_body)
    elif parameters.request_type == "Delete":
        _handle_delete(parameters=parameters, response_body=response_body)
    else:
        raise exceptions.MalformedEventError(
            f"{parameters.request_type} RequestType has not been implemented."
        )

    # Sending response
    pool = urllib3.PoolManager(cert_reqs="CERT_REQUIRED")
    pool.request(
        "PUT", parameters.response_url, body=json.dumps(response_body).encode("utf-8")
    )


def _handle_create(
    *, parameters: Parameters, response_body: typing.Dict[str, str]
) -> None:
    """
    Handle create event.

    Args:
        parameters: Event parameters.
        response_body: The body being assembled for the response.

    """
    result = operations.create(body=parameters.resource_properties)
    response_body["Status"] = result.status
    if result.physical_name is not None:
        response_body["PhysicalResourceId"] = result.physical_name
    if result.status == "FAILURE":
        response_body[
            "PhysicalResourceId"
        ] = f"{FAIL_PHYSICAL_NAME_PREFIX}{parameters.logical_resource_id}"
    if result.reason is not None:
        response_body["Reason"] = result.reason


def _handle_update(
    *, parameters: Parameters, response_body: typing.Dict[str, str]
) -> None:
    """
    Handle update event.

    Args:
        parameters: Event parameters.
        response_body: The body being assembled for the response.

    """
    # Check that physical resource id is given
    if parameters.physical_resource_id is None:
        raise exceptions.MalformedEventError(
            "PhysicalResourceId is required for Update event."
        )
    result = operations.update(
        body=parameters.resource_properties,
        physical_name=parameters.physical_resource_id,
    )
    response_body["Status"] = result.status
    response_body["PhysicalResourceId"] = parameters.physical_resource_id
    if result.reason is not None:
        response_body["Reason"] = result.reason


def _handle_delete(
    *, parameters: Parameters, response_body: typing.Dict[str, str]
) -> None:
    """
    Handle delete event.

    Args:
        parameters: Event parameters.
        response_body: The body being assembled for the response.

    """
    # Check that physical resource id is given
    if parameters.physical_resource_id is None:
        raise exceptions.MalformedEventError(
            "PhysicalResourceId is required for Update event."
        )
    response_body["PhysicalResourceId"] = parameters.physical_resource_id
    # Checking for delete due to failed create
    if parameters.physical_resource_id.startswith(FAIL_PHYSICAL_NAME_PREFIX):
        response_body["Status"] = "SUCCESS"
    else:
        result = operations.delete(
            body=parameters.resource_properties,
            physical_name=parameters.physical_resource_id,
        )
        response_body["Status"] = result.status
        if result.reason is not None:
            response_body["Reason"] = result.reason
