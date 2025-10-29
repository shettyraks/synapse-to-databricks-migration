# GitHub Secrets Configuration Guide

This document lists all required GitHub Secrets for the deployment system.

## Secrets for Each Environment

For each environment (dev, sit, uat, prod), you need to define secrets with the environment suffix (e.g., `_DEV`, `_SIT`, `_UAT`, `_PROD`).

---

## Option 1: Token Authentication (Simpler, Recommended for Development)

### Core Secrets (Required for all environments)

#### Development Environment
- `DATABRICKS_HOST_DEV` - Full Databricks workspace URL (e.g., `adb-xxx.xx.azuredatabricks.net`)
- `DATABRICKS_TOKEN_DEV` - Databricks workspace token (personal access token)
- `HTTP_PATH_DEV` - SQL warehouse HTTP path (e.g., `/sql/1.0/warehouses/xxxxxxxxxxxxx`)
- `SQL_USER_DEV` - SQL connection user (usually `token`)
- `SQL_PASSWORD_DEV` - Same as `DATABRICKS_TOKEN_DEV`

#### SIT Environment
- `DATABRICKS_HOST_SIT` - Full Databricks workspace URL
- `DATABRICKS_TOKEN_SIT` - Databricks workspace token
- `HTTP_PATH_SIT` - SQL warehouse HTTP path
- `SQL_USER_SIT` - SQL connection user (usually `token`)
- `SQL_PASSWORD_SIT` - Same as `DATABRICKS_TOKEN_SIT`

#### UAT Environment
- `DATABRICKS_HOST_UAT` - Full Databricks workspace URL
- `DATABRICKS_TOKEN_UAT` - Databricks workspace token
- `HTTP_PATH_UAT` - SQL warehouse HTTP path
- `SQL_USER_UAT` - SQL connection user (usually `token`)
- `SQL_PASSWORD_UAT` - Same as `DATABRICKS_TOKEN_UAT`

#### Production Environment
- `DATABRICKS_HOST_PROD` - Full Databricks workspace URL
- `DATABRICKS_TOKEN_PROD` - Databricks workspace token
- `HTTP_PATH_PROD` - SQL warehouse HTTP path
- `SQL_USER_PROD` - SQL connection user (usually `token`)
- `SQL_PASSWORD_PROD` - Same as `DATABRICKS_TOKEN_PROD`

---

## Option 2: Service Principal Authentication (Recommended for Production)

In addition to the core secrets above, add these for service principal authentication:

### Development Environment
- `SERVICE_PRINCIPAL_CLIENT_ID_DEV` - Azure AD application (client) ID
- `SERVICE_PRINCIPAL_CLIENT_SECRET_DEV` - Azure AD client secret value
- `SERVICE_PRINCIPAL_TENANT_ID_DEV` - Azure AD tenant ID

### SIT Environment
- `SERVICE_PRINCIPAL_CLIENT_ID_SIT` - Azure AD application (client) ID
- `SERVICE_PRINCIPAL_CLIENT_SECRET_SIT` - Azure AD client secret value
- `SERVICE_PRINCIPAL_TENANT_ID_SIT` - Azure AD tenant ID

### UAT Environment
- `SERVICE_PRINCIPAL_CLIENT_ID_UAT` - Azure AD application (client) ID
- `SERVICE_PRINCIPAL_CLIENT_SECRET_UAT` - Azure AD client secret value
- `SERVICE_PRINCIPAL_TENANT_ID_UAT` - Azure AD tenant ID

### Production Environment
- `SERVICE_PRINCIPAL_CLIENT_ID_PROD` - Azure AD application (client) ID
- `SERVICE_PRINCIPAL_CLIENT_SECRET_PROD` - Azure AD client secret value
- `SERVICE_PRINCIPAL_TENANT_ID_PROD` - Azure AD tenant ID

---

## Complete Secret List Summary

### Token Authentication (Minimal Setup)

**Total: 5 secrets × 4 environments = 20 secrets**

| Environment | Secrets Required |
|------------|------------------|
| Dev | DATABRICKS_HOST_DEV, DATABRICKS_TOKEN_DEV, HTTP_PATH_DEV, SQL_USER_DEV, SQL_PASSWORD_DEV |
| SIT | DATABRICKS_HOST_SIT, DATABRICKS_TOKEN_SIT, HTTP_PATH_SIT, SQL_USER_SIT, SQL_PASSWORD_SIT |
| UAT | DATABRICKS_HOST_UAT, DATABRICKS_TOKEN_UAT, HTTP_PATH_UAT, SQL_USER_UAT, SQL_PASSWORD_UAT |
| Prod | DATABRICKS_HOST_PROD, DATABRICKS_TOKEN_PROD, HTTP_PATH_PROD, SQL_USER_PROD, SQL_PASSWORD_PROD |

### Service Principal Authentication (Enhanced Security)

**Total: 8 secrets × 4 environments = 32 secrets**

Adds 3 secrets per environment:
- SERVICE_PRINCIPAL_CLIENT_ID_{ENV}
- SERVICE_PRINCIPAL_CLIENT_SECRET_{ENV}
- SERVICE_PRINCIPAL_TENANT_ID_{ENV}

---

## How to Add Secrets in GitHub

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name (e.g., `DATABRICKS_HOST_DEV`)
5. Enter the secret value
6. Click **Add secret**
7. Repeat for all required secrets

---

## Quick Setup Checklist

### Development Environment
- [ ] `DATABRICKS_HOST_DEV`
- [ ] `DATABRICKS_TOKEN_DEV`
- [ ] `HTTP_PATH_DEV`
- [ ] `SQL_USER_DEV`
- [ ] `SQL_PASSWORD_DEV`

### SIT Environment (add when ready)
- [ ] `DATABRICKS_HOST_SIT`
- [ ] `DATABRICKS_TOKEN_SIT`
- [ ] `HTTP_PATH_SIT`
- [ ] `SQL_USER_SIT`
- [ ] `SQL_PASSWORD_SIT`

### UAT Environment (add when ready)
- [ ] `DATABRICKS_HOST_UAT`
- [ ] `DATABRICKS_TOKEN_UAT`
- [ ] `HTTP_PATH_UAT`
- [ ] `SQL_USER_UAT`
- [ ] `SQL_PASSWORD_UAT`

### Production Environment (add when ready)
- [ ] `DATABRICKS_HOST_PROD`
- [ ] `DATABRICKS_TOKEN_PROD`
- [ ] `HTTP_PATH_PROD`
- [ ] `SQL_USER_PROD`
- [ ] `SQL_PASSWORD_PROD`

### Service Principal (Optional, for Production)
- [ ] `SERVICE_PRINCIPAL_CLIENT_ID_PROD`
- [ ] `SERVICE_PRINCIPAL_CLIENT_SECRET_PROD`
- [ ] `SERVICE_PRINCIPAL_TENANT_ID_PROD`

---

## Getting Secret Values

### Databricks Host
```
Format: adb-{workspace-id}.{region}.azuredatabricks.net
Example: adb-1234567890123456.7.azuredatabricks.net
Location: Databricks Workspace → Settings → Workspace settings
```

### Databricks Token
```
Location: Databricks Workspace → User Settings → Access Tokens
Can also use: Workspace Settings → Workspace tokens
```

### HTTP Path (SQL Warehouse)
```
Location: Databricks SQL → SQL Warehouses → Click warehouse → Connection Details
Format: /sql/1.0/warehouses/{warehouse-id}
```

### Service Principal Credentials
```
Created via: Azure Portal → Azure Active Directory → App registrations
Or via Azure CLI:
  az ad sp create-for-rbac --name "databricks-deployment-sp"
```

---

## Security Best Practices

1. ✅ Use separate tokens for each environment
2. ✅ Rotate tokens/secrets regularly
3. ✅ Use service principal for production
4. ✅ Grant minimum required permissions
5. ✅ Never log or expose secret values
6. ✅ Use Azure Key Vault for secrets management (advanced)

---

## Troubleshooting

### Missing Secret Error
If you see errors like `Missing required credentials`, check:
- Secret names are exactly as specified (case-sensitive)
- Suffix matches environment (`_DEV`, `_SIT`, `_UAT`, `_PROD`)
- Secrets are added to repository secrets (not environment secrets)

### Permission Denied
- Verify service principal has access to Databricks workspace
- Check token has required permissions (workspace admin)
- Ensure workspace token hasn't expired

---

## Reference

- [Authentication Guide](AUTHENTICATION.md) - Detailed authentication explanation
- [README.md](../README.md) - Main documentation

