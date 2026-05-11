@echo off
echo ==========================================
echo       ECHOES GIT UPLOAD SCRIPT
echo ==========================================
echo.

set /p desc="Enter a brief description of your changes (e.g., added new chapter 2): "

echo.
echo [1/3] Staging files...
git add .

echo [2/3] Committing changes...
git commit -m "%desc%"

echo [3/3] Uploading to GitHub...
git push

echo.
echo ==========================================
echo   Upload complete! Press any key to exit.
echo ==========================================
pause
