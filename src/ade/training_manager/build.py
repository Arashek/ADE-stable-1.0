import os
import sys
import shutil
from pathlib import Path
import subprocess

def build():
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Create build directory
    build_dir = current_dir / "build"
    build_dir.mkdir(exist_ok=True)
    
    # Create assets directory
    assets_dir = build_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Copy icon file
    icon_src = current_dir / "assets" / "icon.ico"
    if icon_src.exists():
        shutil.copy2(icon_src, assets_dir)
    else:
        print("Warning: icon.ico not found in assets directory")
    
    # Install PyInstaller if not already installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Build the executable
    print("Building executable...")
    subprocess.run([
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "--workpath", str(build_dir / "work"),
        "--distpath", str(build_dir / "dist"),
        str(current_dir / "modeltrainingmanager.spec")
    ])
    
    # Create installation package
    print("Creating installation package...")
    dist_dir = build_dir / "dist"
    install_dir = Path("D:/ADE Training Manager")
    
    # Create installation directory
    install_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy executable and dependencies
    shutil.copytree(dist_dir / "modeltrainingmanager", install_dir / "modeltrainingmanager", dirs_exist_ok=True)
    
    # Copy assets
    shutil.copytree(assets_dir, install_dir / "assets", dirs_exist_ok=True)
    
    # Copy requirements.txt
    shutil.copy2(current_dir / "requirements.txt", install_dir)
    
    # Create desktop shortcut
    desktop = Path(os.path.expanduser("~")) / "Desktop"
    shortcut_path = desktop / "ADE Training Manager.lnk"
    
    with open(shortcut_path, "w") as f:
        f.write(f"""[InternetShortcut]
URL=file:///{install_dir}/modeltrainingmanager.exe
IconFile={install_dir}/assets/icon.ico
IconIndex=0
""")
    
    print(f"\nInstallation package created at: {install_dir}")
    print("You can now run the installer by double-clicking the executable.")

if __name__ == "__main__":
    build() 