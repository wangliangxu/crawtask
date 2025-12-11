from pydantic import BaseModel

class SystemSettings(BaseModel):
    inspection_interval: int
