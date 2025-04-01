#!/usr/bin/env python
"""
Import Fixer for ADE Platform

This script automatically fixes import statements in Python files by:
1. Removing 'backend.' prefix from absolute imports
2. Ensuring proper relative imports

Usage:
    python fix_imports.py
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 'from backend.services' with 'from services'
    modified_content = re.sub(r'from backend\.', 'from ', content)
    modified_content = re.sub(r'import backend\.', 'import ', modified_content)
    
    if content != modified_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"Fixed imports in {file_path}")
        return True
    return False

def fix_imports_in_directory(directory):
    """Fix import statements in all Python files in a directory and its subdirectories"""
    fixed_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    return fixed_count

def main():
    """Main function to fix imports in the ADE platform backend"""
    backend_dir = Path(__file__).parent / "backend"
    
    print(f"Fixing imports in {backend_dir}...")
    fixed_count = fix_imports_in_directory(backend_dir)
    
    print(f"Fixed imports in {fixed_count} files")
    print("Import fixing completed")

if __name__ == "__main__":
    main()
