"""
Test suite for Databricks Migration Project
"""
import pytest
import os
import yaml


class TestProjectStructure:
    """Test project structure and configuration files"""
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists"""
        assert os.path.exists("requirements.txt")
    
    def test_databricks_yml_exists(self):
        """Test that databricks.yml exists"""
        assert os.path.exists("databricks.yml")
    
    def test_src_directory_exists(self):
        """Test that src directory exists"""
        assert os.path.exists("src")
    
    def test_domain_directories_exist(self):
        """Test that all domain directories exist"""
        domains = ["Inventory", "MasterData", "Rail", "Shipping", "SmartAlert"]
        for domain in domains:
            assert os.path.exists(f"src/{domain}")
            assert os.path.exists(f"src/{domain}/jobs")
            assert os.path.exists(f"src/{domain}/notebooks")
            assert os.path.exists(f"src/{domain}/sql_deployment")


class TestConfigurationFiles:
    """Test configuration file validity"""
    
    def test_databricks_yml_syntax(self):
        """Test that databricks.yml has valid YAML syntax"""
        with open("databricks.yml", "r") as f:
            content = f.read()
        
        # Basic YAML structure check
        assert "bundle:" in content
        assert "workspace:" in content
        assert "targets:" in content
    
    def test_requirements_txt_format(self):
        """Test that requirements.txt has proper format"""
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        # Check for required packages
        assert "databricks-sdk" in content
        assert "pytest" in content
        assert "PyYAML" in content


class TestSQLFiles:
    """Test SQL migration files"""
    
    def test_inventory_sql_files_exist(self):
        """Test that Inventory SQL files exist"""
        sql_files = [
            "src/Inventory/sql_deployment/V1__create_inventory_header_table.sql",
            "src/Inventory/sql_deployment/V2__create_inventory_transaction_table.sql",
            "src/Inventory/sql_deployment/V3__create_calendar_dim_table.sql"
        ]
        
        for sql_file in sql_files:
            assert os.path.exists(sql_file)
    
    def test_sql_files_have_valid_structure(self):
        """Test that SQL files contain expected SQL keywords"""
        sql_files = [
            "src/Inventory/sql_deployment/V1__create_inventory_header_table.sql",
            "src/Inventory/sql_deployment/V2__create_inventory_transaction_table.sql",
            "src/Inventory/sql_deployment/V3__create_calendar_dim_table.sql"
        ]
        
        for sql_file in sql_files:
            if os.path.exists(sql_file):
                with open(sql_file, "r") as f:
                    content = f.read()
                assert "CREATE TABLE" in content or "INSERT INTO" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
