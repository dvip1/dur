# In app/schemas/packages.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import datetime

from app.schemas.packages import PackageOut


class PackageVersionOut(BaseModel):
    version: str
    release: int
    source_url: HttpUrl
    git_tag: str
    published_at: datetime.datetime

    class Config:
        from_attributes = True 

class PackageDetailOut(PackageOut): 
    latest_version: Optional[PackageVersionOut] = None