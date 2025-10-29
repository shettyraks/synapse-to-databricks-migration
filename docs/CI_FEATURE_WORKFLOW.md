# Feature Branch CI Workflow

This document describes the CI workflow for testing feature branches.

## Overview

The `ci-feature.yml` workflow provides comprehensive testing and validation for feature branches without requiring full environment deployment.

## Triggers

The workflow runs on:
- **Push** to branches matching `feature/**` pattern
- **Pull Requests** to `develop` or `main` branches
- **Specific triggers**:
  - Code changes in `src/`
  - Code changes in `modules/`
  - Code changes in `scripts/`
  - Workflow file changes

## Jobs

### 1. Lint and Validate
- **Purpose**: Code quality checks
- **Duration**: ~2-3 minutes
- **Checks**:
  - Python code linting with `flake8`
  - Code formatting validation with `black`
  - Type checking with `mypy`

### 2. Validate Python Notebooks
- **Purpose**: Ensure notebooks are syntactically correct
- **Duration**: ~1-2 minutes
- **Checks**:
  - Python syntax validation
  - Import consistency checks
  - File structure validation

### 3. Test Modules
- **Purpose**: Module import and basic functionality tests
- **Duration**: ~1 minute
- **Checks**:
  - Module imports work correctly
  - No circular import issues
  - Basic functionality available

### 4. Validate Configuration
- **Purpose**: Configuration file validation
- **Duration**: ~30 seconds
- **Checks**:
  - `config/customer_input.yml` structure
  - `databricks.yml` structure
  - Required fields present
  - Environment configurations valid

### 5. Summary
- **Purpose**: Provide CI status summary
- **Duration**: ~10 seconds
- **Output**: Summary in GitHub Actions UI

## Usage

### Running the Workflow

```bash
# Push to feature branch
git checkout feature/your-feature-name
git push origin feature/your-feature-name

# Create a pull request
gh pr create --base develop --head feature/your-feature-name
```

### Viewing Results

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select the workflow run
4. View individual job results

### Fixing Common Issues

#### Linting Errors
```bash
# Auto-format with black
black modules/ scripts/

# Fix flake8 issues
flake8 modules/ scripts/ --max-line-length=120
```

#### Import Errors
```bash
# Test module imports locally
python3 -c "from modules.config import ConfigManager"

# Check for circular imports
python3 -m py_compile modules/*.py
```

#### Configuration Errors
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/customer_input.yml'))"
```

## Benefits

- **Fast Feedback**: Tests run in ~5 minutes total
- **No Deployment Required**: Tests code quality without Databricks credentials
- **Early Detection**: Catch issues before merge
- **Consistent Standards**: Enforces code quality across branches
- **Safe to Fail**: Doesn't affect production deployments

## Comparison with Other Workflows

| Workflow | Purpose | Triggers | Duration |
|----------|---------|----------|----------|
| `ci-feature.yml` | Code quality checks | feature/** | ~5 min |
| `cd-dev.yml` | Deploy to dev | develop branch | ~10 min |
| `cd-prod.yml` | Deploy to prod | main branch | ~15 min |

## Extending the Workflow

### Adding New Checks

```yaml
new-check:
  name: Custom Check
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run custom check
      run: |
        # Your custom check here
```

### Adding Coverage Reporting

```yaml
coverage:
  name: Test Coverage
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run tests with coverage
      run: |
        pip install pytest pytest-cov
        pytest --cov=modules tests/
```

## Troubleshooting

### Workflow Not Triggering

Check:
- Branch name matches `feature/**`
- Files changed are in watched paths
- Workflow file is committed to the branch

### Jobs Failing

Common causes:
- Syntax errors in Python files
- Import errors
- Missing dependencies
- Configuration file issues

### Quick Fixes

```bash
# Run checks locally before pushing
pip install flake8 black mypy
flake8 modules/ scripts/
black --check modules/ scripts/
mypy modules/
```

## Reference

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [black Documentation](https://black.readthedocs.io/)
- [mypy Documentation](https://mypy.readthedocs.io/)

