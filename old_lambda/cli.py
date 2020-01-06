"""Cli helpers."""

import boto3
import troposphere

import cloudformation


def main():
    """Create all resources."""
    template = troposphere.Template()
    for resource in cloudformation.RESOURCES:
        template.add_resource(resource)

    # Executing template
    stack_name = "cloudformation-kubernetes"
    session = boto3.Session(region_name="ap-southeast-2")
    cloudformation_client = session.client("cloudformation")
    cloudformation_client.update_stack(
        StackName=stack_name,
        TemplateBody=template.to_yaml(clean_up=True),
        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
    )
    cloudformation_client.get_waiter("stack_update_complete").wait(
        StackName=stack_name, WaiterConfig={"Delay": 5}
    )


if __name__ == "__main__":
    main()
