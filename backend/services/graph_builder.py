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
            
            # Process Related (Generic Fallback)
            if auto.related:
                for related_id in auto.related:
                    # We don't know direction, but usually it's input/output.
                    # For visualization, just linking them is enough.
                    # We'll treat them as "related" edge.
                    # To avoid duplicates if trigger/action exists (unlikely in this fallback), we could check.
                    if not self.graph.has_edge(auto.id, related_id) and not self.graph.has_edge(related_id, auto.id):
                         self.graph.add_edge(related_id, auto.id, relation="related") # Default direction? Or undirected?
                         # Let's assume Entity -> Automation for now, or just make it bidirectional?
                         # For simplicity and preventing cycles in layout, let's just do Entity -> Auto (like trigger)
                         # But wait, actions are Auto -> Entity.
                         # Since we don't know, maybe we just add one way?
                         pass
                    
                    # Actually, let's just add it as "related" from Entity -> Automation implies dependency?
                    # Or Automation -> Entity implies impact?
                    # Let's add Entity -> Automation to keep it consistent with "inputs".
                    self.graph.add_edge(related_id, auto.id, relation="related")
                    
        return self.graph

    def to_react_flow_format(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Convert NetworkX graph to React Flow JSON format.
        """
        if self.graph.number_of_nodes() == 0:
            return {"nodes": [], "edges": []}
            
        # 1. Compute Layout (scale positions)
        pos = nx.spring_layout(self.graph, k=0.15, iterations=50)
        
        nodes = []
        for node_id, coords in pos.items():
            # Get node attributes
            attrs = self.graph.nodes[node_id]
            
            # Format Node
            nodes.append({
                "id": node_id,
                "data": {
                    "label": attrs.get("alias") or node_id, # Use alias if available, else ID
                    "type": attrs.get("type", "default"),
                    "details": attrs
                },
                "position": {
                    "x": coords[0] * 2000, # Scale up for better visibility
                    "y": coords[1] * 2000 
                },
                "type": "default" # React Flow node type
            })
            
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "id": f"e-{u}-{v}",
                "source": u,
                "target": v,
                "label": data.get("relation"),
                "animated": True if data.get("relation") == "trigger" else False
            })
            
        return {"nodes": nodes, "edges": edges}
