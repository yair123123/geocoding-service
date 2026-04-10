import asyncio

from app.config import Settings
from app.domain.schemas.geocode_request import GeocodeAddressRequest
from app.domain.schemas.geocode_response import GeocodeResult
from app.services.address_query_builder import AddressQueryBuilder
from app.services.geocoding_cache_service import GeocodingCacheService
from app.services.geocoding_service import GeocodingService


class StubClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls = 0

    async def geocode(self, query: str, country_code: str) -> dict:  # noqa: ARG002
        self.calls += 1
        return self.payload


def _settings() -> Settings:
    return Settings(MAPBOX_ACCESS_TOKEN="test-token")


def _service(payload: dict) -> tuple[GeocodingService, StubClient, GeocodingCacheService]:
    settings = _settings()
    client = StubClient(payload)
    cache = GeocodingCacheService(settings)
    service = GeocodingService(AddressQueryBuilder(settings), client, cache)
    return service, client, cache


def test_normalization_strong_result() -> None:
    payload = {
        "features": [
            {
                "id": "place.123",
                "center": [34.887, 32.091],
                "place_name": "הרצל 10, פתח תקווה, ישראל",
                "text": "הרצל",
                "address": "10",
            }
        ]
    }
    service, _, _ = _service(payload)
    request = GeocodeAddressRequest(city="פתח תקווה", street="הרצל", house_number="10", country_code="IL")

    response = asyncio.run(service.geocode_address(request))

    assert response.success is True
    assert response.result is not None
    assert response.result.match_quality == "high"
    assert response.result.partial_match is False


def test_normalization_partial_result() -> None:
    payload = {
        "features": [
            {
                "id": "place.456",
                "center": [34.78, 32.08],
                "place_name": "דיזנגוף, תל אביב, ישראל",
                "text": "דיזנגוף",
            }
        ]
    }
    service, _, _ = _service(payload)
    request = GeocodeAddressRequest(city="תל אביב", street="דיזנגוף", house_number="50", country_code="IL")

    response = asyncio.run(service.geocode_address(request))

    assert response.success is True
    assert response.result is not None
    assert response.result.match_quality in {"medium", "low"}
    assert response.warnings


def test_no_result_response() -> None:
    service, _, _ = _service({"features": []})
    request = GeocodeAddressRequest(city="תל אביב")

    response = asyncio.run(service.geocode_address(request))

    assert response.success is False
    assert response.result is None
    assert response.warnings == ["No geocoding result found"]


def test_cache_hit_behavior() -> None:
    payload = {
        "features": [
            {
                "id": "place.cache",
                "center": [34.887, 32.091],
                "place_name": "הרצל 10, פתח תקווה, ישראל",
                "text": "הרצל",
                "address": "10",
            }
        ]
    }
    service, client, cache = _service(payload)
    request = GeocodeAddressRequest(city="פתח תקווה", street="הרצל", house_number="10", country_code="IL")

    first = asyncio.run(service.geocode_address(request))
    second = asyncio.run(service.geocode_address(request))

    assert first.success is True and second.success is True
    assert isinstance(cache.get(request), GeocodeResult)
    assert client.calls == 1
