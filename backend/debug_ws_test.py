import asyncio
import websockets
import json
import os
from config import settings

async def test_ws_commands():
    url = settings.HA_URL.replace("http://", "ws://").replace("https://", "wss://") + "/api/websocket"
    token = settings.HA_TOKEN
    
    
    # helper for ids
    class IdGen:
        def __init__(self):
            self.id = 0
        def next(self):
            self.id += 1
            return self.id
            
    id_gen = IdGen()

    async with websockets.connect(url, max_size=None) as websocket:
        # Auth
        await websocket.recv() # auth_required
        await websocket.send(json.dumps({"type": "auth", "access_token": token}))
        auth_resp = await websocket.recv()
        print(f"Auth Response: {auth_resp}")
        
        # Helper to send/recv
        async def send_cmd(cmd_type, **kwargs):
            msg_id = id_gen.next()
            msg = {"id": msg_id, "type": cmd_type}
            msg.update(kwargs)
            print(f"\nSending: {msg['type']} (id={msg_id})")
            await websocket.send(json.dumps(msg))
            resp = await websocket.recv()
            data = json.loads(resp)
            success = data.get("success")
            error = data.get("error")
            print(f"Result: Success={success}, Error={error}")
            if success:
                 print(f"Result Data Snippet: {str(data.get('result'))[:200]}")
            return data

        # 0. Fetch States to get a real automation ID
        print("\nFetching states...")
        await websocket.send(json.dumps({"id": id_gen.next(), "type": "get_states"}))
        resp = await websocket.recv()
        states = json.loads(resp).get("result", [])
        
        real_automation_id = None
        for s in states:
            if s['entity_id'].startswith("automation."):
                real_automation_id = s['entity_id']
                break
        
        print(f"Found automation: {real_automation_id}")

        if real_automation_id:
             # 4. Test search/related (Alternative approach?)
            await send_cmd("search/related", item_type="entity", item_id=real_automation_id) 

            # 5. Try config/automation/get (Guess)
            await send_cmd("config/automation/get", entity_id=real_automation_id)

if __name__ == "__main__":
    asyncio.run(test_ws_commands())
