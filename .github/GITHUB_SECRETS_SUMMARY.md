# GitHub Secrets Required

## Quick Reference - All Required Secrets

### Core Secrets (Token Authentication)

#### Development
```
DATABRICKS_HOST_DEV
DATABRICKS_TOKEN_DEV
HTTP_PATH_DEV
SQL_USER_DEV
SQL_PASSWORD_DEV
```

#### SIT
```
DATABRICKS_HOST_SIT
DATABRICKS_TOKEN_SIT
HTTP_PATH_SIT
SQL_USER_SIT
SQL_PASSWORD_SIT
```

#### UAT
```
DATABRICKS_HOST_UAT
DATABRICKS_TOKEN_UAT
HTTP_PATH_UAT
SQL_USER_UAT
SQL_PASSWORD_UAT
```

#### Production
```
DATABRICKS_HOST_PROD
DATABRICKS_TOKEN_PROD
HTTP_PATH_PROD
SQL_USER_PROD
SQL_PASSWORD_PROD
```

### Optional: Service Principal (Recommended for Production)

For enhanced security, add these to each environment:

```
SERVICE_PRINCIPAL_CLIENT_ID_{ENV}
SERVICE_PRINCIPAL_CLIENT_SECRET_{ENV}
SERVICE_PRINCIPAL_TENANT_ID_{ENV}
```

Replace `{ENV}` with: `DEV`, `SIT`, `UAT`, or `PROD`

## Total Count

- **Token Auth Only**: 20 secrets (5 per environment × 4)
- **With Service Principal**: 32 secrets (8 per environment × 4)

## Setup Instructions

See detailed documentation: [docs/GITHUB_SECRETS.md](../docs/GITHUB_SECRETS.md)
