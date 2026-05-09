from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, index=True)
    file_name = Column(String(255))
    file_url = Column(String(500))
    format = Column(String(20))  # pdf, docx
    report_type = Column(String(50))  # summary, detailed
    status = Column(String(50), default="processing")  # processing, completed, failed
    progress = Column(Integer, default=0)
    message = Column(Text)
    size_bytes = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
