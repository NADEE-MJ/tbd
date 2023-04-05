from asyncio import run
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import get_password_hash
from src.db.db import get_session
from src.models.account import Account
from src.models.user import User


async def main() -> None:
    session: AsyncSession = [i async for i in get_session()][0]
    user = User(
        full_name="Admin Admin",
        email="admin@test.com",
        password=get_password_hash("Test1234!"),
        is_active=True,
        created_at=datetime.now(),
        last_login=datetime.now(),
    )
    session.add(user)

    accounts = [
        Account(name="Wells Fargo", account_type="checking", created_at=datetime.now(), user_id=1),
        Account(name="BOA", account_type="savings", created_at=datetime.now(), user_id=1),
    ]

    session.add_all(accounts)

    await session.commit()


run(main())
