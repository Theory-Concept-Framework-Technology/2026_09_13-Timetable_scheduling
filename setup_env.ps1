```powershell
# ==========================================
# Python 3.7 Project Environment Setup
# ==========================================

$PythonVersion = "3.7"
$VenvPath = ".venv"

Write-Host ""
Write-Host "==========================================" 
Write-Host " Python 3.7 Environment Setup"
Write-Host "=========================================="
Write-Host ""

# ------------------------------------------
# 1. Check whether Python 3.7 is installed
# ------------------------------------------

Write-Host "Checking for Python 3.7..."

$pythonCheck = py -3.7 --version 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Python 3.7 was not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.7 first."
    Write-Host "Then run this script again."
    exit 1
}

Write-Host "Found: $pythonCheck" -ForegroundColor Green

# ------------------------------------------
# 2. Remove old virtual environment
# ------------------------------------------

if (Test-Path $VenvPath) {
    Write-Host ""
    Write-Host "Removing existing virtual environment..."

    Remove-Item -Recurse -Force $VenvPath

    Write-Host "Old environment removed." -ForegroundColor Green
}

# ------------------------------------------
# 3. Create virtual environment using Python 3.7
# ------------------------------------------

Write-Host ""
Write-Host "Creating virtual environment with Python 3.7..."

py -3.7 -m venv $VenvPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

Write-Host "Virtual environment created." -ForegroundColor Green

# ------------------------------------------
# 4. Activate virtual environment
# ------------------------------------------

Write-Host ""
Write-Host "Activating virtual environment..."

& ".\$VenvPath\Scripts\Activate.ps1"

# ------------------------------------------
# 5. Upgrade pip
# ------------------------------------------

Write-Host ""
Write-Host "Upgrading pip..."

python -m pip install --upgrade pip

# ------------------------------------------
# 6. Install project dependencies
# ------------------------------------------

if (Test-Path "requirements.txt") {

    Write-Host ""
    Write-Host "Installing dependencies from requirements.txt..."

    python -m pip install -r requirements.txt

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Dependency installation failed." -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "Dependencies installed successfully." -ForegroundColor Green

}
else {
    Write-Host ""
    Write-Host "WARNING: requirements.txt not found." -ForegroundColor Yellow
}

# ------------------------------------------
# 7. Verify Python version
# ------------------------------------------

Write-Host ""
Write-Host "=========================================="
Write-Host " Environment Ready"
Write-Host "=========================================="

Write-Host ""
Write-Host "Python version:"
python --version

Write-Host ""
Write-Host "Python location:"
Get-Command python | Select-Object -ExpandProperty Source

Write-Host ""
Write-Host "Virtual environment:"
Write-Host $VenvPath

Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
```
