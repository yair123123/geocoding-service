from fastapi.testclient import TestClient

from app.dependencies import get_geocoding_service
from app.domain.schemas.geocode_response import GeocodeResponse, GeocodeResult
from app.main import app


class StubService:
    async def geocode_address(self, request):  # noqa: ANN001
        return GeocodeResponse(
            success=True,
            query=request,
            result=GeocodeResult(
                lat=32.091,
                lon=34.887,
                formatted_address="הרצל 10, פתח תקווה, ישראל",
                provider="mapbox",
                provider_place_id="place.123",
                match_quality="high",
                partial_match=False,
            ),
            warnings=[],
            error=None,
        )


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_geocode_address_smoke() -> None:
    app.dependency_overrides[get_geocoding_service] = lambda: StubService()
    client = TestClient(app)

    response = client.post(
        "/v1/geocode/address",
        json={"city": "פתח תקווה", "street": "הרצל", "house_number": "10", "country_code": "IL"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["result"]["provider"] == "mapbox"


def test_geocode_batch_smoke() -> None:
    app.dependency_overrides[get_geocoding_service] = lambda: StubService()
    client = TestClient(app)

    response = client.post(
        "/v1/geocode/batch",
        json={
            "addresses": [
                {"city": "פתח תקווה", "street": "הרצל", "house_number": "10", "country_code": "IL"},
                {"city": "תל אביב", "street": "דיזנגוף", "house_number": "50", "country_code": "IL"},
            ]
        },
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["results"]) == 2
