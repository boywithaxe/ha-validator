import networkx as nx
from typing import List, Dict, Any, Set, Union
from schemas import Entity, Automation

class SystemGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def _find_entity_ids(self, data: Any) -> Set[str]:
        """Recursively find 'entity_id' values in a dictionary or list."""
        entity_ids = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "entity_id":
                    if isinstance(value, str):
                        entity_ids.add(value)
                    elif isinstance(value, list):
                        entity_ids.update(value)
                else:
                    entity_ids.update(self._find_entity_ids(value))
        elif isinstance(data, list):
            for item in data:
                entity_ids.update(self._find_entity_ids(item))
                
        return entity_ids

    def build(self, entities: List[Entity], automations: List[Automation]) -> nx.DiGraph:
        self.graph.clear()
        
        # Add Entities as Nodes
        for entity in entities:
            self.graph.add_node(entity.id, type="entity", state=entity.state)
            
        # Add Automations as Nodes and Edges
        for auto in automations:
            self.graph.add_node(auto.id, type="automation", alias=auto.alias)
            
            # Process Triggers (Entity -> Automation)
            if auto.trigger:
                trigger_entities = self._find_entity_ids(auto.trigger)
                for ent_id in trigger_entities:
                    # Only add edge if entity node exists? 
                    # Or add implicit node? HA allows referencing non-existent entities.
                    # We will add the edge. NetworkX automagically adds nodes if missing, 
                    # but we might mark them as 'unknown' if we cared.
                    self.graph.add_edge(ent_id, auto.id, relation="trigger")
            
            # Process Actions (Automation -> Entity)
            if auto.action:
                action_entities = self._find_entity_ids(auto.action)
                for ent_id in action_entities:
                    self.graph.add_edge(auto.id, ent_id, relation="action")
                    
        return self.graph
