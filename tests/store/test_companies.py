from dataclasses import replace

import pytest

from finstats.container import Container
from finstats.store import CompaniesRepository
from testing import testdata

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.fixture(scope="session")
def company_repository(container: Container) -> CompaniesRepository:
    return container.resolve(CompaniesRepository)


async def test_empty_db_get_one_should_return_none(company_repository: CompaniesRepository) -> None:
    assert await company_repository.get_company(testdata.CompanyAlphaBank.id) is None


async def test_empty_db_get_many_should_return_empty_array(company_repository: CompaniesRepository) -> None:
    assert await company_repository.get_companies_by_id([x.id for x in testdata.TestCompanies]) == []


async def test_write_read_should_return_company(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    actual_company = await company_repository.get_company(testdata.CompanyAlphaBank.id)
    assert actual_company == testdata.CompanyAlphaBank


async def test_write_read_many_should_return_companies(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    actual = await company_repository.get_companies_by_id([x.id for x in testdata.TestCompanies])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestCompanies, key=lambda x: x.id)


async def test_update_should_return_updated(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    updated = replace(testdata.CompanyAlphaBank, title="Alfa Bank", www="alfa.example.com")
    await company_repository.save_companies([updated])
    actual = await company_repository.get_company(testdata.CompanyAlphaBank.id)
    assert actual == updated


async def test_get_companies_by_id_with_empty_input_should_return_empty(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    assert await company_repository.get_companies_by_id([]) == []


async def test_get_companies_by_id_with_unknown_ids_should_filter(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    actual = await company_repository.get_companies_by_id([testdata.CompanyAlphaBank.id, 999999])
    assert actual == [testdata.CompanyAlphaBank]


async def test_save_companies_with_empty_input_should_do_nothing(company_repository: CompaniesRepository) -> None:
    await company_repository.save_companies(testdata.TestCompanies)
    await company_repository.save_companies([])
    actual = await company_repository.get_companies_by_id([x.id for x in testdata.TestCompanies])
    assert sorted(actual, key=lambda x: x.id) == sorted(testdata.TestCompanies, key=lambda x: x.id)
