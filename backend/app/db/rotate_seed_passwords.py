"""
app/db/rotate_seed_passwords.py
-------------------------------
One-off remediation: give every account created by seed_aarambh a new random
password and revoke its sessions.

Older versions of the seed script used passwords that were published in the
repo (README, seed script, frontend bundle). Any deployment seeded with them
still has those logins active. Run this once, from the Render shell:

    python -m app.db.rotate_seed_passwords

New passwords are printed once and never stored — save them, then have each
person change theirs via /auth/change-password.
"""

import asyncio
import secrets
from datetime import UTC, datetime

from sqlalchemy import select, update

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserSession

SEEDED_DOMAIN = "@aarambhinstitute.com"


async def rotate() -> None:
    async with AsyncSessionLocal() as session:
        users = (
            await session.execute(
                select(User).where(User.email.like(f"%{SEEDED_DOMAIN}"), User.deleted_at.is_(None))
            )
        ).scalars().all()

        if not users:
            print("No seeded accounts found.")
            return

        now = datetime.now(UTC)
        for user in users:
            new_password = secrets.token_urlsafe(16)
            user.password_hash = hash_password(new_password)
            user.failed_login_attempts = 0
            user.locked_until = None
            await session.execute(
                update(UserSession)
                .where(UserSession.user_id == user.id, UserSession.revoked_at.is_(None))
                .values(revoked_at=now)
            )
            print(f"{user.email:45} {user.role:10} {new_password}")

        await session.commit()
        print(f"\nRotated {len(users)} account(s) and revoked their sessions.")


if __name__ == "__main__":
    asyncio.run(rotate())
