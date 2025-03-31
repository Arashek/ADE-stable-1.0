@echo off
echo Building ADE Model Training Manager...

:: Create assets directory if it doesn't exist
if not exist assets mkdir assets

:: Copy icon file if it exists
if exist ..\..\assets\icon.ico (
    copy ..\..\assets\icon.ico assets\
) else (
    echo Warning: icon.ico not found in assets directory
)

:: Install required packages
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

:: Build the executable
echo Building executable...
python build.py

:: Create installation package
echo Creating installation package...
xcopy /E /I /Y "build\dist\modeltrainingmanager" "D:\ADE Training Manager\modeltrainingmanager"
xcopy /E /I /Y "assets" "D:\ADE Training Manager\assets"
copy /Y "requirements.txt" "D:\ADE Training Manager\"

:: Create desktop shortcut
echo Creating desktop shortcut...
echo [InternetShortcut] > "%USERPROFILE%\Desktop\ADE Training Manager.lnk"
echo URL=file:///D:/ADE Training Manager/modeltrainingmanager.exe >> "%USERPROFILE%\Desktop\ADE Training Manager.lnk"
echo IconFile=D:/ADE Training Manager/assets/icon.ico >> "%USERPROFILE%\Desktop\ADE Training Manager.lnk"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\ADE Training Manager.lnk"

echo Build completed successfully!
echo Installation package created at: D:\ADE Training Manager
echo You can now run the installer by double-clicking the executable. 