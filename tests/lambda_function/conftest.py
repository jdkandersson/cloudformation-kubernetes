"""Fixtures for lambda function."""

from unittest import mock

import pytest

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
