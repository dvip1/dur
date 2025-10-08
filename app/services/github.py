# app/services/github.py
import httpx
import re
from typing import List
from pydantic import HttpUrl
from app.core.config import settings # We'll add the GitHub token here next
from .providers import VCSProviderBase, VersionInfo, InvalidRepoException

# The GitHub API endpoint
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com"

class GithubService(VCSProviderBase):
    """Implementation of the VCS provider for GitHub."""

    def _parse_url(self):
        # Extracts "owner/repo_name" from a GitHub URL
        match = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?$", str(self.repo_url))
        if not match:
            raise InvalidRepoException("Invalid GitHub repository URL format.")
        self.owner, self.repo_name = match.groups()

    async def get_versions(self) -> List[VersionInfo]:
        if not self.owner or not self.repo_name:
            raise InvalidRepoException("Repo URL not parsed correctly.")

        tags_url = f"{GITHUB_API_BASE_URL}/repos/{self.owner}/{self.repo_name}/tags"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {settings.GITHUB_ACCESS_TOKEN}"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(tags_url, headers=headers)
                response.raise_for_status() # Raises HTTPError for 4xx/5xx responses
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise InvalidRepoException("Repository not found on GitHub.")
                else:
                    raise InvalidRepoException(f"GitHub API Error: {e.response.text}")
            except httpx.RequestError as e:
                raise InvalidRepoException(f"Failed to connect to GitHub: {e}")

        tags_data = response.json()
        valid_versions: List[VersionInfo] = []
        for tag in tags_data:
            tag_name = tag.get("name")
            if tag_name and self.is_valid_version_tag(tag_name):
                valid_versions.append(VersionInfo(version_string=tag_name, git_tag=tag_name))

        return valid_versions

    async def get_raw_file_content(self, tag: str, file_path: str) -> str:
        """Fetches the raw content of a file from the repo at a specific tag."""
        raw_url = f"{GITHUB_RAW_BASE_URL}/{self.owner}/{self.repo_name}/{tag}/{file_path}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(raw_url)
                response.raise_for_status() # Raise error for 4xx/5xx
                return response.text
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                # Be specific: did the tag not exist or the file? For simplicity, we'll generalize.
                    raise InvalidRepoException(f"File '{file_path}' not found at tag '{tag}'.")
                else:
                    raise InvalidRepoException(f"GitHub API Error: {e.response.text}")