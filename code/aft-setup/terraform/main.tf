# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

module "aft" {
  source = "github.com/aws-ia/terraform-aws-control_tower_account_factory"

  # Required variables
  ct_management_account_id  = "<ct_management_account_id>"
  log_archive_account_id    = "<log_archive_account_id>"
  audit_account_id          = "<audit_account_id>"
  aft_management_account_id = "<aft_management_account_id>"
  ct_home_region            = "<ct_home_region>"

  # Optional variables
  tf_backend_secondary_region = "<tf_backend_secondary_region>"
  aft_metrics_reporting       = "<false|true>"

  # AFT Feature flags
  aft_feature_cloudtrail_data_events      = "<false|true>"
  aft_feature_enterprise_support          = "<false|true>"
  aft_feature_delete_default_vpcs_enabled = "<false|true>"

  # Terraform variables
  terraform_version      = "<terraform_version>"
  terraform_distribution = "<terraform_distribution>"

  # VCS variables (only if you are not using AWS CodeCommit)
  # vcs_provider                                  = "<github|githubenterprise|gitlab|gitlabselfmanaged|bitbucket>"
  # account_request_repo_name                     = "<org-name>/aft-account-request"
  # account_customizations_repo_name              = "<org-name>/aft-account-customizations"
  # account_provisioning_customizations_repo_name = "<org-name>/aft-account-provisioning-customizations"
  # global_customizations_repo_name               = "<org-name>/aft-global-customizations"

}
