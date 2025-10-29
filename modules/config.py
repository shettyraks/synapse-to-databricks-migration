"""Configuration management module for deployment system."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    """Configuration for a single environment."""
    customer: str
    catalog: str
    flyway_schema: str
    schemas: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentConfig':
        """Create EnvironmentConfig from dictionary."""
        return cls(
            customer=data.get('customer', ''),
            catalog=data.get('catalog', ''),
            flyway_schema=data.get('flyway_schema', ''),
            schemas=data.get('schemas', [])
        )


class ConfigManager:
    """Manages configuration for multiple environments."""
    
    def __init__(self, config_path: str = 'config/customer_input.yml'):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = Path(config_path)
        self._config_data: Optional[Dict[str, Any]] = None
        self._environments: Optional[Dict[str, EnvironmentConfig]] = None
        
    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self._config_data = yaml.safe_load(f)
        
        # Parse environments
        self._environments = {}
        environments_data = self._config_data.get('environments', {})
        
        for env_name, env_data in environments_data.items():
            self._environments[env_name] = EnvironmentConfig.from_dict(env_data)
    
    def get_environment(self, environment: str) -> EnvironmentConfig:
        """Get configuration for a specific environment.
        
        Args:
            environment: Environment name (dev, sit, uat, prod)
            
        Returns:
            EnvironmentConfig for the specified environment
        """
        if self._environments is None:
            self.load()
        
        if environment not in self._environments:
            raise ValueError(f"Environment '{environment}' not found in config")
        
        return self._environments[environment]
    
    def get_all_environments(self) -> Dict[str, EnvironmentConfig]:
        """Get all environment configurations.
        
        Returns:
            Dictionary of environment name to EnvironmentConfig
        """
        if self._environments is None:
            self.load()
        
        return self._environments.copy()
    
    def validate(self) -> bool:
        """Validate configuration data.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if self._environments is None:
            self.load()
        
        errors = []
        
        for env_name, env_config in self._environments.items():
            # Check for placeholder values
            if 'TBD' in env_config.customer or 'CHANGE_ME' in env_config.customer:
                errors.append(f"Environment '{env_name}' has placeholder customer value")
            
            if not env_config.catalog:
                errors.append(f"Environment '{env_name}' missing catalog")
            
            if not env_config.flyway_schema:
                errors.append(f"Environment '{env_name}' missing flyway_schema")
            
            if not env_config.schemas:
                errors.append(f"Environment '{env_name}' missing schemas")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True


class DeploymentConfig:
    """Configuration for a deployment run."""
    
    def __init__(self, environment: str):
        """Initialize deployment configuration.
        
        Args:
            environment: Environment name (dev, sit, uat, prod)
        """
        self.environment = environment
        self.config_manager = ConfigManager()
        self.env_config = self.config_manager.get_environment(environment)
        
        # Load Databricks credentials from environment
        self.databricks_host = os.environ.get(f'DATABRICKS_HOST_{environment.upper()}')
        self.databricks_token = os.environ.get(f'DATABRICKS_TOKEN_{environment.upper()}')
        
        # Load Flyway credentials
        self.http_path = os.environ.get(f'HTTP_PATH_{environment.upper()}')
        self.user = os.environ.get(f'USER_{environment.upper()}')
        self.password = os.environ.get(f'PASSWORD_{environment.upper()}')
        
        # Load Flyway configuration
        self.flyway_locations = os.environ.get('FLYWAY_LOCATIONS', 'filesystem:src/Inventory/sql_deployment')
    
    def get_jdbc_url(self) -> str:
        """Get JDBC URL for Flyway."""
        if not all([self.databricks_host, self.http_path]):
            raise ValueError("Missing required Databricks credentials")
        
        return (f"jdbc:databricks://{self.databricks_host}:443;"
                f"transportMode=http;ssl=1;"
                f"httpPath={self.http_path};"
                f"AuthMech=3;UID={self.user};PWD={self.password};"
                f"ConnCatalog={self.env_config.catalog}")
    
    def get_schemas_str(self) -> str:
        """Get comma-separated schemas string."""
        return ','.join(self.env_config.schemas)
    
    def validate(self) -> bool:
        """Validate deployment configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required credentials are missing
        """
        errors = []
        
        if not self.databricks_host:
            errors.append("DATABRICKS_HOST not set")
        
        if not self.databricks_token:
            errors.append("DATABRICKS_TOKEN not set")
        
        if not self.http_path:
            errors.append("HTTP_PATH not set")
        
        if not self.user:
            errors.append("USER not set")
        
        if not self.password:
            errors.append("PASSWORD not set")
        
        if errors:
            raise ValueError(f"Missing required credentials:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True

