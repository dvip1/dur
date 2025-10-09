# app/services/github.py
import json
import httpx
import re
from typing import List
from pydantic import BaseModel, HttpUrl, ValidationError
from app.core.config import settings # We'll add the GitHub token here next
from .providers import VCSProviderBase, VersionInfo, InvalidRepoException

# The GitHub API endpoint
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_RAW_BASE_URL = "https://raw.githubusercontent.com"


# In app/services/providers.py
class PackageMetadata(BaseModel):
    name: str
    version: str
    release: int
    source: HttpUrl



class ParsedVersion(BaseModel):
    git_tag: str
    metadata: PackageMetadata

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

    async def _get_tree_for_tag(self, tag_name: str, client: httpx.AsyncClient) -> List[str]:
        """Helper method to fetch the file list for a specific tag."""
        tree_url = f"{GITHUB_API_BASE_URL}/repos/{self.owner}/{self.repo_name}/git/trees/{tag_name}?recursive=1"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {settings.GITHUB_ACCESS_TOKEN}"
        }
        try:
            response = await client.get(tree_url, headers=headers)
            response.raise_for_status()
            tree_data = response.json().get("tree", [])
            return [item["path"] for item in tree_data]
        except httpx.HTTPStatusError as e:
            # If a tag doesn't have a valid tree (rare), we'll get a 404 or 409
            print(f"Warning: Could not fetch tree for tag {tag_name}. Status: {e.response.status_code}")
            return []

    async def discover_and_parse_versions(self) -> List[ParsedVersion]:
        """
        Efficiently discovers all tags, checks for 'dur.json' using the Git
        Trees API, and then fetches and parses the file for valid versions.
        """
        if not self.owner or not self.repo_name:
            raise InvalidRepoException("Repo URL not parsed correctly.")

        # 1. First, get all the tags for the repository
        tags_url = f"{GITHUB_API_BASE_URL}/repos/{self.owner}/{self.repo_name}/tags"
        headers = { "Authorization": f"token {settings.GITHUB_ACCESS_TOKEN}" }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(tags_url, headers=headers)
                response.raise_for_status()
                tags_data = response.json()
            except httpx.HTTPStatusError:
                raise InvalidRepoException("Repository not found or access denied.")

            # 2. Now, efficiently process each tag
            parsed_versions: List[ParsedVersion] = []
            for tag in tags_data:
                tag_name = tag.get("name")
                if not tag_name:
                    continue

                # 3. Efficiently check if 'dur.json' exists using the Trees API
                file_tree = await self._get_tree_for_tag(tag_name, client)
                if "dur.json" not in file_tree:
                    print(f"Skipping tag {tag_name}: dur.json not found in tree.")
                    continue
                
                # 4. Only if it exists, fetch its content
                try:
                    content = await self.get_raw_file_content(tag_name, "dur.json")
                    metadata_dict = json.loads(content)
                    metadata = PackageMetadata(**metadata_dict)
                    
                    parsed_versions.append(
                        ParsedVersion(git_tag=tag_name, metadata=metadata)
                    )
                    print(f"Successfully parsed dur.json for tag {tag_name}")
                except (json.JSONDecodeError, ValidationError, InvalidRepoException) as e:
                    print(f"Warning: Could not parse dur.json for tag {tag_name}. Reason: {e}")
                    continue

        return parsed_versions

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