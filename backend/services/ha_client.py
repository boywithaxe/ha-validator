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

    async def fetch_automation_config_ws(self) -> List[Dict[str, Any]]:
        """
        Fetch automation config via WebSocket using the authenticated flow.
        """
        # 1. Determine WS URL (already in self.ws_url)
        
        async with websockets.connect(self.ws_url) as websocket:
            # 3. Auth Phase
            init_msg = await websocket.recv()
            if json.loads(init_msg).get("type") != "auth_required":
                 # In case we reconnect or something weird, but standard flow expects auth_required
                 pass 
            
            await websocket.send(json.dumps({
                "type": "auth",
                "access_token": settings.HA_TOKEN
            }))
            
            auth_response = await websocket.recv()
            auth_data = json.loads(auth_response)
            
            if auth_data.get("type") != "auth_ok":
                raise Exception(f"Auth failed: {auth_data.get('message')}")

            # 4. Command Phase
            msg_id = 1
            await websocket.send(json.dumps({
                "id": msg_id,
                "type": "config/automation/list"
            }))
            
            # Loop for response
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data.get("id") == msg_id:
                    if data.get("success"):
                        return data.get("result", [])
                    else:
                        raise Exception(f"Command failed: {data.get('error')}")

    async def fetch_related_items_ws(self, item_id: str) -> List[str]:
        """
        Fetch related items for a given item_id using search/related WS command.
        Returns a list of related entity_ids.
        """
        try:
             async with websockets.connect(self.ws_url) as websocket:
                # Auth
                await websocket.recv() 
                await websocket.send(json.dumps({"type": "auth", "access_token": settings.HA_TOKEN}))
                auth_resp = await websocket.recv()
                if json.loads(auth_resp).get("type") != "auth_ok":
                    return []

                # Command
                msg_id = 999
                await websocket.send(json.dumps({
                    "id": msg_id,
                    "type": "search/related",
                    "item_type": "entity",
                    "item_id": item_id
                }))
                
                while True:
                    resp = await websocket.recv()
                    data = json.loads(resp)
                    if data.get("id") == msg_id:
                        if data.get("success"):
                            # Result is like: {"automation": [...], "script": [...], "entity": [...]}
                            # We want to flatten this into a list of IDs
                            result = data.get("result", {})
                            related_ids = []
                            for category in result.values():
                                if isinstance(category, list):
                                    related_ids.extend(category)
                            return related_ids
                        return []
        except Exception as e:
            logger.warning(f"Failed to fetch related items for {item_id}: {e}")
            return []

    async def fetch_automations(self) -> List[Dict[str, Any]]:
        """
        Fetch automations.
        Try WebSocket config/automation/list first.
        If that fails, fallback to filtering /api/states and using search/related.
        """
        # Try WebSocket Config first
        try:
            return await self.fetch_automation_config_ws()
        except Exception as e:
            logger.warning(f"WS Automation fetch failed: {e}")
            
        # Fallback: Filter states & search/related
        logger.info("Falling back to states + search/related for automations")
        states = await self.fetch_states()
        
        automations_list = []
        for s in states:
            if s['entity_id'].startswith("automation."):
                automations_list.append({
                    "id": s.get('attributes', {}).get('id', s['entity_id']),
                    "alias": s.get('attributes', {}).get('friendly_name'),
                    "entity_id": s['entity_id'] 
                })

        # Augment with related items (capped concurrency)
        sem = asyncio.Semaphore(10)
        
        async def fetch_with_related(auto_obj):
            async with sem:
                # search/related needs the entity_id (e.g. automation.foo) not the internal id
                related = await self.fetch_related_items_ws(auto_obj["entity_id"])
                auto_obj["related"] = related
                return auto_obj

        tasks = [fetch_with_related(a) for a in automations_list]
        return await asyncio.gather(*tasks)
