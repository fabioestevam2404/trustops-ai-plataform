"""Operational CLI, run inside the backend container — not exposed over HTTP.

Used to create the first API key / user (and any subsequent ones): there is
no endpoint for this, since an endpoint to mint credentials would itself need
a credential to call it. Usage:
`docker compose exec backend python -m app.cli create-api-key --name <name>`
`docker compose exec backend python -m app.cli create-user --email <email> --role admin|viewer`
"""

import argparse
import getpass

from app.application.api_key_service import ApiKeyService
from app.application.user_service import UserService
from app.domain.user import EmailAlreadyExistsError, Role
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.api_key_repository import SqlAlchemyApiKeyRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository


def create_api_key(name: str) -> None:
    db = SessionLocal()
    try:
        service = ApiKeyService(SqlAlchemyApiKeyRepository(db))
        _, plaintext_key = service.create(name)
    finally:
        db.close()
    print(f"API key created for '{name}'. Store it now — it will not be shown again:\n")
    print(plaintext_key)


def create_user(email: str, role: str) -> None:
    password = getpass.getpass("Password: ")
    db = SessionLocal()
    try:
        service = UserService(SqlAlchemyUserRepository(db))
        try:
            service.create(email, password, Role(role))
        except EmailAlreadyExistsError:
            print(f"A user with email '{email}' already exists.")
            return
    finally:
        db.close()
    print(f"User '{email}' created with role '{role}'.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_key_parser = subparsers.add_parser("create-api-key", help="Create a new API key")
    create_key_parser.add_argument("--name", required=True, help="Label for this key's owner/use")

    create_user_parser = subparsers.add_parser("create-user", help="Create a new user")
    create_user_parser.add_argument("--email", required=True)
    create_user_parser.add_argument(
        "--role", required=True, choices=[role.value for role in Role]
    )

    args = parser.parse_args()
    if args.command == "create-api-key":
        create_api_key(args.name)
    elif args.command == "create-user":
        create_user(args.email, args.role)


if __name__ == "__main__":
    main()
