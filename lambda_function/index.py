"""Handle CloudFormation requests."""

import dataclasses
import typing

from . import exceptions
from . import operations


@dataclasses.dataclass
class Parameters:
    """Expected parameters for the lambda function."""

    request_type: str
    resource_properties: typing.Dict[str, typing.Any]
    response_url: str
    stack_id: str
    request_id: str
    logical_resource_id: str


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

    return Parameters(
        request_type,
        resource_properties,
        response_url,
        stack_id,
        request_id,
        logical_resource_id,
    )


def lambda_handler(event, _context):
    """Handle CLoudFormation custom resource requests."""
    # Checking that required keys are in the event
    parameters = parameters_from_event(event=event)

    if parameters.request_type == "Create":
        operations.create(body=parameters.resource_properties)
    else:
        raise exceptions.MalformedEventError(
            f"{parameters.request_type} RequestType has not been implemented."
        )
