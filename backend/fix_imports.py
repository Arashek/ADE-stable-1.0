"""
Script to fix relative imports in the ADE backend codebase.
Converts triple-dot relative imports (from ...module) to absolute imports (from backend.module).
"""

import os
import re
import sys
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix relative imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace triple-dot relative imports with absolute imports
        modified_content = re.sub(
            r'from \.\.\.([\w\.]+) import', 
            r'from backend.\1 import', 
            content
        )
        
        # Replace double-dot relative imports with absolute imports
        # Determine the module path based on the file path
        rel_path = os.path.relpath(file_path, os.path.join(os.getcwd()))
        parts = rel_path.split(os.sep)
        if len(parts) > 1:
            module_prefix = '.'.join(parts[:-1])
            modified_content = re.sub(
                r'from \.\.([\w\.]+) import', 
                lambda m: f'from backend.{module_prefix.split(".", 1)[1] if "." in module_prefix else ""}.{m.group(1)} import',
                modified_content
            )
        
        # Write back if changes were made
        if content != modified_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def fix_imports_in_directory(directory_path, extensions=None, max_depth=None, _current_depth=0):
    """Recursively fix imports in all Python files in a directory."""
    if extensions is None:
        extensions = ['.py']
    
    if max_depth is not None and _current_depth > max_depth:
        return 0
    
    fixed_count = 0
    try:
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            
            if os.path.isfile(item_path):
                if any(item_path.endswith(ext) for ext in extensions):
                    if fix_imports_in_file(item_path):
                        print(f"Fixed imports in: {item_path}")
                        fixed_count += 1
            
            elif os.path.isdir(item_path) and not item.startswith('.'):
                fixed_count += fix_imports_in_directory(
                    item_path, extensions, max_depth, _current_depth + 1
                )
    except Exception as e:
        print(f"Error processing directory {directory_path}: {str(e)}")
    
    return fixed_count

def main():
    # Priority directories to fix first
    priority_dirs = [
        'services/memory',
        'services/coordination',
        'services/agents',
        'services/owner_panel_service.py',
        'routes/owner_panel_routes.py',
        'owner',
        'database'
    ]
    
    backend_dir = os.getcwd()
    print(f"Starting import fixes in {backend_dir}")
    
    total_fixed = 0
    
    # Fix priority directories first
    for dir_path in priority_dirs:
        full_path = os.path.join(backend_dir, dir_path)
        if os.path.exists(full_path):
            if os.path.isfile(full_path):
                if fix_imports_in_file(full_path):
                    print(f"Fixed imports in priority file: {full_path}")
                    total_fixed += 1
            else:
                fixed = fix_imports_in_directory(full_path)
                print(f"Fixed {fixed} files in priority directory: {dir_path}")
                total_fixed += fixed
    
    print(f"Total files fixed: {total_fixed}")

if __name__ == "__main__":
    main()
