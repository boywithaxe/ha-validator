from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel

class Entity(BaseModel):
    id: str
    state: str
    attributes: Dict[str, Any]

class Automation(BaseModel):
    id: str
    alias: Optional[str] = None
    trigger: Union[List[Dict[str, Any]], Dict[str, Any]]
    condition: Union[List[Dict[str, Any]], Dict[str, Any]] = []
    action: Union[List[Dict[str, Any]], Dict[str, Any]]
