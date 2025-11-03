# CI/CD Pipeline End User Guide
## Synapse-to-Databricks Migration Deployment

**Version:** 1.0  
**Last Updated:** November 2024  
**Document Type:** User Guide

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [Prerequisites](#prerequisites)
4. [Repository Setup](#repository-setup)
5. [Environment Configuration](#environment-configuration)
6. [GitHub Secrets Configuration](#github-secrets-configuration)
7. [Deployment Workflows](#deployment-workflows)
8. [How to Deploy](#how-to-deploy)
9. [Workflow Triggers](#workflow-triggers)
10. [Monitoring Deployments](#monitoring-deployments)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [Appendix](#appendix)

---

## 1. Introduction

This guide provides comprehensive instructions for using the CI/CD pipeline to deploy Databricks assets and SQL migrations across multiple environments (Development, SIT, UAT, and Production).

### Purpose

The CI/CD pipeline automates the deployment of:
- SQL schema migrations using Flyway
- Databricks notebooks and jobs
- Configuration files and environment-specific settings

### Target Audience

This guide is intended for:
- DevOps engineers
- Data engineers
- Release managers
- System administrators

---

## 2. Quick Start Guide

### Simple 5-Step Process

**Step 1: Write Code**
- Make changes to SQL files, notebooks, or configuration files
- Commit your changes using Git

**Step 2: Push to Branch**
- Push to `develop` branch → Automatically deploys to Development
- Push to `sit` branch → Automatically deploys to SIT
- For UAT/Production → Manual trigger required (see How to Deploy section)

**Step 3: Workflow Runs Automatically**
- GitHub Actions detects the push
- Installs required tools (Python, Flyway, Databricks CLI)
- Runs SQL migrations to create/update tables
- Deploys Databricks assets (notebooks, jobs, configurations)

**Step 4: Deployment Completes**
- SQL tables are created/updated in Databricks
- Notebooks and jobs are deployed
- Configuration is applied

**Step 5: Verify Deployment**
- Check GitHub Actions for deployment status
- Verify in Databricks workspace that assets are deployed

### Environment Selection Guide

| Environment | Branch | Trigger Type | Use Case |
|------------|--------|--------------|----------|
| **Development** | `develop` | Automatic or Manual | Quick testing and development |
| **SIT** | `sit` or `release/sit` | Automatic or Manual | System integration testing |
| **UAT** | `release/uat` | Manual Only | User acceptance testing |
| **Production** | `main` | Manual Only | Live production system |

### Key Points

- **Development & SIT**: Automatic deployment when you push code to the branch
- **UAT & Production**: Manual trigger only (for safety and control)
- **What Gets Deployed**: SQL migrations + Databricks assets (notebooks, jobs)
- **Failure Handling**: Check logs, fix issues, and retry deployment

---

## 3. Prerequisites

### Required Accounts and Access

- **GitHub Account** with access to the repository
- **Databricks Workspace Access** for each environment you need to deploy to
- **Permission to Configure GitHub Secrets** (if you need to set up secrets)

### Required Tools

- **Git** - Version control (for cloning and pushing code)
- **GitHub CLI** (optional) - For monitoring workflows via command line
- **Web Browser** - For accessing GitHub Actions and Databricks

### Required Knowledge

- Basic Git operations (clone, commit, push)
- Understanding of branch-based workflows
- Familiarity with Databricks concepts (workspaces, notebooks, jobs)

---

## 4. Repository Setup

### Repository Structure

```
synapse-to-databricks-migration/
├── .github/
│   └── workflows/
│       ├── cd-dev.yml      # Development workflow
│       ├── cd-sit.yml      # SIT workflow
│       ├── cd-uat.yml      # UAT workflow
│       └── cd-prod.yml    # Production workflow
├── config/
│   └── customer_input.yml # Environment configuration
├── scripts/
│   └── deploy-sql-migrations.sh # SQL migration script
├── src/                    # Source code and SQL files
└── databricks.yml         # Databricks bundle configuration
```

### Cloning the Repository

```bash
git clone https://github.com/shettyraks/synapse-to-databricks-migration.git
cd synapse-to-databricks-migration
```

---

## 5. Environment Configuration

### Environment Configuration File

The main configuration file is located at: `config/customer_input.yml`

This file contains settings for each environment (dev, sit, uat, prod).

#### Example Configuration

```yaml
environments:
  dev:
    customer: PANDs
    catalog: rio_cicd_setup_dev
    flyway_schema: pandas_flyway
    schemas:
      - inventory
      - masterdata
  
  sit:
    customer: PANDs
    catalog: rio_cicd_setup_sit
    flyway_schema: pandas_flyway
    schemas:
      - inventory
      - masterdata
  
  uat:
    customer: PANDs
    catalog: rio_cicd_setup_uat
    flyway_schema: pandas_flyway
    schemas:
      - inventory
      - masterdata
  
  prod:
    customer: PANDs
    catalog: rio_cicd_setup_prod
    flyway_schema: pandas_flyway
    schemas:
      - inventory
      - masterdata
```

### Configuration Parameters Explained

| Parameter | Description | Example |
|-----------|-------------|---------|
| `customer` | Customer identifier | `PANDs` |
| `catalog` | Databricks catalog name | `rio_cicd_setup_dev` |
| `flyway_schema` | Schema for Flyway metadata storage | `pandas_flyway` |
| `schemas` | List of schemas to deploy SQL migrations to | `[inventory, masterdata]` |

---

## 6. GitHub Secrets Configuration

### Overview

GitHub Secrets are secure environment variables stored in GitHub that are used during workflow execution. Each environment has its own set of secrets.

### Required Secrets by Environment

#### Development Environment

Navigate to: **GitHub Repository → Settings → Secrets and Variables → Actions → Environment: development**

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `DATABRICKS_HOST_DEV` | Databricks workspace URL | `adb-1234567890123.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN_DEV` | Personal Access Token | `dapi1234567890abcdef...` |
| `HTTP_PATH_DEV` | SQL Warehouse HTTP Path | `/sql/1.0/warehouses/1234567890abcdef` |
| `USER_DEV` | Database connection user | `token` |

#### SIT Environment

Navigate to: **GitHub Repository → Settings → Secrets and Variables → Actions → Environment: sit**

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `DATABRICKS_HOST_SIT` | Databricks workspace URL | `adb-1234567890123.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN_SIT` | Personal Access Token | `dapi1234567890abcdef...` |
| `HTTP_PATH_SIT` | SQL Warehouse HTTP Path | `/sql/1.0/warehouses/1234567890abcdef` |
| `USER_SIT` | Database connection user | `token` |

#### UAT Environment

Navigate to: **GitHub Repository → Settings → Secrets and Variables → Actions → Environment: uat**

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `DATABRICKS_HOST_UAT` | Databricks workspace URL | `adb-1234567890123.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN_UAT` | Personal Access Token | `dapi1234567890abcdef...` |
| `HTTP_PATH_UAT` | SQL Warehouse HTTP Path | `/sql/1.0/warehouses/1234567890abcdef` |
| `USER_UAT` | Database connection user | `token` |
| `PASSWORD_UAT` | Database password | Same as `DATABRICKS_TOKEN_UAT` |
| `SLACK_WEBHOOK` | (Optional) Slack notification URL | `https://hooks.slack.com/services/...` |

#### Production Environment

Navigate to: **GitHub Repository → Settings → Secrets and Variables → Actions → Environment: production**

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `DATABRICKS_HOST_PROD` | Databricks workspace URL | `adb-1234567890123.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN_PROD` | Personal Access Token | `dapi1234567890abcdef...` |
| `HTTP_PATH_PROD` | SQL Warehouse HTTP Path | `/sql/1.0/warehouses/1234567890abcdef` |
| `USER_PROD` | Database connection user | `token` |
| `PASSWORD_PROD` | Database password | Same as `DATABRICKS_TOKEN_PROD` |
| `SLACK_WEBHOOK` | (Optional) Slack notification URL | `https://hooks.slack.com/services/...` |

### How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and Variables** → **Actions**
3. Select the appropriate **Environment** (development, sit, uat, or production)
4. Click **New repository secret**
5. Enter the secret name (exactly as shown in the table above)
6. Enter the secret value
7. Click **Add secret**
8. Repeat for all required secrets for that environment

### Obtaining Databricks Credentials

#### Getting Databricks Host URL

1. Log in to your Databricks workspace
2. Copy the URL from your browser address bar
   - Example: `https://adb-1234567890123.7.azuredatabricks.net`
3. Remove `https://` prefix if present
   - Use: `adb-1234567890123.7.azuredatabricks.net`

#### Creating Personal Access Token

1. Log in to Databricks workspace
2. Click on your username in the top right corner
3. Select **User Settings** → **Access Tokens**
4. Click **Generate New Token**
5. Enter a description (e.g., "GitHub Actions CI/CD")
6. Set expiration period (recommended: 90 days or as per your policy)
7. Click **Generate**
8. **Copy the token immediately** - it won't be shown again
9. Store it securely and add it to GitHub Secrets

#### Getting SQL Warehouse HTTP Path

1. In Databricks, navigate to **SQL Warehouses**
2. Select your warehouse (or create one if needed)
3. Click on the warehouse name
4. Click on **Connection details** tab
5. Copy the **HTTP Path** value
   - Example: `/sql/1.0/warehouses/1234567890abcdef`

---

## 7. Deployment Workflows

### Available Workflows

| Workflow | File | Environment | Trigger Type |
|----------|------|-------------|--------------|
| Development | `cd-dev.yml` | Development | Automatic (push) / Manual |
| SIT | `cd-sit.yml` | SIT | Automatic (push) / Manual |
| UAT | `cd-uat.yml` | UAT | Manual Only |
| Production | `cd-prod.yml` | Production | Manual Only |

### Workflow Steps Explained

#### Development Workflow (`cd-dev.yml`)

**Triggers:**
- Push to `develop` branch (automatic)
- Manual workflow dispatch

**Steps:**
1. Checkout code from the repository
2. Set up Python 3.8 environment
3. Install Python dependencies from requirements.txt
4. Install Databricks CLI
5. Configure Databricks CLI with credentials
6. Install Java (required for Flyway)
7. Install Flyway (SQL migration tool)
8. Download Databricks JDBC Driver
9. Run SQL Migrations using Flyway
10. Deploy Databricks Assets (notebooks, jobs)
11. Deployment Complete

#### SIT Workflow (`cd-sit.yml`)

**Triggers:**
- Push to `sit` or `release/sit` branch (automatic)
- Manual workflow dispatch

**Steps:**
1. Checkout code from the repository
2. Set up Python 3.8 environment
3. Install Python dependencies from requirements.txt
4. Install Databricks CLI
5. Configure Databricks CLI with credentials
6. Install Java (required for Flyway)
7. Install Flyway (SQL migration tool)
8. Download Databricks JDBC Driver
9. Run SQL Migrations using Flyway
10. Deploy Databricks Assets with --force flag (for branch flexibility)
11. Deployment Complete

#### UAT Workflow (`cd-uat.yml`)

**Triggers:**
- Manual workflow dispatch only

**Steps:**
1. Checkout code from the repository
2. Set up Python 3.8 environment
3. Install Databricks CLI
4. Configure Databricks CLI with credentials
5. Deploy Databricks Assets
6. Run SQL Migrations
7. Validate Deployment
8. Run UAT Tests
9. Send Slack Notification (if configured)

#### Production Workflow (`cd-prod.yml`)

**Triggers:**
- Manual workflow dispatch only

**Steps:**
1. Checkout code from the repository
2. Set up Python 3.8 environment
3. Install Databricks CLI
4. Configure Databricks CLI with credentials
5. **Create Backup** (safety measure)
6. Deploy Databricks Assets
7. Run SQL Migrations
8. Validate Deployment
9. Run Smoke Tests
10. Send Slack Notification (if configured)

---

## 8. How to Deploy

### Method 1: Automatic Deployment (Development and SIT)

#### Development Environment

**Steps:**
1. Make your code changes
2. Commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```
3. Push to the develop branch:
   ```bash
   git push origin develop
   ```
4. The workflow will automatically trigger
5. Monitor the deployment in GitHub Actions

#### SIT Environment

**Steps:**
1. Make your code changes
2. Commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```
3. Push to the sit branch:
   ```bash
   git push origin sit
   ```
   OR push to release/sit:
   ```bash
   git push origin release/sit
   ```
4. The workflow will automatically trigger
5. Monitor the deployment in GitHub Actions

### Method 2: Manual Deployment (All Environments)

#### Using GitHub Web Interface

**Steps:**
1. Navigate to your GitHub repository
2. Click on the **Actions** tab
3. Select the workflow you want to run:
   - **Deploy to Development**
   - **Deploy to SIT**
   - **Deploy to UAT**
   - **Deploy to Production**
4. Click **Run workflow** button (on the right side)
5. Select the branch from the dropdown (if applicable)
6. Click **Run workflow**
7. Monitor the deployment progress

#### Using GitHub CLI

```bash
# Development
gh workflow run cd-dev.yml --ref develop

# SIT
gh workflow run cd-sit.yml --ref sit

# UAT
gh workflow run cd-uat.yml --ref release/uat

# Production
gh workflow run cd-prod.yml --ref main
```

### Deployment Checklist

Before deploying, ensure:

- [ ] All code changes are committed
- [ ] Appropriate branch is pushed to remote (for auto deployments)
- [ ] GitHub secrets are configured for the target environment
- [ ] Configuration file (`customer_input.yml`) is updated if needed
- [ ] SQL migrations are tested locally (if applicable)
- [ ] Databricks workspace is accessible
- [ ] You have necessary permissions for the target environment
- [ ] For Production: Backup procedures are understood

---

## 9. Workflow Triggers

### Automatic Triggers

These workflows trigger automatically when you push code:

| Environment | Branch | What Happens |
|------------|--------|--------------|
| Development | `develop` | Workflow starts automatically on push |
| SIT | `sit` or `release/sit` | Workflow starts automatically on push |

### Manual Triggers

These workflows must be triggered manually:

| Environment | How to Trigger |
|------------|----------------|
| Development | GitHub Actions → Run workflow → Select develop branch |
| SIT | GitHub Actions → Run workflow → Select sit branch |
| UAT | GitHub Actions → Run workflow → Select release/uat branch |
| Production | GitHub Actions → Run workflow → Select main branch |

### Important Notes

- **UAT and Production** workflows are **manual-only** for safety and control
- Always verify you're deploying to the correct environment
- Check that all required secrets are configured before triggering
- For Production: Ensure you have approval and backups are in place

---

## 10. Monitoring Deployments

### Using GitHub Web Interface

**Steps:**
1. Navigate to your GitHub repository
2. Click on the **Actions** tab
3. You'll see a list of workflow runs
4. Click on the workflow run you want to monitor
5. Click on the job name (e.g., `deploy-to-dev`)
6. Expand individual steps to see detailed logs
7. Green checkmarks indicate success, red X indicates failure

### Using GitHub CLI

```bash
# List recent workflow runs
gh run list --workflow=cd-dev.yml --limit 10

# View a specific run
gh run view <RUN_ID>

# Watch a running workflow in real-time
gh run watch <RUN_ID>

# View only failed logs
gh run view <RUN_ID> --log-failed
```

### What to Monitor

- **Setup Steps**: Ensure Python, dependencies, and tools are installed correctly
- **SQL Migrations**: Verify migrations complete without errors
- **Asset Deployment**: Confirm Databricks assets are deployed successfully
- **Validation Steps**: Check that validation passes (for UAT and Production)
- **Test Results**: Review test outputs (for UAT and Production)

### Monitoring Best Practices

- Monitor the workflow during initial deployments
- Check for failed steps and review error logs immediately
- Verify SQL migrations completed successfully
- Confirm Databricks assets are deployed in the workspace
- Validate deployment in the target Databricks environment
- For Production: Monitor closely and have rollback plan ready

---

## 11. Troubleshooting

### Common Issues and Solutions

#### Issue 1: Workflow Fails - Missing Secrets

**Symptoms:**
- Error message: `Required secret is not set`
- Workflow fails at configuration step
- Deployment cannot proceed

**Solution:**
1. Go to GitHub Repository → Settings → Secrets and Variables → Actions
2. Select the appropriate environment (development, sit, uat, or production)
3. Verify all required secrets are listed
4. Check secret names match exactly (they are case-sensitive)
5. Add any missing secrets
6. Retry the deployment

**Required Secrets Check:**
- Development: DATABRICKS_HOST_DEV, DATABRICKS_TOKEN_DEV, HTTP_PATH_DEV, USER_DEV
- SIT: DATABRICKS_HOST_SIT, DATABRICKS_TOKEN_SIT, HTTP_PATH_SIT, USER_SIT
- UAT: DATABRICKS_HOST_UAT, DATABRICKS_TOKEN_UAT, HTTP_PATH_UAT, USER_UAT, PASSWORD_UAT
- Production: DATABRICKS_HOST_PROD, DATABRICKS_TOKEN_PROD, HTTP_PATH_PROD, USER_PROD, PASSWORD_PROD

#### Issue 2: SQL Migration Fails

**Symptoms:**
- Error: `Connection property UID has invalid value`
- Error: `Connection property UID has invalid value of anonymous`
- Flyway migration fails during execution

**Solution:**
1. Verify `HTTP_PATH_<ENV>` secret is set correctly
   - Example: `/sql/1.0/warehouses/1234567890abcdef`
2. Verify `USER_<ENV>` secret is set to exactly `token` (all lowercase)
3. Check that your Databricks workspace is accessible
4. Verify SQL Warehouse is running in Databricks
5. Check SQL Warehouse connection details match the HTTP_PATH secret
6. Retry the deployment after fixing the secrets

#### Issue 3: Branch Mismatch Error

**Symptoms:**
- Error: `not on the right Git branch`
- Error: `expected according to configuration: release/sit`
- Error: `actual: sit`

**Solution:**
- **For SIT**: The workflow automatically uses `--force` flag, so this should not occur
- **For other environments**: Ensure you're deploying from the correct branch
  - UAT: Use `release/uat` branch
  - Production: Use `main` branch
- Check `databricks.yml` file for branch configuration if issues persist

#### Issue 4: Databricks Authentication Fails

**Symptoms:**
- Error: `Unauthorized`
- Error: `Invalid token`
- Databricks CLI configuration fails

**Solution:**
1. Verify `DATABRICKS_TOKEN_<ENV>` is valid and not expired
2. Check token hasn't expired (tokens have expiration dates)
3. Ensure token has necessary permissions:
   - Workspace access
   - SQL warehouse access
   - Job creation/modification permissions
4. Generate a new token if needed:
   - Databricks → User Settings → Access Tokens → Generate New Token
5. Update the secret in GitHub with the new token
6. Retry the deployment

#### Issue 5: Flyway Installation Fails

**Symptoms:**
- Error: `Flyway installation failed`
- Java installation issues
- Workflow fails during Flyway setup

**Solution:**
1. The workflow automatically installs Java - check logs for specific errors
2. If issues persist, check workflow logs for:
   - Disk space issues
   - Network connectivity problems
   - Package manager errors
3. Contact DevOps team if the issue persists, as this is usually an infrastructure problem

### General Troubleshooting Steps

1. **Check Workflow Logs**: Always start by examining the failed step logs
2. **Verify Secrets**: Ensure all required secrets are configured correctly
3. **Check Configuration**: Verify `customer_input.yml` and `databricks.yml` are correct
4. **Test Connectivity**: Verify Databricks workspace is accessible
5. **Review Error Messages**: Error messages usually indicate the specific issue
6. **Contact Support**: If issues persist, contact DevOps team with:
   - Workflow run ID
   - Error message
   - Step that failed
   - Screenshots if available

---

## 12. Best Practices

### Before Deployment

1. **Code Review**: Ensure all changes are reviewed by team members
2. **Testing**: Test changes in development environment first
3. **Documentation**: Update documentation for new features or changes
4. **Backup**: Understand backup procedures, especially for production
5. **Communication**: Inform team members about planned deployments

### During Deployment

1. **Monitor Progress**: Watch workflow execution in real-time
2. **Verify Steps**: Confirm each step completes successfully before proceeding
3. **Check Logs**: Review logs for warnings or errors
4. **Validate**: Verify deployment in target environment
5. **Don't Interrupt**: Avoid canceling workflows unless necessary

### After Deployment

1. **Smoke Tests**: Run smoke tests (especially for production)
2. **Validate**: Verify SQL migrations and assets are deployed correctly
3. **Document**: Document any issues encountered or changes made
4. **Communicate**: Notify team of deployment status (success or failure)
5. **Monitor**: Continue monitoring for a period after deployment

### Branch Management

- **develop**: Use for development testing and feature development
- **sit**: Use for SIT environment testing and integration testing
- **release/uat**: Use for UAT environment (manual deployment only)
- **main**: Use for production (manual deployment only, requires approval)

### Security Best Practices

- **Never commit secrets**: Never commit passwords, tokens, or secrets to the repository
- **Use GitHub Secrets**: Always use GitHub Secrets for sensitive data
- **Rotate tokens**: Rotate Databricks tokens regularly
- **Limit access**: Limit access to production secrets to authorized personnel only
- **Environment-specific secrets**: Use different secrets for each environment
- **Review permissions**: Regularly review who has access to GitHub secrets

### Rollback Procedures

If deployment fails or causes issues:

1. **SQL Migrations**: Flyway tracks migration history - you can rollback migrations
2. **Databricks Assets**: Previous versions are maintained - redeploy previous version
3. **Manual Rollback**: Use previous Git commit and redeploy
4. **Database Restore**: Use backups for critical production issues
5. **Contact DevOps**: For complex rollback scenarios, contact DevOps team

---

## 13. Appendix

### A. Environment Summary

| Environment | Branch | Trigger Type | Auto Backup | Smoke Tests |
|------------|--------|--------------|-------------|-------------|
| Development | `develop` | Auto/Manual | No | No |
| SIT | `sit` / `release/sit` | Auto/Manual | No | No |
| UAT | `release/uat` | Manual Only | No | Yes |
| Production | `main` | Manual Only | Yes | Yes |

### B. Required Secrets Summary

**Development Environment:**
- DATABRICKS_HOST_DEV
- DATABRICKS_TOKEN_DEV
- HTTP_PATH_DEV
- USER_DEV

**SIT Environment:**
- DATABRICKS_HOST_SIT
- DATABRICKS_TOKEN_SIT
- HTTP_PATH_SIT
- USER_SIT

**UAT Environment:**
- DATABRICKS_HOST_UAT
- DATABRICKS_TOKEN_UAT
- HTTP_PATH_UAT
- USER_UAT
- PASSWORD_UAT
- SLACK_WEBHOOK (optional)

**Production Environment:**
- DATABRICKS_HOST_PROD
- DATABRICKS_TOKEN_PROD
- HTTP_PATH_PROD
- USER_PROD
- PASSWORD_PROD
- SLACK_WEBHOOK (optional)

### C. Quick Reference Commands

```bash
# Clone repository
git clone https://github.com/shettyraks/synapse-to-databricks-migration.git

# Check workflow status
gh run list --workflow=cd-dev.yml --limit 5

# View workflow logs
gh run view <RUN_ID> --log-failed

# Trigger workflow manually
gh workflow run cd-dev.yml --ref develop

# Check secrets (requires GitHub CLI with proper permissions)
gh secret list
```

### D. Workflow File Locations

- Development: `.github/workflows/cd-dev.yml`
- SIT: `.github/workflows/cd-sit.yml`
- UAT: `.github/workflows/cd-uat.yml`
- Production: `.github/workflows/cd-prod.yml`

### E. Configuration Files

- Environment Config: `config/customer_input.yml`
- Databricks Config: `databricks.yml`
- SQL Migrations: `src/*/sql_deployment/`

### F. Support Contacts

For issues or questions:
- GitHub Issues: Create an issue in the repository
- DevOps Team: Contact through Slack channel
- Documentation: Check repository README.md

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | November 2024 | DevOps Team | Initial release |

---

**End of Document**
