# Tag-Based Deployment Guide

This guide explains how to use tag-based deployments for the Databricks migration pipeline.

## Overview

The deployment system supports two tag-based deployment methods:

1. **Unified Tag-Based Workflow** (`cd-tag-based.yml`) - Automatically detects environment from tag name
2. **Environment-Specific Workflows** (`cd-dev.yml`, `cd-sit.yml`, `cd-uat.yml`, `cd-prod.yml`) - Tag triggers for specific environments

## Tag Naming Convention

Tags must follow one of these patterns to trigger deployments:

### Format 1: `*-{env}-deploy_now`
- `v1.0.0-dev-deploy_now` - Deploy to dev
- `v1.0.0-sit-deploy_now` - Deploy to sit
- `v1.0.0-uat-deploy_now` - Deploy to uat
- `v1.0.0-prod-deploy_now` - Deploy to prod

### Format 2: `*-{env}-deploy-now`
- `release-dev-deploy-now`
- `release-sit-deploy-now`
- `release-uat-deploy-now`
- `release-prod-deploy-now`

### Format 3: `*_{env}_deploy_now`
- `v1.0.0_dev_deploy_now`
- `v1.0.0_sit_deploy_now`

## Unified Tag-Based Workflow

The `cd-tag-based.yml` workflow automatically extracts the environment from the tag name.

### Automatic Trigger (Push Tag)

```bash
# Create and push a tag
git tag v1.0.0-dev-deploy_now
git push origin v1.0.0-dev-deploy_now
```

The workflow will:
1. Extract `dev` from the tag name
2. Checkout the tagged commit
3. Deploy to the dev environment

### Manual Trigger (Workflow Dispatch)

1. Go to GitHub Actions → "Tag-Based Deployment" workflow
2. Click "Run workflow"
3. Fill in:
   - **Tag name**: `v1.0.0-dev-deploy_now` (or any tag ending with `-deploy_now`)
   - **Environment**: `auto` (extracts from tag) or select specific environment

## Environment-Specific Workflows

Each environment has its own workflow that can be triggered by:

1. **Branch push** (original method)
   - `develop` → dev
   - `release/sit` → sit
   - `release/uat` → uat
   - `main` → prod

2. **Tag push** (tag-based)
   - Tags ending with `-{env}-deploy_now`
   - Example: `v1.0.0-dev-deploy_now` triggers dev deployment

3. **Manual dispatch** (with optional tag)
   - Can specify tag name manually

## Usage Examples

### Deploy to Development

```bash
# Create tag
git tag v1.2.3-dev-deploy_now -m "Deploy v1.2.3 to dev"

# Push tag
git push origin v1.2.3-dev-deploy_now
```

### Deploy to SIT

```bash
git tag v1.2.3-sit-deploy_now -m "Deploy v1.2.3 to sit"
git push origin v1.2.3-sit-deploy_now
```

### Deploy to UAT

```bash
git tag v1.2.3-uat-deploy_now -m "Deploy v1.2.3 to uat"
git push origin v1.2.3-uat-deploy_now
```

### Deploy to Production

```bash
git tag v1.2.3-prod-deploy_now -m "Deploy v1.2.3 to production"
git push origin v1.2.3-prod-deploy_now
```

## Manual Workflow Dispatch

### Using Unified Workflow

1. Navigate to Actions → "Tag-Based Deployment"
2. Click "Run workflow"
3. Enter:
   - **Tag name**: `v1.0.0-dev-deploy_now`
   - **Environment**: `auto` (recommended) or select `dev`, `sit`, `uat`, `prod`

### Using Environment-Specific Workflows

1. Navigate to Actions → "Deploy to Development" (or SIT/UAT/Production)
2. Click "Run workflow"
3. Optionally enter a tag name to checkout specific version

## Environment Detection Logic

The unified workflow detects environment from tag using this priority:

1. Manual selection (if provided)
2. Pattern: `-(dev|sit|uat|prod)-deploy`
3. Pattern: `_(dev|sit|uat|prod)_deploy`
4. Any occurrence of `dev`, `sit`, `uat`, or `prod` in tag name

## Workflow Steps

For each deployment, the workflow:

1. ✅ Determines environment from tag name
2. ✅ Checks out code at the tagged commit
3. ✅ Installs Python dependencies
4. ✅ Installs Databricks CLI
5. ✅ Loads environment configuration
6. ✅ Runs SQL migrations (via Python deployment script)
7. ✅ Deploys Databricks assets
8. ✅ Validates deployment (UAT and Prod only)
9. ✅ Runs smoke tests (Prod only)

## Benefits of Tag-Based Deployment

- **Version Control**: Each deployment is tied to a specific tag/version
- **Reproducibility**: Can redeploy exact same version
- **Auditability**: Clear history of what was deployed when
- **Rollback**: Easy to rollback to previous tag
- **Flexibility**: Deploy any tagged version to any environment

## Best Practices

1. **Tag Format**: Use semantic versioning with environment suffix
   - Good: `v1.2.3-dev-deploy_now`
   - Good: `release-2024-01-15-uat-deploy_now`
   - Bad: `dev-deploy_now` (missing version info)

2. **Tag Messages**: Always include meaningful messages
   ```bash
   git tag v1.2.3-prod-deploy_now -m "Production release: Added inventory reporting"
   ```

3. **Tag First, Then Deploy**: Create the tag, verify, then push to trigger deployment
   ```bash
   # Create tag locally first
   git tag v1.2.3-dev-deploy_now
   
   # Verify tag exists
   git tag -l "*-dev-deploy_now"
   
   # Push to trigger deployment
   git push origin v1.2.3-dev-deploy_now
   ```

4. **Environment Isolation**: Use different tags for different environments
   - Don't reuse the same tag across environments
   - Use consistent versioning scheme

## Troubleshooting

### Tag Not Triggering Workflow

- Ensure tag name matches one of the supported patterns
- Check that tag ends with `-deploy_now` or `-deploy-now`
- Verify tag contains environment name (dev, sit, uat, or prod)

### Wrong Environment Detected

- Use manual dispatch and specify environment explicitly
- Check tag name format - must contain environment name clearly
- Use unified workflow with manual environment selection

### Tag Doesn't Exist Error

- Ensure tag exists in the repository before pushing
- Verify tag is pushed to the correct remote
- Check that checkout is using the correct ref

## Migration from Branch-Based to Tag-Based

The system supports both methods:

- **Branch-based** (existing): Push to `develop`, `release/sit`, etc.
- **Tag-based** (new): Push tags ending with `-deploy_now`

You can use either method or both. Tag-based is recommended for production deployments.

