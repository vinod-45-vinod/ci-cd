@echo off
echo ============================================
echo Testing CI/CD Pipeline Setup
echo ============================================
echo.

echo Step 1: Checking Git Status...
git status
echo.

echo Step 2: Adding package-lock.json files...
git add frontend/package-lock.json
git add backend/package-lock.json
git add .github/workflows/ci-cd.yml
echo.

echo Step 3: Committing changes...
git commit -m "fix: Remove cache dependencies to fix build errors

- Removed cache-dependency-path from Node.js setup
- Removed cache-dependency-path from Python setup  
- Added package-lock.json files for frontend and backend
- This fixes the build errors in GitHub Actions"
echo.

echo Step 4: Ready to push! Run this command:
echo git push origin main
echo.
echo ============================================
echo OR if you want to push now, press any key...
echo ============================================
pause
git push origin main
