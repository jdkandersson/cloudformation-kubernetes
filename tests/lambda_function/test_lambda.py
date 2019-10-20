"""Tests for the lambda function."""

from unittest import mock

import pytest

from lambda_function import exceptions
from lambda_function import index


@pytest.mark.parametrize(
    "event",
    [
        {
            "ResourceProperties": {"key": "value"},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Not Implemented",
            "ResourceProperties": {"key": "value"},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"key": "value"},
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"key": "value"},
            "ResponseURL": "response url 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"key": "value"},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"key": "value"},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
        },
    ],
    ids=[
        "RequestType missing",
        "RequestType notimplemented",
        "ResourceProperties missing",
        "ResponseURL missing",
        "StackId missing",
        "RequestId missing",
        "LogicalResourceId missing",
    ],
)
@pytest.mark.lambda_function
def test_lambda_handler_malformed_event(event, _mocked_operations_create):
    """
    GIVEN event dictionary that is not as expected
    WHEN lambda_handler is called with the event
    THEN MalformedEventError is raised.
    """
    with pytest.raises(exceptions.MalformedEventError):
        index.lambda_handler(event, mock.MagicMock())


@pytest.mark.lambda_function
def test_create_create_call(
    mocked_operations_create: mock.MagicMock, valid_lambda_event
):
    """
    GIVEN mocked operations.create and create Cloudformation request
    WHEN lambda_handler is called with the request
    THEN create is called with the body from the request.
    """
    event = {
        **valid_lambda_event,
        **{"RequestType": "Create", "ResourceProperties": {"key": "value"}},
    }

    index.lambda_handler(event, mock.MagicMock())

    mocked_operations_create.assert_called_once_with(body={"key": "value"})
