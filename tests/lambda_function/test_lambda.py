"""Tests for the lambda function."""

import json
from unittest import mock

import pytest

from lambda_function import exceptions
from lambda_function import index
from lambda_function import operations


@pytest.mark.parametrize(
    "event",
    [
        {
            "ResourceProperties": {"metadata": {"name": "name 1"}},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Not Implemented",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
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
            "ResourceProperties": {},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {}},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
            "ResponseURL": "response url 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "LogicalResourceId": "logical resource id 1",
        },
        {
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
        },
    ],
    ids=[
        "RequestType missing",
        "RequestType notimplemented",
        "ResourceProperties missing",
        "ResourceProperties metadata missing",
        "ResourceProperties metadata name missing",
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
    mocked_operations_create: mock.MagicMock,
    valid_lambda_event,
    _mocked_urllib3_pool_manager,
    _mocked_json_dumps,
):
    """
    GIVEN mocked operations.create and create Cloudformation request
    WHEN lambda_handler is called with the request
    THEN create is called with the body from the request.
    """
    event = {
        **valid_lambda_event,
        **{
            "RequestType": "Create",
            "ResourceProperties": {"metadata": {"name": "name 1"}},
        },
    }

    index.lambda_handler(event, mock.MagicMock())

    mocked_operations_create.assert_called_once_with(
        body={"metadata": {"name": "name 1"}}
    )


@pytest.mark.lambda_function
def test_create_put(
    mocked_operations_create: mock.MagicMock,
    valid_lambda_event,
    mocked_urllib3_pool_manager: mock.MagicMock,
):
    """
    GIVEN mocked operations.create that returns success response and
        urllib3.PoolManager and create Cloudformation request
    WHEN lambda_handler is called with the request
    THEN PoolManager.request PUT is called with the ResponseURL from the request with
        the correct body.
    """
    mocked_operations_create.return_value = operations.CreateReturn(
        "SUCCESS", None, "physical name 1"
    )
    event = {
        **valid_lambda_event,
        **{
            "RequestType": "Create",
            "ResponseURL": "response url 1",
            "StackId": "stack id 1",
            "RequestId": "request id 1",
            "LogicalResourceId": "logical resource id 1",
        },
    }

    index.lambda_handler(event, mock.MagicMock())

    mocked_urllib3_pool_manager.return_value.request.assert_called_once_with(
        "PUT",
        "response url 1",
        body=json.dumps(
            {
                "StackId": "stack id 1",
                "RequestId": "request id 1",
                "LogicalResourceId": "logical resource id 1",
                "Status": "SUCCESS",
                "PhysicalResourceId": "physical name 1",
            }
        ).encode("utf-8"),
    )
