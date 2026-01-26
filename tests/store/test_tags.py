import uuid
from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import TagsRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def tags_repository(container: Container) -> TagsRepository:
    return container.resolve(TagsRepository)


async def test_empty_db_get_one_should_return_none(tags_repository: TagsRepository) -> None:
    assert await tags_repository.get_tag(testdata.TagSelfCare.id) is None


async def test_empty_db_get_many_should_return_empty_array(tags_repository: TagsRepository) -> None:
    assert await tags_repository.get_tags_by_id([x.id for x in testdata.TestTags]) == []


async def test_empty_db_get_all_should_return_empty_array(tags_repository: TagsRepository) -> None:
    assert await tags_repository.get_tags() == []


async def test_write_read_should_return_tag(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    actual = await tags_repository.get_tag(testdata.TagSelfCare.id)
    assert actual == testdata.TagSelfCare


async def test_write_read_many_should_return_tags(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    actual = await tags_repository.get_tags_by_id([x.id for x in testdata.TestTags])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestTags, key=lambda x: x.id)


async def test_get_all_should_return_tags(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    actual = await tags_repository.get_tags()
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestTags, key=lambda x: x.id)


async def test_get_children_tags_should_return_children(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    actual = await tags_repository.get_children_tags(testdata.TagSelfCare.id)
    assert sorted(actual, key=lambda x: x.id) == [testdata.TagHealth]


async def test_update_should_return_updated(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    updated = replace(testdata.TagSelfCare, title="Self care")
    await tags_repository.save_tags([updated])
    actual = await tags_repository.get_tag(testdata.TagSelfCare.id)
    assert actual == updated


async def test_get_tags_by_id_with_empty_input_should_return_empty(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    assert await tags_repository.get_tags_by_id([]) == []


async def test_get_tags_by_id_with_unknown_ids_should_filter(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    actual = await tags_repository.get_tags_by_id([testdata.TagSelfCare.id, uuid.uuid4()])
    assert actual == [testdata.TagSelfCare]


async def test_save_tags_with_empty_input_should_do_nothing(tags_repository: TagsRepository) -> None:
    await tags_repository.save_tags(testdata.TestTags)
    await tags_repository.save_tags([])
    actual = await tags_repository.get_tags_by_id([x.id for x in testdata.TestTags])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestTags, key=lambda x: x.id)
