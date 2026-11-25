import pytest

from app.models.user import User


@pytest.fixture()
async def saved_user(session_factory) -> User:
    user = User(first_name="testname", last_name="testlastname", email="test@email.com", password_hash="passwordhash")
    async with session_factory() as session:
        session.add(user)
        await session.commit()
    return user
