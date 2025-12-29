from services.ha_client import HomeAssistantClient
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check():
    client = HomeAssistantClient()
    logger.info("Fetching states...")
    states = await client.fetch_states()
    automations = [s for s in states if s['entity_id'].startswith('automation.')]
    logger.info(f"Found {len(automations)} automation entities in states.")
    if automations:
        print("Sample automation state:", automations[0])
    
    # Try getting config for one if possible? No direct API for that.
    
if __name__ == "__main__":
    asyncio.run(check())
