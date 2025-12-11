from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class TaskStatus(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"

class RuleType(str, enum.Enum):
    KEYWORD = "keyword"
    LATENCY = "latency"
    REGEX = "regex"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"))
    name = Column(String, index=True)
    log_file_path = Column(String)
    start_command = Column(String, nullable=True)
    stop_command = Column(String, nullable=True)
    
    status = Column(Enum(TaskStatus), default=TaskStatus.UNKNOWN)
    health_status = Column(Enum(HealthStatus), default=HealthStatus.UNKNOWN)
    last_check_time = Column(DateTime, nullable=True)
    last_log_time = Column(DateTime, nullable=True)
    check_interval = Column(Integer, default=60) # seconds
    is_enabled = Column(Integer, default=1) # 1=online, 0=offline (boolean-ish)
    
    # Relationships
    node = relationship("Node", back_populates="tasks")
    health_rules = relationship("HealthRule", back_populates="task", cascade="all, delete-orphan")

class HealthRule(Base):
    __tablename__ = "health_rules"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    rule_type = Column(Enum(RuleType))
    rule_content = Column(String) # For keyword or regex pattern

    task = relationship("Task", back_populates="health_rules")
