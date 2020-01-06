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
def nginx_deployment_info():
    """Kubernetes deployment information."""
    path = "tests/lambda_function/kubernetes_fixtures/nginx-deployment.yaml"
    with open(path) as in_file:
        deployment_dict = yaml.safe_load(in_file)
    namespace = "default"
    name = "nginx-deployment"

    yield deployment_dict, namespace, name

    apps_v1_api = kubernetes.client.AppsV1Api()
    if apps_v1_api.list_namespaced_deployment(namespace=namespace).items:
        apps_v1_api.delete_namespaced_deployment(namespace=namespace, name=name)


@pytest.mark.integration
def test_deployment_create(nginx_deployment_info):
    """
    GIVEN deployment as dictionary
    WHEN create is called with the deployment dictionary as a body
    THEN the deployment is created.
    """
    deployment_dict, namespace, name = nginx_deployment_info

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
def _nginx_deployment(nginx_deployment_info):
    """Create Kubernetes deployment."""
    deployment_dict, _namespace, _name = nginx_deployment_info
    result = operations.create(body=deployment_dict)

    assert result.status == "SUCCESS"


@pytest.mark.integration
def test_deployment_update(nginx_deployment_info, _nginx_deployment):
    """
    GIVEN deployment as dictionary that has been created
    WHEN a label is added to the deployment and update is called with the deployment
        dictionary as a body and physical name
    THEN the deployment is updated.
    """
    deployment_dict, namespace, name = nginx_deployment_info
    deployment_dict["metadata"]["labels"] = {"key": "value"}

    result = operations.update(
        body=deployment_dict, physical_name=f"{namespace}/{name}"
    )

    # Check result
    assert result.status == "SUCCESS"
    # Check that the deployment is updated
    apps_v1_api = kubernetes.client.AppsV1Api()
    response = apps_v1_api.list_namespaced_deployment(namespace=namespace)
    assert response.items
    assert response.items[0].metadata.name == name
    assert response.items[0].metadata.labels["key"] == "value"


@pytest.mark.integration
def test_deployment_delete(nginx_deployment_info, _nginx_deployment):
    """
    GIVEN deployment as dictionary that has been created
    WHEN delete is called with the deployment dictionary as a body and physical name
    THEN the deployment is deleted.
    """
    deployment_dict, namespace, name = nginx_deployment_info

    result = operations.delete(
        body=deployment_dict, physical_name=f"{namespace}/{name}"
    )

    # Check result
    assert result.status == "SUCCESS"
    # Check that the deployment is deleted
    apps_v1_api = kubernetes.client.AppsV1Api()
    response = apps_v1_api.list_namespaced_deployment(namespace=namespace)
    assert not response.items


@pytest.fixture
def cluster_role_info():
    """Kubernetes cluster role."""
    path = "tests/lambda_function/kubernetes_fixtures/cluster-role.yaml"
    with open(path) as in_file:
        cluster_role_dict = yaml.safe_load(in_file)
    name = "cluster-role-1"

    yield cluster_role_dict, name

    rbac_v1_api = kubernetes.client.RbacAuthorizationV1Api()
    response = rbac_v1_api.list_cluster_role()
    name_mapping = {item.metadata.name for item in response.items}
    if name in name_mapping:
        rbac_v1_api.delete_cluster_role(name=name)


@pytest.mark.integration
def test_cluster_role_create(cluster_role_info):
    """
    GIVEN cluster role as dictionary
    WHEN create is called with the cluster role dictionary as a body
    THEN the cluster role is created.
    """
    cluster_role_dict, name = cluster_role_info

    result = operations.create(body=cluster_role_dict)

    # Check result
    assert result.status == "SUCCESS"
    assert result.physical_name == name
    # Check that the cluster role is created
    rbac_v1_api = kubernetes.client.RbacAuthorizationV1Api()
    response = rbac_v1_api.list_cluster_role()
    assert response.items
    assert name in {item.metadata.name for item in response.items}


@pytest.fixture
def _cluster_role(cluster_role_info):
    """Create Kubernetes cluster role."""
    cluster_role_dict, _name = cluster_role_info
    result = operations.create(body=cluster_role_dict)

    assert result.status == "SUCCESS"


@pytest.mark.integration
def test_cluster_role_update(cluster_role_info, _cluster_role):
    """
    GIVEN cluster role as dictionary that has been created
    WHEN a label is added to the cluster role and update is called with the cluster role
        dictionary as a body and physical name
    THEN the cluster role is updated.
    """
    cluster_role_dict, name = cluster_role_info
    cluster_role_dict["metadata"]["labels"] = {"key": "value"}

    result = operations.update(body=cluster_role_dict, physical_name=name)

    # Check result
    assert result.status == "SUCCESS"
    # Check that the cluster_role is created
    rbac_v1_api = kubernetes.client.RbacAuthorizationV1Api()
    response = rbac_v1_api.list_cluster_role()
    assert response.items
    metadata_dict = {item.metadata.name: item.metadata for item in response.items}
    assert name in metadata_dict
    assert metadata_dict[name].labels["key"] == "value"


@pytest.mark.integration
def test_cluster_role_delete(cluster_role_info, _cluster_role):
    """
    GIVEN cluster role as dictionary that has been created
    WHEN delete is called with the cluster role dictionary as a body and physical name
    THEN the cluster role is deleted.
    """
    cluster_role_dict, name = cluster_role_info

    result = operations.delete(body=cluster_role_dict, physical_name=name)

    # Check result
    assert result.status == "SUCCESS"
    # Check that the cluster_role is created
    rbac_v1_api = kubernetes.client.RbacAuthorizationV1Api()
    response = rbac_v1_api.list_cluster_role()
    assert response.items
    assert name not in {item.metadata.name for item in response.items}
