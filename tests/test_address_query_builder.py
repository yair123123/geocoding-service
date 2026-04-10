from app.config import Settings
from app.domain.schemas.geocode_request import GeocodeAddressRequest
from app.services.address_query_builder import AddressQueryBuilder


def _settings() -> Settings:
    return Settings(MAPBOX_ACCESS_TOKEN="test-token")


def test_query_builder_full_address() -> None:
    builder = AddressQueryBuilder(_settings())
    request = GeocodeAddressRequest(city="פתח תקווה", street="הרצל", house_number="10", country_code="IL")

    assert builder.build_query(request) == "הרצל 10, פתח תקווה, ישראל"


def test_query_builder_without_house_number() -> None:
    builder = AddressQueryBuilder(_settings())
    request = GeocodeAddressRequest(city="פתח תקווה", street="הרצל", country_code="IL")

    assert builder.build_query(request) == "הרצל, פתח תקווה, ישראל"


def test_query_builder_city_only_defaults_country() -> None:
    builder = AddressQueryBuilder(_settings())
    request = GeocodeAddressRequest(city="תל אביב")

    assert builder.build_query(request) == "תל אביב, ישראל"
