# app/services/factory.py
from fastapi import HTTPException, status
from pydantic import HttpUrl

from .providers import VCSProviderBase, InvalidRepoException
from .github import GithubService

def get_vcs_provider(repo_url: HttpUrl) -> VCSProviderBase:
    """
    Factory function that returns the correct VCS provider instance
    based on the repository URL.
    """
    try:
        if "github.com" in str(repo_url):
            return GithubService(repo_url=repo_url)
        # In the future, you'd add:
        # elif "gitlab.com" in str(repo_url):
        #     return GitlabService(repo_url=repo_url)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported repository provider. Only GitHub is supported."
            )
    except InvalidRepoException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))