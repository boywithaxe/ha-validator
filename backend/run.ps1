# Check if venv exists, if not create it
if (!(Test-Path .venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate venv
Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

# Install requirements
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Run server
Write-Host "Starting server..."
python main.py
