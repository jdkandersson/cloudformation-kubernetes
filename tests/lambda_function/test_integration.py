"""Integration tests."""
# pylint: disable=redefined-outer-name

import kubernetes
import pytest
import yaml
from lambda_function import operations


@pytest.fixture(scope="session", autouse=True)
def kubeconfig():
    """Load kubecofig."""
    kubernetes.config.load_kube_config()


@pytest.fixture
def nginx_deployment():
    """Kubernetes deployment."""
    path = "tests/lambda_function/kubernetes_fixtures/nginx-deployment.yaml"
    with open(path) as in_file:
        deployment_dict = yaml.safe_load(in_file)
    namespace = "default"
    name = "nginx-deployment"

    yield deployment_dict, namespace, name

    apps_v1_api = kubernetes.client.AppsV1Api()
    apps_v1_api.delete_namespaced_deployment(namespace=namespace, name=name)


@pytest.mark.integration
def test_deployment_create(nginx_deployment):
    """
    GIVEN deployment as dictionary
    WHEN create is called with the deployment dictionary as a body
    THEN the deployment is created.
    """
    deployment_dict, namespace, name = nginx_deployment

    result = operations.create(body=deployment_dict)

    # Check result
    assert result.status == "SUCCESS"
    assert result.physical_name == f"{namespace}/{name}"
    # Check that the deployment is created
    apps_v1_api = kubernetes.client.AppsV1Api()
    response = apps_v1_api.list_namespaced_deployment(namespace=namespace)
    assert response.items
    assert response.items[0].metadata.name == name


@pytest.fixture
def namespace():
    """Kubernetes namespace."""
    path = "tests/lambda_function/kubernetes_fixtures/namespace.yaml"
    with open(path) as in_file:
        deployment_dict = yaml.safe_load(in_file)
    name = "namespace-1"

    yield deployment_dict, name

    core_v1_api = kubernetes.client.CoreV1Api()
    core_v1_api.delete_namespace(name=name)


@pytest.mark.integration
def test_namespace_create(namespace):
    """
    GIVEN namespace as dictionary
    WHEN create is called with the namespace dictionary as a body
    THEN the namespace is created.
    """
    namespace_dict, name = namespace

    result = operations.create(body=namespace_dict)

    # Check result
    assert result.status == "SUCCESS"
    assert result.physical_name == name
    # Check that the namespace is created
    core_v1_api = kubernetes.client.CoreV1Api()
    response = core_v1_api.list_namespace()
    assert response.items
    assert name in {item.metadata.name for item in response.items}
