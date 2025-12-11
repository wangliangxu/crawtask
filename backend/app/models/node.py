from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    host = Column(String, index=True)
    port = Column(Integer, nullable=True)
    username = Column(String)
    encrypted_password = Column(String)
    ssh_key_path = Column(String, nullable=True)
    is_center = Column(Integer, default=0) # 0 for False, 1 for True (using Integer for SQLite boolean compatibility/simplicity)

    tasks = relationship("Task", back_populates="node", cascade="all, delete-orphan")

