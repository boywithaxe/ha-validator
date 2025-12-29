import httpx
from fastapi import HTTPException
from config import settings
from typing import List, Dict, Any

class HomeAssistantClient:
    def __init__(self):
        self.base_url = settings.HA_URL.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {settings.HA_TOKEN}",
            "Content-Type": "application/json",
        }

    async def _get(self, endpoint: str) -> Any:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=f"Home Assistant API error: {e.response.text}"
                )
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to connect to Home Assistant: {str(e)}"
                )

    async def fetch_states(self) -> List[Dict[str, Any]]:
        """Fetch all states from /api/states"""
        return await self._get("/api/states")

    async def fetch_automations(self) -> List[Dict[str, Any]]:
        """
        Fetch automations config from /api/config/automation
        Note: This endpoint might not be available depending on HA setup/permissions.
        Often valid automation configs are found in states or specialized registry endpoints.
        If /api/config/automation fails or is not what we want, we might filter /api/states for 'automation.*'.
        For now, implementing as requested.
        """
        return await self._get("/api/config/automation")
