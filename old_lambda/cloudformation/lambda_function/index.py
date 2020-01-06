"""Handles actioning kubernetes API calls."""

import json

import urllib3


def lambda_handler(event, context):
    """Handle events."""
    print({"event": str(event)})
    print({"context": str(context)})

    url = event["ResponseURL"]
    cfn_response = {
        "Status": "SUCCESS",
        "PhysicalResourceId": "test",
        "StackId": event["StackId"],
        "RequestId": event["RequestId"],
        "LogicalResourceId": event["LogicalResourceId"],
    }
    encoded_cfn_response = json.dumps(cfn_response).encode("utf-8")
    http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED")
    response = http.request("PUT", url, body=encoded_cfn_response)
    print(response.status)
    print(response.data)
