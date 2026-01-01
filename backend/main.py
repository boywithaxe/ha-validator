import asyncio
import logging
import requests
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import settings
from services.ha_client import HomeAssistantClient
from services.graph_builder import SystemGraph
from schemas import Entity, Automation
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@app.post("/api/ingest")
async def ingest_data():
    client = HomeAssistantClient()
    
    try:
        # Fetch data in parallel
        states_task = client.fetch_states()
        automations_task = client.fetch_automations()
        
        # We use return_exceptions=True to allow partial success if needed, 
        # but here we'll just gather and check results.
        # Note: automation api might fail if not supported, we'll handle that.
        results = await asyncio.gather(states_task, automations_task, return_exceptions=True)
        
        raw_states = results[0]
        raw_automations = results[1]
        
        # Handle exceptions
        if isinstance(raw_states, Exception):
            raise HTTPException(status_code=500, detail=f"Failed to fetch states: {str(raw_states)}")
        
        # Automations might fail gracefully if endpoint doesn't exist
        valid_automations_list = []
        if isinstance(raw_automations, Exception):
            logger.warning(f"Failed to fetch automations config: {str(raw_automations)}")
            raw_automations = [] # Fallback
        
        # DEBUG: Dump raw automations to file to inspect structure
        import json
        with open("debug_automations.json", "w") as f:
            json.dump(raw_automations, f, indent=2, default=str)

        # Validate Entities
        valid_entities: List[Entity] = []
        for state_data in raw_states:
            try:
                # Ensure simple mapping: entity_id -> id
                if "entity_id" in state_data and "id" not in state_data:
                    state_data["id"] = state_data["entity_id"]
                
                entity = Entity(**state_data)
                valid_entities.append(entity)
            except ValidationError as e:
                logger.warning(f"Skipping invalid entity {state_data.get('entity_id', 'unknown')}: {e}")

        # Validate Automations
        # Note: /api/config/automation returns a list of config objects if successful
        # They usually have 'id', 'alias', etc.
        for auto_data in raw_automations:
            try:
                automation = Automation(**auto_data)
                valid_automations_list.append(automation)
            except ValidationError as e:
                 logger.warning(f"Skipping invalid automation {auto_data.get('id', 'unknown')}: {e}")

        # Build Graph
        graph_builder = SystemGraph()
        graph_builder.build(valid_entities, valid_automations_list)
        graph_data = graph_builder.to_react_flow_format()

        return {
            "status": "success",
            "entity_count": len(valid_entities),
            "automation_count": len(valid_automations_list),
            "data": {
                "entities": [e.model_dump() for e in valid_entities],
                "automations": [a.model_dump() for a in valid_automations_list],
                "graph": graph_data
            }
        }

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph")
async def get_graph():
    # Helper to re-fetch and build graph on demand
    # In a real app we might cache this or use the last ingested data.
    # For now, we'll re-run a quick fetch (or just states fallback) to build it.
    client = HomeAssistantClient()
    try:
        states = await client.fetch_states() # Fallback source
        # We need to map these to entities/automations
        entities = []
        automations = []
        for s in states:
            if s['entity_id'].startswith('automation.'):
                 automations.append(Automation(
                     id=s['attributes'].get('id', s['entity_id']),
                     alias=s['attributes'].get('friendly_name')
                 ))
            entities.append(Entity(
                id=s['entity_id'], 
                state=s['state'], 
                attributes=s['attributes']
            ))
            
        graph_builder = SystemGraph()
        graph_builder.build(entities, automations)
        return graph_builder.to_react_flow_format()
    except Exception as e:
        logger.error(f"Graph fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
