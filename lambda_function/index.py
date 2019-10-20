"""Handle CloudFormation requests."""

from . import exceptions
from . import operations


def lambda_handler(event, _context):
    """Handle CLoudFormation custom resource requests."""
    # Checking for RequestType
    operation_name = event.get("RequestType")
    if operation_name is None:
        raise exceptions.MalformedEventError(
            "RequestType is a required property in the event."
        )
    body = event.get("ResourceProperties")
    if body is None:
        raise exceptions.MalformedEventError(
            "ResourceProperties is a required property in the event."
        )

    if operation_name == "Create":
        operations.create(body=body)
    else:
        raise exceptions.MalformedEventError(
            f"{operation_name} RequestType has not been implemented."
        )
