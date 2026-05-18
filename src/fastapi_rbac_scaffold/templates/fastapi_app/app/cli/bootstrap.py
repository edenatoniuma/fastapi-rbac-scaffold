from __future__ import annotations

import argparse
import asyncio
import getpass

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, close_database
from app.model.iam import User
from app.security.password import hash_password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="app-bootstrap",
        description="Create or update the first platform administrator.",
    )
    parser.add_argument("--username", required=True)
    parser.add_argument("--email")
    parser.add_argument("--password")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Allow updating an existing user's platform-admin flag and password.",
    )
    return parser


async def bootstrap_platform_admin(
    *,
    username: str,
    password: str,
    email: str | None,
    update_existing: bool,
) -> None:
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.username == username))
        if user is not None and not update_existing:
            raise RuntimeError(
                "User already exists. Re-run with --yes to promote/update this user."
            )

        if user is None:
            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                is_platform_admin=True,
                status="active",
            )
            db.add(user)
        else:
            user.email = email or user.email
            user.hashed_password = hash_password(password)
            user.is_platform_admin = True
            user.status = "active"

        await db.commit()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    password = args.password or getpass.getpass("Password: ")
    if not password:
        raise SystemExit("Password cannot be empty.")

    async def runner() -> None:
        try:
            await bootstrap_platform_admin(
                username=args.username,
                password=password,
                email=args.email,
                update_existing=args.yes,
            )
        finally:
            await close_database()

    asyncio.run(runner())

    print(f"Platform administrator is ready: {args.username}")


if __name__ == "__main__":
    main()
