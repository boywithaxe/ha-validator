# HA Validator

This is a monorepo containing the `ha-validator` project.

## Project Structure

- **root**: Contains project-wide configuration and documentation.
- **backend/**: The Python backend application (FastAPI).
- **frontend/**: The Node.js frontend application (React + Vite).

## Environment Setup

To run the application locally, you need to configure environment variables for both the backend and frontend.

### Backend

1. Navigate to the `backend/` directory.
2. Copy `.env.example` to a new file named `.env`:
   ```sh
   cp .env.example .env
   ```
   *(On Windows PowerShell: `Copy-Item .env.example .env`)*
3. Edit `.env` and provide your Home Assistant URL and Token:
   - `HA_URL`: The URL of your Home Assistant instance (e.g., `http://192.168.1.10:8123`)
   - `HA_TOKEN`: Your Long-Lived Access Token.

### Frontend

1. Navigate to the `frontend/` directory.
2. Copy `.env.example` to a new file named `.env`:
   ```sh
   cp .env.example .env
   ```
3. Edit `.env` if your backend is running on a different port/host:
   - `VITE_API_URL`: The base URL of the backend API (default: `http://localhost:8000`).

## Getting Started

### Backend
Run the initialization script (Windows):
```powershell
cd backend
.\run.ps1
```

### Frontend
Run the initialization script (Windows):
```powershell
cd frontend
.\run.ps1
```
