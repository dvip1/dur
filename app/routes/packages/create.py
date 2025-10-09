# routes/packages/create.py

from app.routes.packages.packages import router
from app.core.routes_version1 import Routes
from app.schemas.packages import PackageOut, PackageBase
from fastapi import APIRouter, HTTPException, Request, Depends, status
from app.schemas import user as user_schema
from sqlalchemy.orm import Session
from app.crud.packages import create_package as create, create_with_versions
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

# In create.py

# ... your other imports

async def create_package_route(
    data: PackageBase,
    current_user: user_schema.UserPublic = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Create a new package by discovering all valid versions from its recipe repository.
    ...
    """
    provider = get_vcs_provider(repo_url=data.repo_url)

    try:
        print(f"Discovering versions for {data.repo_url}...")
        valid_versions = await provider.discover_and_parse_versions()

        if not valid_versions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid versions with a 'dur.json' file were found in the repository."
            )
        
        print(f"Found {len(valid_versions)} valid versions to import.")
        
        new_package = create_with_versions(
            db=db,
            package_in=data,
            versions_data=valid_versions,
            user_id=current_user.id
        )
        return new_package

    except InvalidRepoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Package with this name or repo_url already exists.",
        )

    except HTTPException as e:
        raise e
    # -----------------------
    except Exception as e:
        db.rollback()
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        )