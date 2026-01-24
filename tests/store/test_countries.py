from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import CountriesRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def country_repository(container: Container) -> CountriesRepository:
    return container.resolve(CountriesRepository)


async def test_empty_db_get_one_should_return_none(country_repository: CountriesRepository) -> None:
    assert await country_repository.get_country(testdata.CountryRussia.id) is None


async def test_empty_db_get_many_should_return_empty_array(country_repository: CountriesRepository) -> None:
    assert await country_repository.get_countries_by_id([x.id for x in testdata.TestCountries]) == []


async def test_write_read_should_return_country(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    actual_country = await country_repository.get_country(testdata.CountryRussia.id)
    assert actual_country == testdata.CountryRussia


async def test_write_read_many_should_return_countries(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    actual = await country_repository.get_countries_by_id([x.id for x in testdata.TestCountries])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestCountries, key=lambda x: x.id)


async def test_update_should_return_updated(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    updated = replace(testdata.CountryRussia, title="Russian Federation")
    await country_repository.save_countries([updated])
    actual = await country_repository.get_country(testdata.CountryRussia.id)
    assert actual == updated


async def test_get_countries_by_id_empty_input_returns_empty(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    assert await country_repository.get_countries_by_id([]) == []


async def test_get_countries_by_id_filters_unknown_ids(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    actual = await country_repository.get_countries_by_id([testdata.CountryRussia.id, 999999])
    assert actual == [testdata.CountryRussia]


async def test_save_countries_empty_noop(country_repository: CountriesRepository) -> None:
    await country_repository.save_countries(testdata.TestCountries)
    await country_repository.save_countries([])
    actual = await country_repository.get_countries_by_id([x.id for x in testdata.TestCountries])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestCountries, key=lambda x: x.id)
