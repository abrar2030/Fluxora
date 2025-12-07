#!/bin/bash

# Linting and Fixing Script for Fluxora Project (Python, JavaScript, YAML, Terraform)
# Optimized, Enhanced, and Secured Version

set -euo pipefail # Exit on error, exit on unset variable, and fail on pipe errors

echo "----------------------------------------"
echo "Starting linting and fixing process for Fluxora..."
echo "----------------------------------------"

# --- Configuration ---
PYTHON_LINTERS="black isort flake8 pylint nbqa"
NPM_LINTERS="eslint prettier"

# Define directories to process
PYTHON_DIRECTORIES=(
  "code"
  "scripts"
  "notebooks"
)

JS_DIRECTORIES=(
  "mobile-frontend"
  "web-frontend"
)

YAML_DIRECTORIES=(
  "config"
  "infrastructure"
  "tools"
  ".github/workflows"
)

TERRAFORM_DIRECTORIES=(
  "infrastructure/terraform"
)

# --- Utility Functions ---

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
install_python_deps() {
  echo "Checking for Python linting tools..."
  if command_exists black; then
    echo "Python linters appear to be installed (found 'black'). Skipping installation."
    return 0
  fi

  echo "Installing/Updating Python linting tools: $PYTHON_LINTERS"
  if command_exists pip3; then
    # Use a temporary virtual environment for installation if possible, or install globally as a fallback
    if [ -z "${VIRTUAL_ENV}" ]; then
      echo "Warning: Not in a virtual environment. Installing globally. Consider using 'python3 -m venv venv' and 'source venv/bin/activate'."
    fi
    pip3 install --upgrade $PYTHON_LINTERS || {
      echo "Error: Failed to install Python dependencies. Check your pip3 installation and permissions."
      exit 1
    }
  else
    echo "Error: pip3 is required but not installed. Please install pip3."
    exit 1
  fi
}

# Function to install Node dependencies
install_node_deps() {
  echo "Checking for Node linting tools..."
  if command_exists eslint; then
    echo "Node linters appear to be installed (found 'eslint'). Skipping installation."
    return 0
  fi

  echo "Installing/Updating JavaScript linting tools: $NPM_LINTERS"
  if command_exists npm; then
    npm install -g $NPM_LINTERS || {
      echo "Error: Failed to install Node dependencies. Check your npm installation and permissions."
      exit 1
    }
  else
    echo "Error: npm is required but not installed. Please install Node.js and npm."
    exit 1
  fi
}

# --- Tool Availability Checks ---

TERRAFORM_AVAILABLE=false
if command_exists terraform; then
  echo "terraform is installed."
  TERRAFORM_AVAILABLE=true
else
  echo "Warning: terraform is not installed. Terraform validation will be limited."
fi

YAMLLINT_AVAILABLE=false
if command_exists yamllint; then
  echo "yamllint is installed."
  YAMLLINT_AVAILABLE=true
else
  echo "Warning: yamllint is not installed. YAML validation will be limited."
fi

# --- Dependency Installation ---
install_python_deps
install_node_deps

# --- Linting Process ---

# 1. Python Linting
echo "----------------------------------------"
echo "Running Python linting tools..."

# 1.1 Run Black (code formatter)
echo "Running Black code formatter..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Formatting Python files in $dir..."
    python3 -m black "$dir" || echo "Black encountered issues in $dir. Please review the above errors."
  else
    echo "Directory $dir not found. Skipping Black formatting for this directory."
  fi
done
echo "Black formatting completed."

# 1.2 Run isort (import sorter)
echo "Running isort to sort imports..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Sorting imports in Python files in $dir..."
    python3 -m isort "$dir" || echo "isort encountered issues in $dir. Please review the above errors."
  else
    echo "Directory $dir not found. Skipping isort for this directory."
  fi
done
echo "Import sorting completed."

# 1.3 Run flake8 (linter)
echo "Running flake8 linter..."
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting Python files in $dir with flake8..."
    python3 -m flake8 "$dir" || echo "Flake8 found issues in $dir. Please review the above warnings/errors."
  else
    echo "Directory $dir not found. Skipping flake8 for this directory."
  fi
done
echo "Flake8 linting completed."

# 1.4 Run pylint (more comprehensive linter)
echo "Running pylint for more comprehensive linting..."
# Note: The original script disabled many checks (C0111, C0103, C0303, W0621, C0301, W0612, W0611, R0913, R0914, R0915).
# This is maintained for compatibility, but a stricter configuration is recommended.
PYLINT_DISABLED_CHECKS="C0111,C0103,C0303,W0621,C0301,W0612,W0611,R0913,R0914,R0915"
for dir in "${PYTHON_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting Python files in $dir with pylint..."
    find "$dir" -type f -name "*.py" | xargs python3 -m pylint --disable=$PYLINT_DISABLED_CHECKS || echo "Pylint found issues in $dir. Please review the above warnings/errors."
  else
    echo "Directory $dir not found. Skipping pylint for this directory."
  fi
done
echo "Pylint linting completed."

# 1.5 Run linting on Jupyter notebooks
echo "Running linting on Jupyter notebooks..."
if [ -d "notebooks" ]; then
  echo "Formatting Jupyter notebooks with Black..."
  python3 -m nbqa black notebooks || echo "Black encountered issues with notebooks. Please review the above errors."

  echo "Sorting imports in Jupyter notebooks with isort..."
  python3 -m nbqa isort notebooks || echo "isort encountered issues with notebooks. Please review the above errors."

  echo "Linting Jupyter notebooks with flake8..."
  python3 -m nbqa flake8 notebooks || echo "flake8 found issues in notebooks. Please review the above warnings/errors."
else
  echo "Directory notebooks not found. Skipping notebook linting."
fi
echo "Jupyter notebook linting completed."

# 2. JavaScript/TypeScript Linting
echo "----------------------------------------"
echo "Running JavaScript/TypeScript linting tools..."

# 2.1 Create ESLint config if it doesn't exist (Original logic maintained)
if [ ! -f "eslint.config.js" ]; then
  echo "Creating ESLint configuration..."
  cat > eslint.config.js << 'EOF'
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    'react',
  ],
  rules: {
    'no-unused-vars': 'warn',
    'react/prop-types': 'off',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
EOF
fi

# 2.2 Create Prettier config if it doesn't exist (Original logic maintained)
if [ ! -f ".prettierrc.json" ]; then
  echo "Creating Prettier configuration..."
  cat > .prettierrc.json << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
EOF
fi

# 2.3 Run ESLint
echo "Running ESLint for JavaScript/TypeScript files..."
for dir in "${JS_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Linting JavaScript/TypeScript files in $dir with ESLint..."
    # Using npx to ensure the local version of eslint is used if available, otherwise the global one
    npx eslint "$dir" --ext .js,.jsx,.ts,.tsx --fix || echo "ESLint found issues in $dir. Please review the above warnings/errors."
  else
    echo "Directory $dir not found. Skipping ESLint for this directory."
  fi
done
echo "ESLint linting completed."

# 2.4 Run Prettier
echo "Running Prettier for JavaScript/TypeScript files..."
for dir in "${JS_DIRECTORIES[@]}"; do
  if [ -d "$dir" ]; then
    echo "Formatting JavaScript/TypeScript files in $dir with Prettier..."
    npx prettier --write "$dir/**/*.{js,jsx,ts,tsx}" || echo "Prettier encountered issues in $dir. Please review the above errors."
  else
    echo "Directory $dir not found. Skipping Prettier for this directory."
  fi
done
echo "Prettier formatting completed."

# 3. YAML Linting
echo "----------------------------------------"
echo "Running YAML linting tools..."

# 3.1 Run yamllint if available
if [ "$YAMLLINT_AVAILABLE" = true ]; then
  echo "Running yamllint for YAML files..."
  for dir in "${YAML_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      echo "Linting YAML files in $dir with yamllint..."
      yamllint "$dir" || echo "yamllint found issues in $dir. Please review the above warnings/errors."
    else
      echo "Directory $dir not found. Skipping yamllint for this directory."
    fi
  done
  echo "yamllint completed."
else
  echo "Skipping yamllint (not installed)."

  # 3.2 Basic YAML validation using Python
  echo "Performing basic YAML validation using Python..."
  # Install pyyaml only if needed for validation
  if ! python3 -c "import yaml" 2>/dev/null; then
    pip3 install --upgrade pyyaml
  fi

  for dir in "${YAML_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      echo "Validating YAML files in $dir..."
      find "$dir" -type f \( -name "*.yaml" -o -name "*.yml" \) -exec python3 -c "import yaml; yaml.safe_load(open('{}', 'r'))" \; || echo "YAML validation found issues in $dir. Please review the above errors."
    else
      echo "Directory $dir not found. Skipping YAML validation for this directory."
    fi
  done
  echo "Basic YAML validation completed."
fi

# 4. Terraform Linting
echo "----------------------------------------"
echo "Running Terraform linting tools..."

# 4.1 Run terraform fmt if available
if [ "$TERRAFORM_AVAILABLE" = true ]; then
  echo "Running terraform fmt for Terraform files..."
  for dir in "${TERRAFORM_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      echo "Formatting Terraform files in $dir..."
      terraform fmt -recursive "$dir" || echo "terraform fmt encountered issues in $dir. Please review the above errors."
    else
      echo "Directory $dir not found. Skipping terraform fmt for this directory."
    fi
  done
  echo "terraform fmt completed."

  # 4.2 Run terraform validate if available
  echo "Running terraform validate for Terraform files..."
  for dir in "${TERRAFORM_DIRECTORIES[@]}"; do
    if [ -d "$dir" ]; then
      echo "Validating Terraform files in $dir..."
      # Use a subshell to change directory and run commands
      (cd "$dir" && terraform init -backend=false && terraform validate) || echo "terraform validate encountered issues in $dir. Please review the above errors."
    else
      echo "Directory $dir not found. Skipping terraform validate for this directory."
    fi
  done
  echo "terraform validate completed."
else
  echo "Skipping Terraform linting (terraform not installed)."
fi

# 5. Common Fixes for All File Types
echo "----------------------------------------"
echo "Applying common fixes to all file types..."

# 5.1 Fix trailing whitespace
echo "Fixing trailing whitespace..."
FILE_TYPES="*.py,*.js,*.jsx,*.ts,*.tsx,*.yaml,*.yml,*.tf,*.tfvars"
EXCLUDE_PATHS="*/node_modules/* -not -path */venv/* -not -path */dist/*"
find . -type f \( $(echo $FILE_TYPES | sed 's/,/ -o -name /g' | sed 's/^/-name /') \) -not -path "$EXCLUDE_PATHS" -exec sed -i 's/[ \t]*$//' {} \;
echo "Fixed trailing whitespace."

# 5.2 Ensure newline at end of file
echo "Ensuring newline at end of files..."
find . -type f \( $(echo $FILE_TYPES | sed 's/,/ -o -name /g' | sed 's/^/-name /') \) -not -path "$EXCLUDE_PATHS" -exec sh -c '[ -n "$(tail -c1 "$1")" ] && echo "" >> "$1"' sh {} \;
echo "Ensured newline at end of files."

echo "----------------------------------------"
echo "Linting and fixing process for Fluxora completed!"
echo "----------------------------------------"
