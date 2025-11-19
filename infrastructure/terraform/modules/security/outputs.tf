# Enhanced Security Module Outputs for Financial Standards Compliance

# Security Group Outputs
output "web_tier_security_group_id" {
  description = "ID of the web tier security group"
  value       = aws_security_group.web_tier.id
}

output "alb_security_group_id" {
  description = "ID of the Application Load Balancer security group"
  value       = aws_security_group.alb.id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "ID of the cache security group"
  value       = aws_security_group.cache.id
}

output "bastion_security_group_id" {
  description = "ID of the bastion host security group"
  value       = aws_security_group.bastion.id
}

# KMS Outputs
output "kms_key_id" {
  description = "ID of the KMS key for encryption"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  value       = aws_kms_key.main.arn
}

output "kms_alias_name" {
  description = "Name of the KMS key alias"
  value       = aws_kms_alias.main.name
}

# WAF Outputs
output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.id
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

# CloudTrail Outputs
output "cloudtrail_arn" {
  description = "ARN of the CloudTrail"
  value       = aws_cloudtrail.main.arn
}

output "cloudtrail_home_region" {
  description = "Home region of the CloudTrail"
  value       = aws_cloudtrail.main.home_region
}

# S3 Bucket Outputs
output "cloudtrail_logs_bucket_id" {
  description = "ID of the CloudTrail logs S3 bucket"
  value       = aws_s3_bucket.cloudtrail_logs.id
}

output "cloudtrail_logs_bucket_arn" {
  description = "ARN of the CloudTrail logs S3 bucket"
  value       = aws_s3_bucket.cloudtrail_logs.arn
}

output "app_data_bucket_id" {
  description = "ID of the application data S3 bucket"
  value       = aws_s3_bucket.app_data.id
}

output "app_data_bucket_arn" {
  description = "ARN of the application data S3 bucket"
  value       = aws_s3_bucket.app_data.arn
}

output "config_logs_bucket_id" {
  description = "ID of the Config logs S3 bucket"
  value       = aws_s3_bucket.config_logs.id
}

output "config_logs_bucket_arn" {
  description = "ARN of the Config logs S3 bucket"
  value       = aws_s3_bucket.config_logs.arn
}

# IAM Outputs
output "ec2_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2_role.arn
}

output "ec2_instance_profile_name" {
  description = "Name of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "ec2_instance_profile_arn" {
  description = "ARN of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.arn
}

output "config_role_arn" {
  description = "ARN of the Config service role"
  value       = aws_iam_role.config_role.arn
}

# Security Service Outputs
output "guardduty_detector_id" {
  description = "ID of the GuardDuty detector"
  value       = aws_guardduty_detector.main.id
}

output "security_hub_account_id" {
  description = "Security Hub account ID"
  value       = aws_securityhub_account.main.id
}

output "config_recorder_name" {
  description = "Name of the Config recorder"
  value       = aws_config_configuration_recorder.main.name
}

output "config_delivery_channel_name" {
  description = "Name of the Config delivery channel"
  value       = aws_config_delivery_channel.main.name
}

# Compliance and Audit Outputs
output "compliance_status" {
  description = "Compliance framework status"
  value = {
    pci_dss_enabled     = var.compliance_framework.pci_dss
    gdpr_enabled        = var.compliance_framework.gdpr
    soc2_enabled        = var.compliance_framework.soc2
    hipaa_enabled       = var.compliance_framework.hipaa
    encryption_at_rest  = var.encryption_at_rest_required
    encryption_in_transit = var.encryption_in_transit_required
    audit_logging       = true
    threat_detection    = var.enable_guardduty
    vulnerability_scanning = var.enable_inspector
  }
}

output "security_endpoints" {
  description = "Security service endpoints and configurations"
  value = {
    waf_endpoint        = aws_wafv2_web_acl.main.arn
    cloudtrail_endpoint = aws_cloudtrail.main.arn
    guardduty_endpoint  = aws_guardduty_detector.main.id
    config_endpoint     = aws_config_configuration_recorder.main.name
    kms_endpoint        = aws_kms_key.main.arn
  }
}

output "audit_trail_configuration" {
  description = "Audit trail configuration details"
  value = {
    cloudtrail_enabled     = true
    multi_region_enabled   = var.enable_multi_region_trail
    log_file_validation    = true
    kms_encryption_enabled = true
    s3_bucket_logging      = aws_s3_bucket.cloudtrail_logs.id
    retention_period       = var.cloudtrail_log_retention_days
  }
}

output "network_security_configuration" {
  description = "Network security configuration summary"
  value = {
    waf_enabled           = true
    security_groups_count = 5
    network_segmentation  = var.network_segmentation_enabled
    bastion_host_enabled  = true
    private_subnets_only  = true
  }
}

output "data_protection_configuration" {
  description = "Data protection configuration summary"
  value = {
    encryption_at_rest_enabled    = var.encryption_at_rest_required
    encryption_in_transit_enabled = var.encryption_in_transit_required
    kms_key_rotation_enabled      = true
    s3_versioning_enabled         = true
    s3_public_access_blocked      = true
    backup_retention_days         = var.backup_retention_period
  }
}
