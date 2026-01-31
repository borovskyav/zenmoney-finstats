from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import UsersRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def user_repository(container: Container) -> UsersRepository:
    return container.resolve(UsersRepository)


async def test_empty_db_get_user_should_raise_value_error(user_repository: UsersRepository) -> None:
    with pytest.raises(ValueError, match="No users found"):
        await user_repository.get_user()


async def test_write_read_one_should_return_user(user_repository: UsersRepository) -> None:
    await user_repository.save_users([testdata.ActiveUser])
    actual_user = await user_repository.get_user()
    assert actual_user == testdata.ActiveUser


async def test_write_multiple_read_should_raise_value_error(user_repository: UsersRepository) -> None:
    await user_repository.save_users(testdata.TestUsers)
    with pytest.raises(ValueError, match="Expected exactly 1 user, found 2"):
        await user_repository.get_user()


async def test_update_user_should_be_updated(user_repository: UsersRepository) -> None:
    await user_repository.save_users([testdata.ActiveUser])
    updated_user = replace(testdata.ActiveUser, email="new_email@mail.com")
    await user_repository.save_users([updated_user])
    actual_user = await user_repository.get_user()
    assert actual_user == updated_user
