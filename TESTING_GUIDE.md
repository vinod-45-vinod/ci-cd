# 🧪 Complete Testing Guide - CI/CD Pipeline

## ⚡ QUICK FIX for Build Errors

**If you got "Process completed with exit code 1" errors**, they've been fixed!

### What Was Wrong:
- Missing `package-lock.json` files
- Workflow trying to use cache before files existed

### What Was Fixed:
1. ✅ Generated `frontend/package-lock.json`
2. ✅ Generated `backend/package-lock.json`
3. ✅ Removed cache configurations from workflow

### Ready to Push:
```cmd
git add .
git commit -m "fix: Remove cache dependencies and add package-lock.json"
git push origin main
```

Or use the batch file: `commit-and-push.bat`

---

## How to Test Your Pipeline Before GitHub

Follow these steps to test everything locally **before** pushing to GitHub.

---

## 📋 **Prerequisites Check**

Run these commands to verify your environment:

```bash
# Check Node.js version (should be 18.x)
node --version

# Check npm version
npm --version

# Check Python version (should be 3.11.x)
python --version

# Check Docker (optional, for full testing)
docker --version
docker-compose --version
```

---

## 🎯 **Step-by-Step Local Testing**

### **1. Test Frontend**

Open a new terminal and run:

```bash
# Navigate to frontend
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\frontend"

# Install dependencies
npm install

# Run tests with coverage (must pass with ≥75%)
npm run test:coverage

# Run linting (must have zero errors)
npm run lint

# Build production bundle
npm run build
```

**Expected Results:**
- ✅ All tests pass (14 tests)
- ✅ Coverage ≥75% for all metrics (statements, branches, functions, lines)
- ✅ Zero ESLint errors
- ✅ Build completes successfully

**If it fails:**
- Coverage too low? The tests might not be running. Try: `npm test -- --coverage --watchAll=false`
- Lint errors? Run: `npm run lint:fix` to auto-fix, then `npm run lint` again

---

### **2. Test Backend**

Open a new terminal and run:

```bash
# Navigate to backend
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\backend"

# Install dependencies
npm install

# Run tests with coverage (must pass with ≥75%)
npm run test:coverage

# Run linting (must have zero errors)
npm run lint
```

**Expected Results:**
- ✅ All tests pass (30+ tests)
- ✅ Coverage ≥75% for all metrics
- ✅ Zero ESLint errors

**If it fails:**
- Port already in use? Close any running backend servers
- Module not found? Delete `node_modules` and `package-lock.json`, then run `npm install` again

---

### **3. Test Python Service**

Open a new terminal and run:

```bash
# Navigate to Python service
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\python_service"

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
playwright install-deps chromium

# Run tests with coverage (must pass with ≥75%)
pytest test_main_comprehensive.py --cov=main --cov-report=html --cov-report=term --cov-fail-under=75

# Run pylint (must score ≥7.5/10)
pylint main.py --fail-under=7.5

# Run security scan
bandit -r . -ll
```

**Expected Results:**
- ✅ All pytest tests pass (30+ tests)
- ✅ Coverage ≥75%
- ✅ pylint score ≥7.5/10
- ✅ No high/critical security issues

**If it fails:**
- Playwright not installed? Run: `playwright install chromium`
- Import errors? Ensure all packages in requirements.txt are installed
- pylint score too low? Review the output and fix reported issues

---

## 🎨 **Quick Test All (One Command Per Service)**

### Frontend Quick Test
```bash
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\frontend" && npm install && npm run test:coverage && npm run lint && npm run build
```

### Backend Quick Test
```bash
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\backend" && npm install && npm run test:coverage && npm run lint
```

### Python Quick Test
```bash
cd "c:\Users\Vinod G R\Desktop\article-pdf-app\python_service" && pip install -r requirements.txt && playwright install chromium && pytest test_main_comprehensive.py --cov=main --cov-fail-under=75 && pylint main.py --fail-under=7.5 && bandit -r . -ll
```

---

## 📊 **View Coverage Reports**

After running tests with coverage, open these HTML files in your browser:

**Frontend:**
```
c:\Users\Vinod G R\Desktop\article-pdf-app\frontend\coverage\lcov-report\index.html
```

**Backend:**
```
c:\Users\Vinod G R\Desktop\article-pdf-app\backend\coverage\lcov-report\index.html
```

**Python:**
```
c:\Users\Vinod G R\Desktop\article-pdf-app\python_service\htmlcov\index.html
```

These show detailed line-by-line coverage information.

---

## 🐳 **Test with Docker (Optional but Recommended)**

Test the complete application:

```bash
# Navigate to project root
cd "c:\Users\Vinod G R\Desktop\article-pdf-app"

# Build all services
docker-compose build

# Start all services
docker-compose up

# In another terminal, check if services are running
docker-compose ps

# Test the application
# Open browser: http://localhost:3000
# Try converting a URL to PDF

# Stop services
docker-compose down
```

**Expected Results:**
- ✅ All 3 services build successfully
- ✅ All services start without errors
- ✅ Frontend accessible at http://localhost:3000
- ✅ Backend API responds at http://localhost:5000/health
- ✅ Python service responds at http://localhost:8000/health
- ✅ Can successfully convert a URL to PDF

---

## 🚀 **Testing on GitHub Actions**

### **Step 1: Push to GitHub**

```bash
# Navigate to project root
cd "c:\Users\Vinod G R\Desktop\article-pdf-app"

# Check git status
git status

# Add all files
git add .

# Commit with descriptive message
git commit -m "feat: Complete CI/CD pipeline implementation

- Implemented 6-stage CI/CD pipeline
- All tests pass with ≥75% coverage
- Zero lint errors, pylint score ≥7.5/10
- Security scanning configured
- Deployment artifact creation
- Complete documentation"

# Push to GitHub (replace 'main' with your branch name if different)
git push origin main
```

### **Step 2: Watch Pipeline Execute**

1. Go to your GitHub repository
2. Click on the **"Actions"** tab at the top
3. You'll see your workflow run starting
4. Click on the workflow run to see details

### **Step 3: Monitor Each Stage**

The pipeline will execute in this order:

**Stage 1: BUILD (Parallel - ~2-3 minutes)**
- 🏗️ Build Frontend
- 🏗️ Build Backend
- 🏗️ Build Python Service

**Stage 2: TEST (Parallel - ~3-5 minutes)**
- 🧪 Test Frontend
- 🧪 Test Backend
- 🧪 Test Python Service

**Stage 3: COVERAGE (Parallel - ~3-5 minutes)**
- 📊 Frontend Coverage (≥75%)
- 📊 Backend Coverage (≥75%)
- 📊 Python Coverage (≥75%)

**Stage 4: LINT (Parallel - ~2-3 minutes)**
- 🔍 Lint Frontend (Zero Errors)
- 🔍 Lint Backend (Zero Errors)
- 🔍 Lint Python (≥7.5/10)

**Stage 5: SECURITY (Parallel - ~2-3 minutes)**
- 🔒 Security Scan - Frontend
- 🔒 Security Scan - Backend
- 🔒 Security Scan - Python

**Stage 6: DEPLOYMENT ARTIFACT (~2-3 minutes)**
- 📦 Create Deployment Artifact

**Stage 7: DOCKER BUILD (Optional - ~5-10 minutes)**
- 🐳 Build Docker Images

**Total Pipeline Time: ~15-25 minutes**

### **Step 4: Check Results**

Click on each job to see:
- ✅ Green checkmark = Passed
- ❌ Red X = Failed (click to see error logs)
- 🟡 Yellow circle = Running

### **Step 5: Download Artifacts**

After pipeline completes successfully:

1. Scroll to the bottom of the workflow run page
2. Under **"Artifacts"** section, you'll see:
   - `deployment-artifact-complete` (ZIP file with everything)
   - `frontend-coverage-report` (HTML coverage report)
   - `backend-coverage-report` (HTML coverage report)
   - `python-coverage-report` (HTML coverage report)
   - `frontend-lint-report` (JSON)
   - `backend-lint-report` (JSON)
   - `python-lint-report` (JSON)
   - Various security reports

3. Click on any artifact to download it

---

## 🔍 **What Success Looks Like**

### **GitHub Actions Success:**
```
✅ build-frontend (1m 32s)
✅ build-backend (1m 28s)
✅ build-python (2m 15s)
✅ test-frontend (1m 45s)
✅ test-backend (1m 52s)
✅ test-python (2m 30s)
✅ coverage-frontend (1m 50s)
✅ coverage-backend (1m 48s)
✅ coverage-python (2m 25s)
✅ lint-frontend (1m 20s)
✅ lint-backend (1m 18s)
✅ lint-python (1m 35s)
✅ security-frontend (1m 10s)
✅ security-backend (1m 12s)
✅ security-python (1m 40s)
✅ create-deployment-artifact (2m 5s)
✅ docker-build (8m 30s)
✅ pipeline-summary (0m 15s)
```

### **Local Test Success:**
```
Frontend:
  Test Suites: 1 passed, 1 total
  Tests:       14 passed, 14 total
  Coverage:    Statements: 85.7% | Branches: 82.4% | Functions: 90.0% | Lines: 85.7%
  Lint:        0 errors, 0 warnings

Backend:
  Test Suites: 1 passed, 1 total
  Tests:       30 passed, 30 total
  Coverage:    Statements: 88.2% | Branches: 85.0% | Functions: 92.3% | Lines: 88.2%
  Lint:        0 errors, 0 warnings

Python:
  Tests:       30 passed
  Coverage:    88%
  Pylint:      8.5/10
  Bandit:      No issues found
```

---

## ❌ **Common Issues and Fixes**

### **Issue 1: Tests Fail Locally**

**Problem:** Tests won't run or fail immediately

**Solutions:**
```bash
# Clear node_modules and reinstall
cd frontend  # or backend
del /s /q node_modules
del package-lock.json
npm install

# For Python
cd python_service
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
playwright install chromium
```

### **Issue 2: Coverage Below 75%**

**Problem:** Coverage is 60-70%

**Solutions:**
- The comprehensive test files should provide ≥75% coverage
- If not, check that test files are being discovered:
  ```bash
  # Frontend
  npm test -- --listTests
  
  # Backend
  npm test -- --listTests
  
  # Python
  pytest --collect-only
  ```

### **Issue 3: Lint Errors**

**Problem:** ESLint or pylint failures

**Solutions:**
```bash
# Frontend/Backend - Auto-fix
npm run lint:fix

# Python - View specific errors
pylint main.py

# Common Python fixes:
# - Add docstrings to functions
# - Fix line length (max 120 chars)
# - Fix variable naming
```

### **Issue 4: GitHub Actions Fails but Local Works**

**Problem:** Pipeline fails on GitHub but works locally

**Common causes:**
1. **Missing files:** Check that all files are committed
   ```bash
   git status
   git add .
   git commit -m "Add missing files"
   git push
   ```

2. **Different dependencies:** Check package-lock.json is committed
   ```bash
   git add package-lock.json
   git commit -m "Add package-lock.json"
   git push
   ```

3. **Path issues:** GitHub uses Linux paths (`/`), not Windows (`\`)
   - The pipeline is already configured correctly for Linux

### **Issue 5: Playwright Not Working**

**Problem:** Playwright tests fail

**Solutions:**
```bash
cd python_service

# Uninstall and reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
playwright install-deps chromium

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

### **Issue 6: Docker Build Fails**

**Problem:** Docker services won't start

**Solutions:**
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose build --no-cache
docker-compose up
```

---

## 🎯 **Test Checklist**

Before pushing to GitHub, verify:

- [ ] Frontend tests pass locally
- [ ] Frontend coverage ≥75%
- [ ] Frontend lint passes (zero errors)
- [ ] Frontend builds successfully
- [ ] Backend tests pass locally
- [ ] Backend coverage ≥75%
- [ ] Backend lint passes (zero errors)
- [ ] Python tests pass locally
- [ ] Python coverage ≥75%
- [ ] Python pylint score ≥7.5/10
- [ ] Python bandit scan passes
- [ ] All files are committed to git
- [ ] Git repository is up to date

After pushing to GitHub:

- [ ] GitHub Actions workflow starts automatically
- [ ] All stages complete successfully
- [ ] Green checkmarks on all jobs
- [ ] Deployment artifact is created
- [ ] Can download and view coverage reports
- [ ] README badges are updated with correct repo URL

---

## 📞 **Getting Help**

### **Check Logs:**

**Local:**
```bash
# Verbose test output
npm test -- --verbose

# Python verbose
pytest -vv
```

**GitHub:**
1. Go to Actions tab
2. Click on failed workflow
3. Click on failed job
4. Expand failed step
5. Read error message

### **Debug Mode:**

Add this to your local test commands for more info:
```bash
# Frontend/Backend
npm test -- --verbose --no-coverage

# Python
pytest -vv --tb=long
```

---

## 🎓 **What You're Testing For**

Your pipeline validates:

1. **Functionality** - All code works as expected
2. **Quality** - Code coverage ≥75%
3. **Standards** - Lint scores meet requirements
4. **Security** - No vulnerabilities
5. **Buildability** - Can be deployed
6. **Documentation** - Everything is documented

**This demonstrates academic excellence and production-ready code!**

---

## 🚀 **Ready to Test?**

Start with Step 1 (Frontend) and work through each service. Once all local tests pass, push to GitHub and watch your pipeline succeed!

**Good luck! Your pipeline is production-ready.** 🎉
