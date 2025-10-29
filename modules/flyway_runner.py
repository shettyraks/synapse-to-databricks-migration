"""Flyway migration runner for SQL deployments."""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from .config import DeploymentConfig


class FlywayRunner:
    """Runner for Flyway SQL migrations."""
    
    def __init__(self, deployment_config: DeploymentConfig):
        """Initialize Flyway runner.
        
        Args:
            deployment_config: Deployment configuration
        """
        self.config = deployment_config
        self.flyway_jar_path = Path('lib/flyway-commandline-10.18.0/flyway')
        
    def _download_flyway_if_needed(self) -> None:
        """Download Flyway if not already present."""
        if self.flyway_jar_path.exists():
            return
        
        flyway_dir = self.flyway_jar_path.parent
        flyway_dir.mkdir(parents=True, exist_ok=True)
        
        print("Downloading Flyway...")
        url = "https://repo1.maven.org/maven2/org/flywaydb/flyway-commandline/10.18.0/flyway-commandline-10.18.0-linux-x64.tar.gz"
        
        subprocess.run(['curl', '-fsSL', url, '-o', 'flyway.tar.gz'], check=True)
        subprocess.run(['tar', '-xzf', 'flyway.tar.gz', '-C', str(flyway_dir)], check=True)
        Path('flyway.tar.gz').unlink()
        
        # Download JDBC driver
        jdbc_url = "https://repo1.maven.org/maven2/com/databricks/databricks-jdbc/3.2.0/databricks-jdbc-3.2.0.jar"
        subprocess.run(['curl', '-fsSL', jdbc_url, '-o', 'lib/databricks-jdbc.jar'], check=True)
        
    def _download_jdbc_driver(self) -> None:
        """Download Databricks JDBC driver if needed."""
        driver_path = Path('lib/databricks-jdbc.jar')
        
        if driver_path.exists():
            return
        
        print("Downloading Databricks JDBC driver...")
        jdbc_url = "https://repo1.maven.org/maven2/com/databricks/databricks-jdbc/3.2.0/databricks-jdbc-3.2.0.jar"
        
        os.makedirs('lib', exist_ok=True)
        subprocess.run(['curl', '-fsSL', jdbc_url, '-o', str(driver_path)], check=True)
    
    def _create_flyway_conf(self, conf_file: Path) -> None:
        """Create Flyway configuration file.
        
        Args:
            conf_file: Path to configuration file
        """
        jdbc_url = self.config.get_jdbc_url()
        schemas = self.config.get_schemas_str()
        
        conf_content = f"""flyway.url={jdbc_url}
flyway.driver=com.databricks.client.jdbc.Driver
flyway.locations={self.config.flyway_locations}
flyway.schemas={schemas}
flyway.defaultSchema={self.config.env_config.flyway_schema}
flyway.baselineOnMigrate=true
flyway.validateOnMigrate=true
flyway.outOfOrder=false
flyway.cleanDisabled=true
flyway.placeholders.customer={self.config.env_config.customer}
"""
        
        with open(conf_file, 'w') as f:
            f.write(conf_content)
    
    def migrate(self, debug: bool = False) -> bool:
        """Run Flyway migrations.
        
        Args:
            debug: Enable debug output
            
        Returns:
            True if migrations succeeded
            
        Raises:
            RuntimeError: If migration fails
        """
        # Download dependencies if needed
        self._download_jdbc_driver()
        
        # Create Flyway configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as conf_file:
            conf_path = Path(conf_file.name)
            self._create_flyway_conf(conf_path)
            
            try:
                # Run Flyway migrate
                jdbc_driver = Path('lib/databricks-jdbc.jar').absolute()
                flyway_cmd = Path('lib/flyway-commandline-10.18.0/flyway')
                
                if not flyway_cmd.exists():
                    self._download_flyway_if_needed()
                
                command = [
                    'java',
                    '-cp', f'{flyway_cmd}/lib/*:{jdbc_driver}',
                    'org.flywaydb.commandline.Main',
                    f'-configFiles={conf_path}',
                    'migrate'
                ]
                
                if debug:
                    command.append('-X')
                
                print(f"Running Flyway migrations for {self.config.environment}...")
                print(f"JDBC URL: {self.config.get_jdbc_url()[:100]}...")
                
                env = os.environ.copy()
                env['FLYWAY_DEBUG'] = '1' if debug else '0'
                
                result = subprocess.run(
                    command,
                    capture_output=False,
                    env=env
                )
                
                if result.returncode == 0:
                    print("✅ Flyway migrations completed successfully")
                    return True
                else:
                    raise RuntimeError(f"Flyway migration failed with return code {result.returncode}")
                    
            finally:
                # Clean up
                if conf_path.exists():
                    conf_path.unlink()
    
    def validate(self) -> bool:
        """Validate migration state without applying changes.
        
        Returns:
            True if validation passes
            
        Raises:
            RuntimeError: If validation fails
        """
        self._download_jdbc_driver()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as conf_file:
            conf_path = Path(conf_file.name)
            self._create_flyway_conf(conf_path)
            
            try:
                jdbc_driver = Path('lib/databricks-jdbc.jar').absolute()
                flyway_cmd = Path('lib/flyway-commandline-10.18.0/flyway')
                
                command = [
                    'java',
                    '-cp', f'{flyway_cmd}/lib/*:{jdbc_driver}',
                    'org.flywaydb.commandline.Main',
                    f'-configFiles={conf_path}',
                    'validate'
                ]
                
                print(f"Validating Flyway migrations for {self.config.environment}...")
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("✅ Flyway validation passed")
                    return True
                else:
                    print(f"❌ Flyway validation failed:\n{result.stderr}")
                    raise RuntimeError(f"Flyway validation failed with return code {result.returncode}")
                    
            finally:
                if conf_path.exists():
                    conf_path.unlink()

