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

    operations.create(body=deployment_dict)

    # Check that the deployment is created
    apps_v1_api = kubernetes.client.AppsV1Api()
    response = apps_v1_api.list_namespaced_deployment(namespace=namespace)
    assert response.items
    assert response.items[0].metadata.name == name
