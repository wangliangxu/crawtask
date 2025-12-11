from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class RuleType(str, Enum):
    KEYWORD = "keyword"
    LATENCY = "latency"
    REGEX = "regex"

# HealthRule Schemas
class HealthRuleBase(BaseModel):
    rule_type: RuleType
    rule_content: str

class HealthRuleCreate(HealthRuleBase):
    pass

class HealthRuleResponse(HealthRuleBase):
    id: int
    task_id: int

    class Config:
        from_attributes = True

# Task Schemas
class TaskBase(BaseModel):
    name: str
    log_file_path: str
    start_command: Optional[str] = None
    stop_command: Optional[str] = None
    check_interval: Optional[int] = 60
    is_enabled: Optional[bool] = True

class TaskCreate(TaskBase):
    node_ids: List[int]
    health_rules: List[HealthRuleCreate] = []

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    log_file_path: Optional[str] = None
    start_command: Optional[str] = None
    stop_command: Optional[str] = None
    check_interval: Optional[int] = None
    is_enabled: Optional[bool] = None
    health_rules: Optional[List[HealthRuleCreate]] = None

class TaskResponse(TaskBase):
    id: int
    node_id: Optional[int] = None
    status: Optional[TaskStatus] = TaskStatus.UNKNOWN
    health_status: Optional[HealthStatus] = HealthStatus.UNKNOWN
    last_check_time: Optional[datetime] = None
    last_log_time: Optional[datetime] = None
    health_rules: List[HealthRuleResponse] = []
    is_enabled: bool = True

    class Config:
        from_attributes = True
