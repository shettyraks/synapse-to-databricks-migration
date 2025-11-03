# Authentication Guide

This document explains the authentication options available for connecting to Databricks SQL and deploying Databricks Asset Bundles.

## Authentication Methods

The deployment system supports two authentication methods:

1. **Token Authentication** (Default)
2. **Service Principal Authentication** (Azure)

## Token Authentication

Token authentication uses a Databricks personal access token or workspace token.

### Required Environment Variables

For **SQL Migrations**:
```bash
DATABRICKS_HOST_DEV=adb-xxx.xx.azuredatabricks.net
HTTP_PATH_DEV=/sql/1.0/warehouses/xxx
SQL_USER_DEV=token
SQL_PASSWORD_DEV=your-databricks-token
DATABRICKS_TOKEN_DEV=your-databricks-token
```

### How It Works

- Uses `AuthMech=3` in JDBC URL
- Requires a workspace token or personal access token
- Simple setup, suitable for development and CI/CD

## Service Principal Authentication

Service Principal authentication uses Azure AD service principal credentials.

### Required Environment Variables

For **SQL Migrations**:
```bash
DATABRICKS_HOST_DEV=adb-xxx.xx.azuredatabricks.net
HTTP_PATH_DEV=/sql/1.0/warehouses/xxx
SERVICE_PRINCIPAL_CLIENT_ID_DEV=your-client-id
SERVICE_PRINCIPAL_CLIENT_SECRET_DEV=your-client-secret
SERVICE_PRINCIPAL_TENANT_ID_DEV=your-tenant-id
DATABRICKS_TOKEN_DEV=your-databricks-token  # Still needed for CLI
```

### How It Works

- Uses `AuthMech=11` in JDBC URL with `TenantId` parameter
- Requires Azure AD service principal with permissions to Databricks workspace
- More secure for production environments
- Allows integration with Azure Key Vault

### Setting Up a Service Principal

1. Create service principal in Azure AD:
   ```bash
   az ad sp create-for-rbac --name "databricks-deployment-sp"
   ```

2. Grant permissions to Databricks workspace:
   - Add service principal to Databricks workspace
   - Assign appropriate role (Contributor or Owner)

3. Configure environment variables:
   ```bash
   export SERVICE_PRINCIPAL_CLIENT_ID_DEV="<client-id>"
   export SERVICE_PRINCIPAL_CLIENT_SECRET_DEV="<client-secret>"
   export SERVICE_PRINCIPAL_TENANT_ID_DEV="<tenant-id>"
   ```

## Automatic Detection

The deployment system automatically detects which authentication method to use based on environment variables:

- If `SERVICE_PRINCIPAL_CLIENT_ID`, `SERVICE_PRINCIPAL_CLIENT_SECRET`, and `SERVICE_PRINCIPAL_TENANT_ID` are all set → Uses Service Principal
- Otherwise → Uses Token authentication

## GitHub Actions Integration

### Token Authentication in CI/CD

```yaml
env:
  DATABRICKS_HOST_DEV: ${{ secrets.DATABRICKS_HOST_DEV }}
  DATABRICKS_TOKEN_DEV: ${{ secrets.DATABRICKS_TOKEN_DEV }}
  HTTP_PATH_DEV: ${{ secrets.HTTP_PATH_DEV }}
  SQL_USER_DEV: ${{ secrets.SQL_USER_DEV }}
  SQL_PASSWORD_DEV: ${{ secrets.SQL_PASSWORD_DEV }}
```

### Service Principal in CI/CD

```yaml
env:
  DATABRICKS_HOST_DEV: ${{ secrets.DATABRICKS_HOST_DEV }}
  SERVICE_PRINCIPAL_CLIENT_ID_DEV: ${{ secrets.SERVICE_PRINCIPAL_CLIENT_ID_DEV }}
  SERVICE_PRINCIPAL_CLIENT_SECRET_DEV: ${{ secrets.SERVICE_PRINCIPAL_CLIENT_SECRET_DEV }}
  SERVICE_PRINCIPAL_TENANT_ID_DEV: ${{ secrets.SERVICE_PRINCIPAL_TENANT_ID_DEV }}
  DATABRICKS_TOKEN_DEV: ${{ secrets.DATABRICKS_TOKEN_DEV }}
  HTTP_PATH_DEV: ${{ secrets.HTTP_PATH_DEV }}
```

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use GitHub Secrets** for all authentication credentials
3. **Rotate credentials regularly** (especially tokens)
4. **Use Service Principal for production** environments
5. **Implement least privilege** - grant minimum required permissions
6. **Use Azure Key Vault** to manage service principal credentials

## Troubleshooting

### Connection Failures

```bash
# Enable debug mode to see authentication details
python deploy.py --environment dev --debug
```

### Service Principal Authentication Issues

1. Verify service principal has access to Databricks workspace
2. Check tenant ID is correct
3. Ensure client secret hasn't expired
4. Verify Azure AD app registration permissions

### Token Authentication Issues

1. Verify token hasn't expired
2. Check token has necessary permissions
3. Ensure workspace URL is correct

## JDBC URL Comparison

### Token Authentication
```
jdbc:databricks://adb-xxx:443;transportMode=http;ssl=1;httpPath=/sql/1.0/warehouses/xxx;AuthMech=3;UID=token;PWD=your-token;ConnCatalog=your-catalog
```

### Service Principal Authentication
```
jdbc:databricks://adb-xxx:443;transportMode=http;ssl=1;httpPath=/sql/1.0/warehouses/xxx;AuthMech=11;UID=client-id;PWD=client-secret;TenantId=tenant-id;ConnCatalog=your-catalog
```

