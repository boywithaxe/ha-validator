import httpx
import websockets
import json
import asyncio
import logging
from fastapi import HTTPException
from config import settings
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HomeAssistantClient:
    def __init__(self):
        self.base_url = settings.HA_URL.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {settings.HA_TOKEN}",
            "Content-Type": "application/json",
        }
        # Derive WS URL from HTTP URL
        self.ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"

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
        Fetch automations.
        Try WebSocket config/automation/list first.
        If that fails (unknown command), fallback to filtering /api/states for 'automation.*'.
        """
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # 1. Auth Phase
                await websocket.recv() # auth_required
                await websocket.send(json.dumps({
                    "type": "auth",
                    "access_token": settings.HA_TOKEN
                }))
                auth_conn = await websocket.recv()
                if json.loads(auth_conn).get("type") != "auth_ok":
                    raise Exception("Auth failed")

                # 2. Fetch Automations Config
                msg_id = 99
                await websocket.send(json.dumps({
                    "id": msg_id,
                    "type": "config/automation/list"
                }))
                
                resp = await websocket.recv()
                data = json.loads(resp)
                
                if data.get("id") == msg_id and data.get("success"):
                    return data.get("result", [])
                
                logger.warning(f"WS config/automation/list failed/empty: {data}")
                # Fallback to states
        except Exception as e:
            logger.warning(f"WS Automation fetch failed: {e}")
            
        # Fallback: Filter states
        logger.info("Falling back to states for automations")
        states = await self.fetch_states()
        automations = []
        for s in states:
            if s['entity_id'].startswith("automation."):
                # Map state object to Automation schema fields (best effort)
                auto = {
                    "id": s.get('attributes', {}).get('id', s['entity_id']),
                    "alias": s.get('attributes', {}).get('friendly_name'),
                    # Triggers/Actions are not available in state
                }
                automations.append(auto)
        return automations
