# Secrets Management Module Outputs

# KMS Outputs
output "secrets_kms_key_id" {
  description = "ID of the KMS key for secrets encryption"
  value       = aws_kms_key.secrets.key_id
}

output "secrets_kms_key_arn" {
  description = "ARN of the KMS key for secrets encryption"
  value       = aws_kms_key.secrets.arn
}

output "secrets_kms_alias_name" {
  description = "Name of the KMS key alias for secrets"
  value       = aws_kms_alias.secrets.name
}

# Secrets Manager Outputs
output "db_master_secret_arn" {
  description = "ARN of the database master credentials secret"
  value       = aws_secretsmanager_secret.db_master_credentials.arn
}

output "db_master_secret_name" {
  description = "Name of the database master credentials secret"
  value       = aws_secretsmanager_secret.db_master_credentials.name
}

output "db_app_secret_arn" {
  description = "ARN of the database application credentials secret"
  value       = aws_secretsmanager_secret.db_app_credentials.arn
}

output "db_app_secret_name" {
  description = "Name of the database application credentials secret"
  value       = aws_secretsmanager_secret.db_app_credentials.name
}

output "redis_secret_arn" {
  description = "ARN of the Redis credentials secret"
  value       = aws_secretsmanager_secret.redis_credentials.arn
}

output "redis_secret_name" {
  description = "Name of the Redis credentials secret"
  value       = aws_secretsmanager_secret.redis_credentials.name
}

output "app_secrets_arn" {
  description = "ARN of the application secrets"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "app_secrets_name" {
  description = "Name of the application secrets"
  value       = aws_secretsmanager_secret.app_secrets.name
}

output "external_apis_secret_arn" {
  description = "ARN of the external APIs credentials secret"
  value       = aws_secretsmanager_secret.external_apis.arn
}

output "external_apis_secret_name" {
  description = "Name of the external APIs credentials secret"
  value       = aws_secretsmanager_secret.external_apis.name
}

output "ssl_certificates_secret_arn" {
  description = "ARN of the SSL certificates secret"
  value       = aws_secretsmanager_secret.ssl_certificates.arn
}

output "ssl_certificates_secret_name" {
  description = "Name of the SSL certificates secret"
  value       = aws_secretsmanager_secret.ssl_certificates.name
}

# IAM Outputs
output "secrets_access_role_arn" {
  description = "ARN of the secrets access IAM role"
  value       = aws_iam_role.secrets_access_role.arn
}

output "secrets_access_role_name" {
  description = "Name of the secrets access IAM role"
  value       = aws_iam_role.secrets_access_role.name
}

output "secrets_access_instance_profile_arn" {
  description = "ARN of the secrets access instance profile"
  value       = aws_iam_instance_profile.secrets_access_profile.arn
}

output "secrets_access_instance_profile_name" {
  description = "Name of the secrets access instance profile"
  value       = aws_iam_instance_profile.secrets_access_profile.name
}

output "secrets_rotation_role_arn" {
  description = "ARN of the secrets rotation IAM role"
  value       = aws_iam_role.secrets_rotation_role.arn
}

output "secrets_rotation_role_name" {
  description = "Name of the secrets rotation IAM role"
  value       = aws_iam_role.secrets_rotation_role.name
}

# Systems Manager Parameter Store Outputs
output "app_config_parameters" {
  description = "Map of application configuration parameter names and ARNs"
  value = {
    for key, param in aws_ssm_parameter.app_config : key => {
      name = param.name
      arn  = param.arn
      type = param.type
    }
  }
}

# Monitoring Outputs
output "secrets_access_log_group_name" {
  description = "Name of the CloudWatch log group for secrets access"
  value       = aws_cloudwatch_log_group.secrets_access_logs.name
}

output "secrets_access_log_group_arn" {
  description = "ARN of the CloudWatch log group for secrets access"
  value       = aws_cloudwatch_log_group.secrets_access_logs.arn
}

output "secrets_access_alarm_arn" {
  description = "ARN of the CloudWatch alarm for secrets access failures"
  value       = aws_cloudwatch_metric_alarm.secrets_access_failures.arn
}

# Backup Outputs
output "secrets_backup_vault_arn" {
  description = "ARN of the backup vault for secrets"
  value       = aws_backup_vault.secrets_backup.arn
}

output "secrets_backup_vault_name" {
  description = "Name of the backup vault for secrets"
  value       = aws_backup_vault.secrets_backup.name
}

# Security Configuration Summary
output "secrets_security_configuration" {
  description = "Summary of secrets security configuration"
  value = {
    encryption_enabled        = true
    kms_key_rotation_enabled = true
    cross_region_replication = true
    access_logging_enabled   = var.secrets_access_logging_enabled
    backup_enabled           = true
    rotation_enabled         = var.enable_secrets_rotation
    compliance_frameworks    = var.compliance_requirements
  }
}

# Access Configuration Summary
output "secrets_access_configuration" {
  description = "Summary of secrets access configuration"
  value = {
    iam_role_based_access    = true
    instance_profile_enabled = true
    parameter_store_enabled  = true
    cross_account_sharing    = var.secret_sharing_enabled
    ip_restrictions_enabled  = var.ip_restrictions.enabled
    time_based_access        = var.time_based_access.enabled
    audit_trail_enabled      = var.audit_trail_enabled
  }
}

# Secrets Inventory
output "secrets_inventory" {
  description = "Inventory of all managed secrets"
  value = {
    database_secrets = {
      master_credentials = aws_secretsmanager_secret.db_master_credentials.name
      app_credentials    = aws_secretsmanager_secret.db_app_credentials.name
    }
    cache_secrets = {
      redis_credentials = aws_secretsmanager_secret.redis_credentials.name
    }
    application_secrets = {
      app_secrets = aws_secretsmanager_secret.app_secrets.name
    }
    external_secrets = {
      api_credentials = aws_secretsmanager_secret.external_apis.name
    }
    ssl_secrets = {
      certificates = aws_secretsmanager_secret.ssl_certificates.name
    }
  }
}

# Compliance Status
output "compliance_status" {
  description = "Compliance status for secrets management"
  value = {
    pci_dss_compliant = var.compliance_requirements.pci_dss_required
    gdpr_compliant    = var.compliance_requirements.gdpr_required
    soc2_compliant    = var.compliance_requirements.soc2_required
    hipaa_compliant   = var.compliance_requirements.hipaa_required
    encryption_at_rest = true
    access_controls    = true
    audit_logging      = true
    backup_recovery    = true
  }
}

