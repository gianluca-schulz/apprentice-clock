import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User


async def test_saved_user_can_be_read_back(session_factory):
    user = User(first_name="Peter", last_name="Maffay", email="tabaluga@peter.com", password_hash="6742069")
    async with session_factory() as session:
        session.add(user)
        await session.commit()

    async with session_factory() as session:
        user_copy = await session.get(User, user.id)
        assert user_copy is not None
        assert user_copy.email == user.email


async def test_second_user_with_identical_email_gets_rejected_by_database(session_factory):
    user1 = User(first_name="Uwe", last_name="Uwenson", email="Uwe123@uwe.com", password_hash="asdjhakghw")
    user2 = User(first_name="Uwe", last_name="Peterson", email="Uwe123@uwe.com", password_hash="arhrhrhr")
    async with session_factory() as session:
        session.add(user1)
        await session.commit()
    async with session_factory() as session:
        session.add(user2)
        with pytest.raises(IntegrityError):
            await session.commit()
