#!/usr/bin/env python3
"""
Notebook Validation Script
Validates Databricks notebooks for syntax and structure
"""

import os
import sys
import json
import nbformat
from nbformat import validate

def validate_notebook_file(file_path):
    """Validate a single notebook file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Validate notebook structure
        validate(notebook)
        
        # Check for required metadata
        if 'metadata' not in notebook:
            return False, "Missing metadata"
        
        # Check for language info
        if 'language_info' not in notebook.get('metadata', {}):
            return False, "Missing language_info in metadata"
        
        # Check cells
        if not notebook.get('cells'):
            return False, "No cells found"
        
        # Validate each cell
        for i, cell in enumerate(notebook['cells']):
            if 'cell_type' not in cell:
                return False, f"Cell {i} missing cell_type"
            
            if cell['cell_type'] not in ['code', 'markdown', 'raw']:
                return False, f"Cell {i} has invalid cell_type: {cell['cell_type']}"
        
        return True, "Valid"
        
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
