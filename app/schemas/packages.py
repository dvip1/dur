from pydantic import BaseModel, HttpUrl
from typing import Optional

class PackageBase(BaseModel):
    """
    Base schema for a package.
    Contains all the fields that are common for creation and reading.
    """
    name: str
    description: Optional[str] = None
    repo_url: HttpUrl # Using HttpUrl for automatic URL validation
    license: Optional[str] = None
    homepage: Optional[HttpUrl] = None
