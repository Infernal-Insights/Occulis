from pydantic import BaseModel
from typing import Dict, Any


class RigStatus(BaseModel):
    name: str
    stats: Dict[str, Any]
