# Install dependencies
if (!(Test-Path node_modules)) {
    Write-Host "Installing dependencies..."
    npm install
}

# Start dev server
Write-Host "Starting frontend..."
npm run dev
