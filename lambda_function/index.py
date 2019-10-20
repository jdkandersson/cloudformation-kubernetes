"""Handle CloudFormation requests."""

from . import exceptions
from . import operations


def lambda_handler(event, _context):
    """Handle CLoudFormation custom resource requests."""
    # Checking that required keys are in the event
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

    if request_type == "Create":
        operations.create(body=resource_properties)
    else:
        raise exceptions.MalformedEventError(
            f"{request_type} RequestType has not been implemented."
        )
