# Contributing to Fluxora

Thank you for your interest in contributing to Fluxora! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites
- Git
- Python 3.x
- Node.js (for frontend development)
- DVC
- Make

### Setting Up Development Environment
1. Fork the repository
2. Clone your fork
3. Set up the development environment (see [Setup Guide](SETUP_GUIDE.md))
4. Create a new branch for your feature/fix

## Contribution Workflow

### 1. Creating a New Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix-name
```

### 2. Making Changes
- Follow the [Development Guidelines](DEVELOPMENT_GUIDELINES.md)
- Write clear, concise commit messages
- Include tests for new features
- Update documentation as needed

### 3. Testing
- Run all tests: `make test`
- Check code style: `make lint`
- Verify documentation builds: `make docs`

### 4. Submitting Changes
1. Push your branch to your fork
2. Create a Pull Request (PR)
3. Fill out the PR template
4. Request review from maintainers

## Code Review Process

### What to Expect
- Review within 48 hours
- Feedback on code quality
- Suggestions for improvements
- Discussion of implementation details

### Responding to Feedback
- Address all comments
- Make requested changes
- Keep the discussion professional
- Be open to suggestions

## Documentation

### Required Documentation
- Update relevant documentation
- Add comments for complex code
- Include examples where helpful
- Document breaking changes

### Documentation Standards
- Use Markdown format
- Follow existing style
- Include code examples
- Keep it concise and clear

## Testing Requirements

### Test Coverage
- Maintain 80%+ coverage
- Test edge cases
- Include integration tests
- Test error conditions

### Running Tests
```bash
# Run all tests
make test

# Run specific test
python -m pytest tests/path/to/test.py

# Run with coverage
make test-coverage
```

## Style Guide

### Code Style
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Follow project conventions
- Use consistent formatting

### Git Commit Messages
- Use present tense
- Start with type (feat, fix, docs, etc.)
- Keep first line under 50 chars
- Reference issues if applicable

## Feature Requests

### Submitting Feature Requests
1. Check existing issues
2. Create new issue
3. Use feature request template
4. Provide detailed description

### Feature Request Guidelines
- Explain the problem
- Describe the solution
- Provide use cases
- Consider alternatives

## Bug Reports

### Submitting Bug Reports
1. Check existing issues
2. Create new issue
3. Use bug report template
4. Include reproduction steps

### Bug Report Requirements
- Clear description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details

## Security Issues

### Reporting Security Issues
- Email security team
- Do not disclose publicly
- Include detailed report
- Follow responsible disclosure

### Security Response
- Acknowledge receipt
- Investigate promptly
- Provide updates
- Coordinate fix release

## Community Guidelines

### Code of Conduct
- Be respectful
- Be inclusive
- Be constructive
- Be professional

### Communication
- Use project channels
- Be clear and concise
- Be patient and helpful
- Follow community norms

## Additional Resources
- [Project Overview](PROJECT_OVERVIEW.md)
- [Development Guidelines](DEVELOPMENT_GUIDELINES.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md) 