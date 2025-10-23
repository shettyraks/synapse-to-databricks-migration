#!/usr/bin/env python3
"""
Notebook Validation Script
Validates Databricks notebooks for syntax and structure
"""

import os
import sys
import json

def validate_notebook_file(file_path):
    """Validate a single notebook file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic Python syntax check for .py files
        if file_path.endswith('.py'):
            compile(content, file_path, 'exec')
            return True, "Valid Python syntax"
        
        # For .ipynb files, do basic JSON validation
        elif file_path.endswith('.ipynb'):
            try:
                notebook_data = json.loads(content)
                if 'cells' not in notebook_data:
                    return False, "Missing cells in notebook"
                return True, "Valid notebook structure"
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {e}"
        
        return True, "Valid"
        
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def validate_notebooks():
    """Validate all notebooks in the project"""
    print("🔍 Validating Databricks notebooks...")
    
    notebook_files = []
    
    # Find all Python files in notebooks directories
    for root, dirs, files in os.walk('src'):
        if 'notebooks' in root:
            for file in files:
                if file.endswith('.py'):
                    notebook_files.append(os.path.join(root, file))
    
    if not notebook_files:
        print("⚠️  No notebook files found")
        return True
    
    print(f"Found {len(notebook_files)} notebook files:")
    
    all_valid = True
    
    for notebook_file in notebook_files:
        print(f"  📝 Validating {notebook_file}...")
        
        # For Python files, we'll do basic syntax validation
        try:
            with open(notebook_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic Python syntax check
            compile(content, notebook_file, 'exec')
            print(f"    ✅ {notebook_file} - Valid Python syntax")
            
        except SyntaxError as e:
            print(f"    ❌ {notebook_file} - Syntax error: {e}")
            all_valid = False
        except Exception as e:
            print(f"    ❌ {notebook_file} - Error: {e}")
            all_valid = False
    
    return all_valid

def main():
    print("🚀 Starting notebook validation...")
    print("=" * 50)
    
    valid = validate_notebooks()
    
    print("=" * 50)
    
    if valid:
        print("🎉 All notebooks validated successfully!")
        sys.exit(0)
    else:
        print("❌ Notebook validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
