"""Tests for operations."""
# pylint: disable=redefined-outer-name

from unittest import mock

import kubernetes
import pytest
from lambda_function import exceptions, helpers, operations


@pytest.fixture(scope="function", autouse=True)
def mocked_get_api_version(monkeypatch):
    """Monkeypatch helpers.get_api_version."""
    mock_get_api_version = mock.MagicMock()
    monkeypatch.setattr(helpers, "get_api_version", mock_get_api_version)
    return mock_get_api_version


@pytest.fixture(scope="function", autouse=True)
def mocked_get_kind(monkeypatch):
    """Monkeypatch helpers.get_kind."""
    mock_get_kind = mock.MagicMock()
    monkeypatch.setattr(helpers, "get_kind", mock_get_kind)
    return mock_get_kind


@pytest.fixture(scope="function", autouse=True)
def mocked_get_function(monkeypatch):
    """Monkeypatch helpers.get_function."""
    mock_get_function = mock.MagicMock()
    mock_get_function.return_value = (mock.MagicMock(), False)
    monkeypatch.setattr(helpers, "get_function", mock_get_function)
    return mock_get_function


@pytest.fixture(scope="function", autouse=True)
def mocked_calculate_namespace(monkeypatch):
    """Monkeypatch helpers.calculate_namespace."""
    mock_calculate_namespace = mock.MagicMock()
    monkeypatch.setattr(helpers, "calculate_namespace", mock_calculate_namespace)
    return mock_calculate_namespace


def test_create_get_api_version_call(mocked_get_api_version: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_api_version
    WHEN create is called with the body
    THEN get_api_version is called with the body.
    """
    mock_body = mock.MagicMock()

    operations.create(body=mock_body)

    mocked_get_api_version.assert_called_once_with(body=mock_body)


def test_create_get_api_version_raises(mocked_get_api_version: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_api_version that raises ApiVersionMissingError
    WHEN create is called with the body
    THEN failure response is returned.
    """
    mocked_get_api_version.side_effect = exceptions.ApiVersionMissingError

    return_value = operations.create(body=mock.MagicMock())

    assert return_value == operations.CreateReturn(
        "FAILURE", "apiVersion is required.", None
    )


def test_create_get_kind_call(mocked_get_kind: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_kind
    WHEN create is called with the body
    THEN get_kind is called with the body.
    """
    mock_body = mock.MagicMock()

    operations.create(body=mock_body)

    mocked_get_kind.assert_called_once_with(body=mock_body)


def test_create_get_kind_raises(mocked_get_kind: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_kind that raises KindMissingError
    WHEN create is called with the body
    THEN failure response is returned.
    """
    mocked_get_kind.side_effect = exceptions.KindMissingError

    return_value = operations.create(body=mock.MagicMock())

    assert return_value == operations.CreateReturn("FAILURE", "kind is required.", None)


def test_create_get_function_call(
    mocked_get_api_version: mock.MagicMock,
    mocked_get_kind: mock.MagicMock,
    mocked_get_function: mock.MagicMock,
):
    """
    GIVEN mocked get_api_version, get_kind and get_function
    WHEN create is called with the body
    THEN get_function is called with get_api_version and get_kind return value and the
        create operation.
    """
    operations.create(body=mock.MagicMock())

    mocked_get_function.assert_called_once_with(
        api_version=mocked_get_api_version.return_value,
        kind=mocked_get_kind.return_value,
        operation="create",
    )


def test_create_client_function_call(mocked_get_function: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_function that returns a client function and False
        for namespaced
    WHEN create is called with the body
    THEN the client function is called with the body.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, False
    )

    operations.create(body=mock_body)

    mock_client_function.assert_called_once_with(body=mock_body)


def test_create_client_function_return(mocked_get_function: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_function that returns a client function that
        returns the metadata with a name and False for namespaced
    WHEN create is called with the body
    THEN success response is returned.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mock_return = mock.MagicMock()
    mock_return.metadata.name = "name 1"
    mock_client_function.return_value = mock_return
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, False
    )

    return_value = operations.create(body=mock_body)

    assert return_value == operations.CreateReturn("SUCCESS", None, "name 1")


def test_create_client_function_raises(mocked_get_function: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_function that returns a client function that
        raises ApiException and False for namespaced
    WHEN create is called with the body
    THEN failure response is returned.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mock_client_function.side_effect = kubernetes.client.rest.ApiException(
        "400", "reason 1"
    )
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, False
    )

    return_value = operations.create(body=mock_body)

    assert return_value == operations.CreateReturn(
        "FAILURE", "(400)\nReason: reason 1\n", None
    )


def test_create_calculate_namespace_call(
    mocked_get_function: mock.MagicMock, mocked_calculate_namespace: mock.MagicMock
):
    """
    GIVEN mocked body and mocked get_function that returns a client function and True
        for namespaced and mocked calculate_namespace
    WHEN create is called with the body
    THEN calculate_namespace is called with the body.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, True
    )

    operations.create(body=mock_body)

    mocked_calculate_namespace.assert_called_once_with(body=mock_body)


def test_create_client_function_namespace_call(
    mocked_get_function: mock.MagicMock, mocked_calculate_namespace: mock.MagicMock
):
    """
    GIVEN mocked body and mocked get_function that returns a client function and True
        for namespaced
    WHEN create is called with the body
    THEN the client function is called with the body.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, True
    )

    operations.create(body=mock_body)

    mock_client_function.assert_called_once_with(
        namespace=mocked_calculate_namespace.return_value, body=mock_body
    )


def test_create_client_function_namespace_return(mocked_get_function: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_function that returns a client function that
        returns the metadata with a name and True for namespaced
    WHEN create is called with the body
    THEN success response is returned.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mock_return = mock.MagicMock()
    mock_return.metadata.namespace = "namespace 1"
    mock_return.metadata.name = "name 1"
    mock_client_function.return_value = mock_return
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, True
    )

    return_value = operations.create(body=mock_body)

    assert return_value == operations.CreateReturn(
        "SUCCESS", None, "namespace 1/name 1"
    )


def test_create_client_function_namespace_raises(mocked_get_function: mock.MagicMock):
    """
    GIVEN mocked body and mocked get_function that returns a client function that
        raises ApiException and True for namespaced
    WHEN create is called with the body
    THEN failure response is returned.
    """
    mock_body = mock.MagicMock()
    mock_client_function = mock.MagicMock()
    mock_client_function.side_effect = kubernetes.client.rest.ApiException(
        "400", "reason 1"
    )
    mocked_get_function.return_value = helpers.GetFunctionReturn(
        mock_client_function, True
    )

    return_value = operations.create(body=mock_body)

    assert return_value == operations.CreateReturn(
        "FAILURE", "(400)\nReason: reason 1\n", None
    )
