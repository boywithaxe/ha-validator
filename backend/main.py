import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import settings

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "configured_ha_url": settings.HA_URL
    }

@app.get("/validate-ha")
def validate_ha():
    headers = {
        "Authorization": f"Bearer {settings.HA_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        # Pinging the API root to check connectivity and auth
        response = requests.get(f"{settings.HA_URL}/api/", headers=headers, timeout=5)
        response.raise_for_status()
        return {
            "status": "ok", 
            "message": "Connected to Home Assistant", 
            "details": response.json()
        }
    except requests.RequestException as e:
        return {
            "status": "error", 
            "message": f"Failed to connect to Home Assistant: {str(e)}",
            "ha_url": settings.HA_URL
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
