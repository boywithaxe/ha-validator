from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel, field_validator

class Entity(BaseModel):
    id: str
    state: str
    attributes: Dict[str, Any]

class Automation(BaseModel):
    id: str
    alias: Optional[str] = None
    trigger: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    condition: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    action: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    related: Optional[List[str]] = []

    @classmethod
    def ensure_list(cls, v: Any) -> List[Any]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        return [v]

    @field_validator('trigger', 'condition', 'action', mode='before')
    @classmethod
    def validate_list_fields(cls, v: Any) -> List[Any]:
        return cls.ensure_list(v)
