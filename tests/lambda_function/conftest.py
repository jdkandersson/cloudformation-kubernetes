"""Fixtures for lambda function."""

import json
from unittest import mock

import pytest
import urllib3

from lambda_function import operations


@pytest.fixture
def mocked_operations_create(monkeypatch):
    """Monkeypatch operations.create."""
    mock_create = mock.MagicMock()
    monkeypatch.setattr(operations, "create", mock_create)
    return mock_create


@pytest.fixture
def _mocked_operations_create(
    mocked_operations_create,  # pylint: disable=redefined-outer-name
):
    """For supressing unused-argument pylint error."""
    return mocked_operations_create


@pytest.fixture
def mocked_operations_update(monkeypatch):
    """Monkeypatch operations.update."""
    mock_update = mock.MagicMock()
    monkeypatch.setattr(operations, "update", mock_update)
    return mock_update


@pytest.fixture
def mocked_operations_delete(monkeypatch):
    """Monkeypatch operations.delete."""
    mock_delete = mock.MagicMock()
    monkeypatch.setattr(operations, "delete", mock_delete)
    return mock_delete


@pytest.fixture
def valid_lambda_event():
    """A valid lambda event object."""
    return {
        "RequestType": "Create",
        "ResourceProperties": {"key": "value"},
        "ResponseURL": "response url 1",
        "StackId": "stack id 1",
        "RequestId": "request id 1",
        "LogicalResourceId": "logical resource id 1",
    }


@pytest.fixture
def mocked_urllib3_pool_manager(monkeypatch):
    """Monkeypatch urllib3.PoolManager."""
    mock_pool_manager = mock.MagicMock()
    monkeypatch.setattr(urllib3, "PoolManager", mock_pool_manager)
    return mock_pool_manager


@pytest.fixture
def _mocked_urllib3_pool_manager(
    mocked_urllib3_pool_manager,  # pylint: disable=redefined-outer-name
):
    """For supressing unused-argument pylint error."""
    return mocked_urllib3_pool_manager


@pytest.fixture
def mocked_json_dumps(monkeypatch):
    """Monkeypatch json.dumps."""
    mock_dumps = mock.MagicMock()
    monkeypatch.setattr(json, "dumps", mock_dumps)
    return mock_dumps


@pytest.fixture
def _mocked_json_dumps(mocked_json_dumps):  # pylint: disable=redefined-outer-name
    """For supressing unused-argument pylint error."""
    return mocked_json_dumps
