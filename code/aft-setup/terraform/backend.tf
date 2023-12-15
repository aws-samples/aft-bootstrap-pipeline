# Copyright Amazon.com, Inc. or its affiliates. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

terraform {
  backend "s3" {
    bucket = "<bucket_name>"
    key    = "aft-setup"
    region = "<region>"
  }
}
