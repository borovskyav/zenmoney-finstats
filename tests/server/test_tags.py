import uuid

import pytest

from client.client import FinstatsClient
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_get_tags_should_return_all_tags(client: FinstatsClient) -> None:
    tags = await client.get_tags()
    assert len(tags) == len(testdata.TestTags)
    expected_sorted = sorted(tags, key=lambda x: x.id)
    actual_sorted = sorted(testdata.TestTags, key=lambda x: x.id)
    expected_children_map: dict[uuid.UUID, list[uuid.UUID]] = {}
    for tag in testdata.TestTags:
        if tag.parent is not None:
            expected_children_map.setdefault(tag.parent, []).append(tag.id)
    for children in expected_children_map.values():
        children.sort()
    for i, expected_tag in enumerate(expected_sorted):
        assert actual_sorted[i].id == expected_tag.id
        assert actual_sorted[i].title == expected_tag.title
        assert actual_sorted[i].changed == expected_tag.changed
        assert actual_sorted[i].user == expected_tag.user
        assert actual_sorted[i].parent == expected_tag.parent
        assert actual_sorted[i].icon == expected_tag.icon
        assert actual_sorted[i].static_id == expected_tag.static_id
        assert actual_sorted[i].picture == expected_tag.picture
        assert actual_sorted[i].color == expected_tag.color
        assert actual_sorted[i].show_income == expected_tag.show_income
        assert actual_sorted[i].show_outcome == expected_tag.show_outcome
        assert actual_sorted[i].budget_income == expected_tag.budget_income
        assert actual_sorted[i].budget_outcome == expected_tag.budget_outcome
        assert actual_sorted[i].required == expected_tag.required
        assert actual_sorted[i].archive == expected_tag.archive
        expected_children = expected_children_map.get(expected_tag.id, [])
        assert sorted(expected_tag.children) == expected_children
