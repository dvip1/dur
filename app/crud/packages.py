from sqlalchemy.orm import Session
from app.schemas.packages import PackageBase  
from app.database.models.packages import Package, PackageVersion

def create_package(db:Session, package: PackageBase, user_id: int )->Package: 
    """
     Create a new package in the database.

    Args:
        db (Session): SQLAlchemy session.
        package (schema.package.PackageBase): Pydantic schema with package input data.
        user_id (int): ID of the user creating the package.

    Returns:
        Package: The newly created Package object.
    """
    db_package = Package(name=package.name, description= package.description, repo_url= str(package.repo_url), 
                         license = package.license, 
                         homepage= str(package.homepage),
                         created_by = user_id 
                         )
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package


def create_with_versions(
    db: Session, *, package_in: PackageBase, versions_data: list, user_id: int
) -> Package:
    """
    Creates a Package and all its associated PackageVersion records in a single transaction.
    """
    # Use .model_dump() to get a dictionary
    package_data = package_in.model_dump()

    # Explicitly convert HttpUrl fields to strings before saving
    package_data['repo_url'] = str(package_data['repo_url'])
    if package_data.get('homepage'):
        package_data['homepage'] = str(package_data['homepage'])

    # The rest of your logic can now work with the dictionary as expected
    db_package = Package(**package_data, created_by=user_id)
    db.add(db_package)

    for version_info in versions_data:
        db_version = PackageVersion(
            package=db_package,
            version=version_info.metadata.version,
            release=version_info.metadata.release,
            source_url=str(version_info.metadata.source),
            git_tag=version_info.git_tag,
            package_metadata=version_info.metadata.model_dump(mode='json')
        )
        db.add(db_version)

    db.commit()
    db.refresh(db_package)
    return db_package