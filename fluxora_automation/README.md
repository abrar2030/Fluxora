# Fluxora Automation Scripts

This directory contains a collection of automation scripts for the Fluxora repository. These scripts are designed to streamline common development, testing, and deployment tasks.

## Available Scripts

1. **setup_environment.sh** - Automates the setup of development environment prerequisites
2. **docker_manager.sh** - Simplifies Docker operations (build, start, stop, status)
3. **install_dependencies.sh** - Installs all required dependencies for different components
4. **start_services.sh** - Starts all required services in the correct order
5. **api_tester.sh** - Tests API endpoints and generates example requests
6. **monitoring_setup.sh** - Configures and launches the monitoring stack
7. **run_tests.sh** - Executes tests for different components with reporting
8. **dev_workflow.sh** - Automates common development tasks
9. **deploy.sh** - Streamlines the deployment process

## Usage

All scripts include detailed help information that can be accessed using the `-h` or `--help` flag:

```bash
./script_name.sh --help
```

### Common Options

Most scripts support the following options:

- `-d, --directory` - Specify the Fluxora project directory (default: current directory)
- `-h, --help` - Show help message

### Typical Workflow

1. Set up your environment:
   ```bash
   ./setup_environment.sh
   ```

2. Install dependencies:
   ```bash
   ./install_dependencies.sh
   ```

3. Start services:
   ```bash
   ./start_services.sh
   ```

4. Run tests:
   ```bash
   ./run_tests.sh
   ```

5. Use development workflow tools:
   ```bash
   ./dev_workflow.sh format-all
   ```

6. Deploy the application:
   ```bash
   ./deploy.sh -e dev
   ```

## Script Permissions

Make sure all scripts have execution permissions:

```bash
chmod +x *.sh
```

## Requirements

- Bash shell
- Git
- Docker and Docker Compose (for containerized operations)
- Python 3.9+ (for backend operations)
- Node.js 16+ (for frontend operations)

## Notes

- These scripts are designed to work with the Fluxora repository structure
- All scripts include error handling and detailed logging
- Scripts can be run individually or as part of a workflow
