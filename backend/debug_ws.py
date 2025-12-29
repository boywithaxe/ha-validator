import asyncio
import websockets
import json
import logging
from config import settings

logging.basicConfig(level=logging.INFO)

async def test_ws():
    url = settings.HA_URL.rstrip('/').replace("http", "ws") + "/api/websocket"
    async with websockets.connect(url) as ws:
        # Auth
        await ws.recv() # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": settings.HA_TOKEN}))
        await ws.recv() # auth_ok
        
        # Try List again
        print("Sending config/automation/list")
        await ws.send(json.dumps({"id": 1, "type": "config/automation/list"}))
        res = await ws.recv()
        print(f"List Result: {res[:200]}...") # Truncate
        
        # Try getting config for specific ID
        # Looking at the earlier output: id='1719605623417'
        test_id = '1719605623417'
        print(f"Sending config/automation/get for {test_id}")
        # There isn't a documented command, guessing...
        # Some sources suggest `config/automation/config`?
        # Or maybe it's accessible via `config_entries`?
        await ws.send(json.dumps({"id": 2, "type": "config/automation/config", "automation_id": test_id}))
        res = await ws.recv()
        print(f"Config Result: {res}")

if __name__ == "__main__":
    asyncio.run(test_ws())
