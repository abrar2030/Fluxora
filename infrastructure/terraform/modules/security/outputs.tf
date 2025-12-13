# Simplified Security Module Outputs

output "app_security_group_id" {
  description = "ID of the application security group"
  value       = aws_security_group.app.id
}

output "db_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "ID of the cache security group"
  value       = aws_security_group.cache.id
}

output "admin_security_group_id" {
  description = "ID of the admin security group"
  value       = aws_security_group.admin.id
}

# Legacy compatibility outputs
output "web_tier_security_group_id" {
  description = "ID of the web tier security group (alias for app)"
  value       = aws_security_group.app.id
}

output "alb_security_group_id" {
  description = "ID of the ALB security group (alias for app)"
  value       = aws_security_group.app.id
}

output "bastion_security_group_id" {
  description = "ID of the bastion security group (alias for admin)"
  value       = aws_security_group.admin.id
}
