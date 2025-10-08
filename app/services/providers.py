# app/services/providers.py
import re
from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

# A Pydantic model to standardize the version data we get back from any provider
class VersionInfo(BaseModel):
    version_string: str
    git_tag: str

# Custom exception for clarity
class InvalidRepoException(Exception):
    pass

# The "contract" for all future Version Control System (VCS) providers
class VCSProviderBase(ABC):
    """Abstract base class for a Version Control System provider."""

    def __init__(self, repo_url: HttpUrl):
        self.repo_url = repo_url
        self.owner: Optional[str] = None
        self.repo_name: Optional[str] = None
        self._parse_url()

    @abstractmethod
    def _parse_url(self):
        """Parses the repo_url to extract owner and repo name."""
        raise NotImplementedError

    @abstractmethod
    async def get_versions(self) -> List[VersionInfo]:
        """Fetches tags from the repository and returns them as a list of VersionInfo."""
        raise NotImplementedError

    @staticmethod
    def is_valid_version_tag(tag_name: str) -> bool:
        """
        A simple check for semantic-like versioning (e.g., v1.0.0, 1.0, 2.3.4-alpha).
        You can make this more strict if needed.
        """
        # This regex matches patterns like: 1.0, 1.2.3, v1.2.3, 1.2.3-rc1
        semver_pattern = re.compile(r'^v?(\d+)(\.\d+){1,2}(-[a-zA-Z0-9.-]+)?$')
        return semver_pattern.match(tag_name) is not None