# routes/packages/create.py

from app.routes.packages.packages import router
from app.core.routes_version1 import Routes
from app.schemas.packages import PackageOut, PackageBase
from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.schemas import user as user_schema
from sqlalchemy.orm import Session
from app.crud.packages import create_package as create
from sqlite3 import IntegrityError
from app import dependencies as deps
from app.services.factory import get_vcs_provider
from app.services.providers import InvalidRepoException

@router.post(
    Routes.Packages.default, 
    response_model=PackageOut, 
    status_code=status.HTTP_201_CREATED,
    # Add explicit responses for better documentation
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Conflict Error",
            "content": {
                "application/json": {
                    "example": {"detail": "Package with this name or repo_url already exists."}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {"detail": "An unexpected error occurred."}
                }
            },
        }
    }
)

async def create_package_route(
    data: PackageBase,
    current_user: user_schema.UserPublic = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Create a new package.

    This endpoint allows an authenticated user to register a new package in the system.
    The package name and repository URL must be unique.

    - **name**: The name of the package (must be unique).
    - **repo_url**: The repository URL for the package (must be unique).
    - **description**: A short description of the package.
    """
    # 1. Get the correct VCS provider based on the repo URL
    provider = get_vcs_provider(repo_url=data.repo_url)

    try:
        # 2. Fetch versions from the provider's API and log them
        print(f"Fetching versions for {data.repo_url}...")
        versions = await provider.get_versions()

        if not versions:
            print("No valid version tags found in the repository.")
        else:
            print("--- Found Valid Versions ---")
            for version in versions:
                print(f"  Version String: {version.version_string}")
                print(f"  Git Tag: {version.git_tag}")
            print("--------------------------")

        # --- Your original database logic remains below ---
        new_package = create(
            db=db,
            package=data,
            user_id=current_user.id,
        )
        return new_package

    except InvalidRepoException as e:
        # This new exception handles errors from our service (e.g., repo not found)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Package with this name or repo_url already exists.",
        )

    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the package.",
        )