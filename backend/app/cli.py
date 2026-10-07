"""Operational CLI, run inside the backend container — not exposed over HTTP.

Used to create the first API key (and any subsequent ones): there is no
endpoint for this, since an endpoint to mint keys would itself need a key to
call it. Usage: `docker compose exec backend python -m app.cli create-api-key --name <name>`.
"""

import argparse

from app.application.api_key_service import ApiKeyService
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.repositories.api_key_repository import SqlAlchemyApiKeyRepository


def create_api_key(name: str) -> None:
    db = SessionLocal()
    try:
        service = ApiKeyService(SqlAlchemyApiKeyRepository(db))
        _, plaintext_key = service.create(name)
    finally:
        db.close()
    print(f"API key created for '{name}'. Store it now — it will not be shown again:\n")
    print(plaintext_key)


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-api-key", help="Create a new API key")
    create_parser.add_argument("--name", required=True, help="Label for this key's owner/use")

    args = parser.parse_args()
    if args.command == "create-api-key":
        create_api_key(args.name)


if __name__ == "__main__":
    main()
