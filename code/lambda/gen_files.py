"""
This module contains the AWS Lambda function for generating Terraform configuration files.

The Lambda function defined in this module is triggered by AWS CloudFormation events. 
It handles the creation, update, and deletion of resources by generating the necessary Terraform 
configuration files and uploading them to an S3 bucket. The function's behavior is controlled by 
environment variables and the type of request received from CloudFormation.

Functions:
    handler(event, context): The main function that handles CloudFormation custom resource events.
"""
import os
import zipfile
import io
# pylint: disable=import-error
import boto3
import cfnresponse

def handler(event, context):
    """
    Handle Lambda function invocations for CloudFormation custom resources.

    This function processes CloudFormation custom resource events, generating 
    Terraform configuration files and uploading them to an S3 bucket, 
    depending on the environment variables and CloudFormation request type.

    Args:
        event (dict): The event passed by the AWS CloudFormation service, 
                      which includes details about the request type (Create, Update, Delete).
        context (LambdaContext): Provides runtime information about the Lambda function execution.

    Returns:
        None: The function sends a response directly to CloudFormation and does not return a value.
    """
    if event['RequestType'] == 'Delete':
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        return

    if event['RequestType'] == 'Update':
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
        return

    s3_client = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    aft_version = (
    "" if os.environ['AFT_VERSION'] == 'latest' 
    else f"?ref={os.environ['AFT_VERSION']}"
    )

    # Create in-memory zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

        # main.tf content
        main_tf_content = f'''
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

module "aft" {{
source = "github.com/aws-ia/terraform-aws-control_tower_account_factory{aft_version}"

# Required variables
ct_management_account_id  = "{os.environ['MANAGEMENT_ACCOUNT_ID']}"
log_archive_account_id    = "{os.environ['LOG_ARCHIVE_ACCOUNT_ID']}"
audit_account_id          = "{os.environ['AUDIT_ACCOUNT_ID']}"
aft_management_account_id = "{os.environ['AFT_ACCOUNT_ID']}"
ct_home_region            = "{os.environ['HOME_REGION']}"

# Optional variables
tf_backend_secondary_region = "{os.environ['SECONDARY_REGION']}"
aft_metrics_reporting       = "{os.environ['AFT_METRICS_REPORTING']}"

# AFT Feature flags
aft_feature_cloudtrail_data_events      = "{os.environ['AFT_FEATURE_CLOUDTRAIL_DATA_EVENTS']}"
aft_feature_enterprise_support          = "{os.environ['AFT_FEATURE_ENTERPRISE_SUPPORT']}"
aft_feature_delete_default_vpcs_enabled = "{os.environ['AFT_FEATURE_DELETE_DEFAULT_VPCS_ENABLED']}"

# Terraform variables
terraform_version      = "{os.environ['TERRAFORM_VERSION']}"
terraform_distribution = "OSS"
}}
        '''
        zip_file.writestr('terraform/main.tf', main_tf_content)

        # backend.tf content
        backend_tf_content = f'''
# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

terraform {{
backend "s3" {{
    bucket = "{bucket_name}"
    key    = "aft-setup"
    region = "{os.environ['REGION']}"
}}
}}
        '''
        zip_file.writestr('terraform/backend.tf', backend_tf_content)

    try:
        # Move the pointer of zip_buffer to the beginning of the buffer
        zip_buffer.seek(0)
        # Upload zip file
        s3_client.put_object(
            Bucket=bucket_name,
            Key='terraform_files.zip',
            Body=zip_buffer.getvalue()
        )


        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
    except Exception as e: # pylint: disable=broad-exception-caught
        print(e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {})
