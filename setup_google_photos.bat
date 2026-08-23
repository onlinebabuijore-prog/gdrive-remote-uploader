@echo off
title Setup Google Photos Remote
color 0b
echo ========================================================
echo       Google Photos Authorization Setup
echo ========================================================
echo.
echo Step 1: Your default web browser will open.
echo Step 2: Choose your Google account and click "Allow".
echo.
pause

set RCLONE_EXE="C:\Users\Rajib Karmakar\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.75.0-windows-amd64\rclone.exe"

echo.
echo Launching Google Photos Authorization...
%RCLONE_EXE% config create gphotos "google photos"

echo.
echo Syncing new config to GitHub Actions Secret...
powershell -Command "$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes(\"$env:APPDATA\rclone\rclone.conf\")); gh secret set RCLONE_CONF_BASE64 --body $b64 --repo onlinebabuijore-prog/gdrive-remote-uploader"

echo.
echo ========================================================
echo [SUCCESS] Google Photos has been successfully connected!
echo ========================================================
echo.
pause
