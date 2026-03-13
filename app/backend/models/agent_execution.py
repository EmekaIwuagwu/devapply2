from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.backend.database.connection import Base


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    strategy_id = Column(String(36), ForeignKey("strategies.id"))
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    status = Column(String(50))  # Running, Completed, Failed
    jobs_found = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    errors = Column(JSON)
    execution_logs = Column(Text)

    user = relationship("User", backref="agent_executions")
    strategy = relationship("Strategy", backref="agent_executions")
