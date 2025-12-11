from pydantic import BaseModel
from typing import Optional

class NodeBase(BaseModel):
    name: str
    host: str
    port: Optional[int] = None
    username: Optional[str] = None
    ssh_key_path: Optional[str] = None
    is_center: bool = False

class NodeCreate(NodeBase):
    password: Optional[str] = None

class NodeUpdate(NodeBase):
    password: Optional[str] = None

class NodeResponse(NodeBase):
    id: int
    
    class Config:
        from_attributes = True
