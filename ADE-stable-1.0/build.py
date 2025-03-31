import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build_executable():
    print("Building executable...")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    if os.path.exists('modeltrainingmanager.spec'):
        os.remove('modeltrainingmanager.spec')
    
    # Add src to Python path
    src_path = os.path.abspath('src')
    sys.path.insert(0, src_path)
    
    # Build using PyInstaller
    PyInstaller.__main__.run([
        'src/ade/training_manager/main.py',
        '--name=modeltrainingmanager',
        '--onefile',
        '--windowed',
        '--icon=assets/icon.ico',
        '--add-data=assets;assets',
        '--add-data=config;config',
        '--add-data=docs;docs',
        '--hidden-import=PyQt6',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=matplotlib',
        '--hidden-import=numpy',
        '--hidden-import=torch',
        '--hidden-import=transformers',
        '--paths=src',
        '--clean'
    ])
    
    # Copy executable to root directory
    if os.path.exists('dist/modeltrainingmanager.exe'):
        shutil.copy('dist/modeltrainingmanager.exe', 'modeltrainingmanager.exe')
        print("Build completed successfully!")
    else:
        print("Error: Executable not found in dist directory")
        sys.exit(1)

if __name__ == "__main__":
    build_executable() 