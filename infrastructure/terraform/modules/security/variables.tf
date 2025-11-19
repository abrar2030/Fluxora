# Enhanced Security Module Variables for Financial Standards Compliance

variable "app_name" {
  description = "Name of the application"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_id" {
  description = "ID of the VPC where security groups will be created"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "admin_cidr_blocks" {
  description = "List of CIDR blocks allowed for administrative access"
  type        = list(string)
  validation {
    condition     = length(var.admin_cidr_blocks) > 0
    error_message = "At least one admin CIDR block must be specified."
  }
}

variable "common_tags" {
  description = "Common tags to be applied to all resources"
  type        = map(string)
  default = {
    Project     = "fluxora"
    ManagedBy   = "terraform"
    Compliance  = "pci-dss,gdpr,soc2"
  }
}

variable "kms_deletion_window" {
  description = "Number of days before KMS key deletion (7-30)"
  type        = number
  default     = 30
  validation {
    condition     = var.kms_deletion_window >= 7 && var.kms_deletion_window <= 30
    error_message = "KMS deletion window must be between 7 and 30 days."
  }
}

variable "waf_rate_limit" {
  description = "Rate limit for WAF (requests per 5 minutes)"
  type        = number
  default     = 2000
  validation {
    condition     = var.waf_rate_limit >= 100 && var.waf_rate_limit <= 20000000
    error_message = "WAF rate limit must be between 100 and 20,000,000."
  }
}

variable "enable_guardduty" {
  description = "Enable GuardDuty threat detection"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable Security Hub for centralized security findings"
  type        = bool
  default     = true
}

variable "enable_inspector" {
  description = "Enable Inspector for vulnerability assessment"
  type        = bool
  default     = true
}

variable "cloudtrail_log_retention_days" {
  description = "Number of days to retain CloudTrail logs"
  type        = number
  default     = 90
  validation {
    condition     = var.cloudtrail_log_retention_days >= 30
    error_message = "CloudTrail log retention must be at least 30 days for compliance."
  }
}

variable "enable_multi_region_trail" {
  description = "Enable multi-region CloudTrail"
  type        = bool
  default     = true
}

variable "s3_force_destroy" {
  description = "Allow force destroy of S3 buckets (should be false for production)"
  type        = bool
  default     = false
}

variable "database_port" {
  description = "Port number for database connections"
  type        = number
  default     = 3306
}

variable "cache_port" {
  description = "Port number for cache connections"
  type        = number
  default     = 6379
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 30
  validation {
    condition     = var.backup_retention_period >= 7
    error_message = "Backup retention period must be at least 7 days."
  }
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for critical resources"
  type        = bool
  default     = true
}

variable "monitoring_endpoints" {
  description = "List of monitoring service endpoints that need access"
  type        = list(string)
  default     = []
}

variable "compliance_framework" {
  description = "Compliance framework requirements"
  type        = object({
    pci_dss = bool
    gdpr    = bool
    soc2    = bool
    hipaa   = bool
  })
  default = {
    pci_dss = true
    gdpr    = true
    soc2    = true
    hipaa   = false
  }
}

variable "encryption_at_rest_required" {
  description = "Require encryption at rest for all storage"
  type        = bool
  default     = true
}

variable "encryption_in_transit_required" {
  description = "Require encryption in transit for all communications"
  type        = bool
  default     = true
}

variable "network_segmentation_enabled" {
  description = "Enable strict network segmentation"
  type        = bool
  default     = true
}

variable "audit_log_destinations" {
  description = "List of destinations for audit logs"
  type        = list(object({
    type     = string
    endpoint = string
  }))
  default = []
}

variable "incident_response_contacts" {
  description = "List of contacts for incident response"
  type        = list(object({
    name  = string
    email = string
    role  = string
  }))
  default = []
}

variable "data_classification_levels" {
  description = "Data classification levels and their requirements"
  type        = map(object({
    encryption_required = bool
    access_logging     = bool
    retention_days     = number
  }))
  default = {
    public = {
      encryption_required = false
      access_logging     = false
      retention_days     = 30
    }
    internal = {
      encryption_required = true
      access_logging     = true
      retention_days     = 90
    }
    confidential = {
      encryption_required = true
      access_logging     = true
      retention_days     = 365
    }
    restricted = {
      encryption_required = true
      access_logging     = true
      retention_days     = 2555  # 7 years
    }
  }
}
