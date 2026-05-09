from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AutoReportRequest(BaseModel):
    start_date: str
    end_date: str
    format: str = "pdf"  # pdf or docx
    include_charts: bool = True
    report_type: str = "summary"  # summary or detailed


class AutoReportPreview(BaseModel):
    estimated_pages: int
    sections: list
    data_summary: dict


class AutoReportResponse(BaseModel):
    report_id: str
    file_url: str
    file_name: str
    format: str
    created_at: datetime
    size_bytes: Optional[int] = None


class AutoReportStatus(BaseModel):
    report_id: str
    status: str  # processing, completed, failed
    progress: int
    message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
