import asyncio
import logging
from services.ha_client import HomeAssistantClient
from services.graph_builder import SystemGraph
from schemas import Entity, Automation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify():
    print("--- Starting Verification ---")
    client = HomeAssistantClient()
    
    # 1. Fetch Data
    print("Fetching states...")
    states = await client.fetch_states()
    print(f"Fetched {len(states)} states.")
    
    print("Fetching automations (with fallback)...")
    automations_data = await client.fetch_automations()
    print(f"Fetched {len(automations_data)} automations.")
    
    # 2. Check for 'related' data
    count_with_related = 0
    total_related_items = 0
    for a in automations_data:
        related = a.get("related", [])
        if related:
            count_with_related += 1
            total_related_items += len(related)
            
    print(f"Automations with related items: {count_with_related}/{len(automations_data)}")
    print(f"Total related items found: {total_related_items}")
    
    if count_with_related > 0:
        example = next(a for a in automations_data if a.get("related"))
        print(f"Example related data for {example['id']}: {example['related']}")

    # 3. Build Graph
    print("\nBuilding Graph...")
    entities = []
    for s in states:
        if "entity_id" in s:
            entities.append(Entity(id=s["entity_id"], state=s["state"], attributes=s["attributes"]))
            
    automations = []
    for a in automations_data:
        automations.append(Automation(**a))
        
    builder = SystemGraph()
    graph = builder.build(entities, automations)
    
    print(f"Graph Nodes: {graph.number_of_nodes()}")
    print(f"Graph Edges: {graph.number_of_edges()}")
    
    # 4. Check for 'related' edges
    related_edges = [d for u, v, d in graph.edges(data=True) if d.get("relation") == "related"]
    print(f"Edges with relation='related': {len(related_edges)}")
    
    if not related_edges and count_with_related > 0:
        print("WARNING: Related items found but no edges created! Check logic.")

if __name__ == "__main__":
    asyncio.run(verify())
