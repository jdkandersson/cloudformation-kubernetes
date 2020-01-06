"""Resources for lambda function."""

import troposphere
from awacs import aws
from troposphere import awslambda
from troposphere import cloudformation
from troposphere import iam

_ROLE = iam.Role(
    title="LambdaRole",
    AssumeRolePolicyDocument=aws.PolicyDocument(
        Statement=[
            aws.Statement(
                Action=[aws.Action("sts", "AssumeRole")],
                Effect="Allow",
                Principal=aws.Principal(
                    principal="Service", resources=["lambda.amazonaws.com"]
                ),
            )
        ]
    ),
    ManagedPolicyArns=[
        "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    ],
    RoleName="cloudformation-kubernetes-lambda",
)

with open("cloudformation/lambda_function/index.py") as in_file:
    _CODE = awslambda.Code(ZipFile=in_file.read())
_LAMBDA = awslambda.Function(
    title="Lambda",
    Code=_CODE,
    Description="Custom CloudFormation handler for kubernetes API calls",
    FunctionName="cloudformation-kubernetes",
    Handler="index.lambda_handler",
    MemorySize=128,
    Role=troposphere.GetAtt(_ROLE, "Arn"),
    Runtime="python3.7",
    Timeout=900,
)

_CUSTOM = cloudformation.CustomResource(
    title="CustomResource",
    ServiceToken=troposphere.GetAtt(_LAMBDA, "Arn"),
    apiVersion="apps/v1",
    kind="Deployment",
    metadata={"name": "web-deployment", "labels": {"app": "web"}},
    spec={
        "replicas": 1,
        "selector": {"matchLabels": {"app": "web"}},
        "template": {
            "metadata": {
                "labels": {"app": "web"},
                "spec": {
                    "containers": [
                        {
                            "name": "web-container",
                            "image": "nginx:latest",
                            "ports": [{"containerPort": 80}],
                            "stdin": True,
                            "tty": True,
                        }
                    ]
                },
            }
        },
    },
)


RESOURCES = [_ROLE, _LAMBDA]
