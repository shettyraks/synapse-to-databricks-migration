"""Databricks API client for deployment operations."""

import os
import subprocess
import json
from typing import Dict, List, Optional, Any
from .config import DeploymentConfig


class DatabricksClient:
    """Client for interacting with Databricks APIs."""
    
    def __init__(self, deployment_config: DeploymentConfig):
        """Initialize Databricks client.
        
        Args:
            deployment_config: Deployment configuration
        """
        self.config = deployment_config
        self.host = deployment_config.databricks_host
        self.auth_method = deployment_config.auth_method
        
    def _run_cli_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a Databricks CLI command.
        
        Args:
            command: Command and arguments as list
            capture_output: Whether to capture output
            
        Returns:
            CompletedProcess with result
        """
        env = os.environ.copy()
        env['DATABRICKS_HOST'] = self.host
        
        # Set authentication based on method
        if self.auth_method == 'service_principal':
            # Service Principal authentication
            if self.config.service_principal_client_id:
                env['ARM_CLIENT_ID'] = self.config.service_principal_client_id
            if self.config.service_principal_client_secret:
                env['ARM_CLIENT_SECRET'] = self.config.service_principal_client_secret
            if self.config.service_principal_tenant_id:
                env['ARM_TENANT_ID'] = self.config.service_principal_tenant_id
            
            # Still provide token for CLI compatibility
            if self.config.databricks_token:
                env['DATABRICKS_TOKEN'] = self.config.databricks_token
            
            env['DATABRICKS_AUTH_TYPE'] = 'azure-cli'
        else:
            # Token authentication (default)
            env['DATABRICKS_TOKEN'] = self.config.databricks_token
        
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                check=True,
                env=env
            )
            return result
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Databricks CLI command failed: {' '.join(command)}\n{e.stderr}") from e
    
    def bundle_deploy(self, target: str, variables: Dict[str, str]) -> None:
        """Deploy Databricks Asset Bundle.
        
        Args:
            target: Deployment target (dev, sit, uat, prod)
            variables: Variables to pass to deployment
        """
        command = ['databricks', 'bundle', 'deploy', '--target', target]
        
        # Add variables
        for key, value in variables.items():
            command.extend(['--var', f"{key}={value}"])
        
        print(f"Deploying Databricks bundle to {target}...")
        result = self._run_cli_command(command, capture_output=False)
        
        if result.returncode == 0:
            print(f"✅ Bundle deployment to {target} completed")
        else:
            raise RuntimeError(f"Bundle deployment to {target} failed")
    
    def bundle_summary(self, target: str) -> None:
        """Get bundle deployment summary.
        
        Args:
            target: Deployment target
        """
        command = ['databricks', 'bundle', 'summary', '--target', target]
        result = self._run_cli_command(command, capture_output=False)
        
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs in the workspace.
        
        Returns:
            List of job definitions
        """
        command = ['databricks', 'jobs', 'list', '--output', 'json']
        result = self._run_cli_command(command)
        
        try:
            jobs = json.loads(result.stdout)
            return jobs
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse jobs list: {e}") from e
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get job details.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job definition
        """
        command = ['databricks', 'jobs', 'get', '--job-id', job_id, '--output', 'json']
        result = self._run_cli_command(command)
        
        try:
            job = json.loads(result.stdout)
            return job
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse job details: {e}") from e
    
    def run_job(self, job_id: str, parameters: Optional[Dict[str, str]] = None) -> str:
        """Run a job now (one-time trigger).
        
        Args:
            job_id: Job ID
            parameters: Optional job parameters
            
        Returns:
            Run ID
        """
        command = ['databricks', 'jobs', 'run-now', '--job-id', job_id]
        
        if parameters:
            command.extend(['--json', json.dumps({'notebook_params': parameters})])
        
        result = self._run_cli_command(command)
        
        try:
            run_info = json.loads(result.stdout)
            return run_info.get('run_id')
        except (json.JSONDecodeError, KeyError) as e:
            raise RuntimeError(f"Failed to parse run-now response: {e}") from e

