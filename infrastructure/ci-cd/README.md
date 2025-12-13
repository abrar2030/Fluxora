# CI/CD Pipeline Configuration

## GitHub Actions Pipeline

The main GitHub Actions pipeline is defined in `github-actions-pipeline.yml`.

### Required Secrets

Configure the following secrets in your GitHub repository settings:

- `AWS_ACCESS_KEY_ID` - AWS access key for deployments
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `K8S_CONFIG` - Base64 encoded Kubernetes config
- `SLACK_WEBHOOK` - Slack webhook for notifications

### Running Locally

To test the pipeline locally using `act`:

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run workflow
act push --secret-file .secrets
```

### Validation Steps

The pipeline includes:

1. **Terraform Validation**
   - `terraform fmt -check`
   - `terraform validate`
   - `tfsec` security scanning

2. **Kubernetes Validation**
   - `yamllint` for YAML syntax
   - `kubeval` for schema validation
   - Resource limit checks

3. **Ansible Validation**
   - `ansible-lint` for playbook quality
   - Syntax checking

4. **Security Scanning**
   - Container image scanning
   - Dependency vulnerability checks
   - Secret detection
