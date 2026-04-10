import logging

from app.clients.mapbox_geocoding_client import MapboxGeocodingClient, ProviderError
from app.domain.schemas.geocode_request import GeocodeAddressRequest
from app.domain.schemas.geocode_response import GeocodeResponse, GeocodeResult
from app.services.address_query_builder import AddressQueryBuilder
from app.services.geocoding_cache_service import GeocodingCacheService

logger = logging.getLogger(__name__)


class GeocodingService:
    """Coordinates query building, provider calls, normalization, and caching."""

    def __init__(
        self,
        query_builder: AddressQueryBuilder,
        provider_client: MapboxGeocodingClient,
        cache_service: GeocodingCacheService,
    ) -> None:
        self._query_builder = query_builder
        self._provider_client = provider_client
        self._cache_service = cache_service

    async def geocode_address(self, request: GeocodeAddressRequest) -> GeocodeResponse:
        normalized_query = self._query_builder.normalize_request(request)
        cached = self._cache_service.get(normalized_query)
        if cached is not None:
            return GeocodeResponse(success=True, query=normalized_query, result=cached, warnings=[], error=None)

        query_text = self._query_builder.build_query(normalized_query)
        try:
            raw_payload = await self._provider_client.geocode(query=query_text, country_code=normalized_query.country_code or "IL")
        except ProviderError:
            return GeocodeResponse(
                success=False,
                query=normalized_query,
                result=None,
                warnings=[],
                error="Geocoding provider is unavailable",
            )

        response = self._normalize_response(normalized_query, raw_payload)
        if response.success and response.result is not None:
            self._cache_service.set(normalized_query, response.result)
        return response

    def _normalize_response(self, request: GeocodeAddressRequest, payload: dict) -> GeocodeResponse:
        features = payload.get("features")
        if not isinstance(features, list) or not features:
            return GeocodeResponse(
                success=False,
                query=request,
                result=None,
                warnings=["No geocoding result found"],
                error=None,
            )

        top = features[0]
        try:
            center = top["center"]
            lon = float(center[0])
            lat = float(center[1])
            formatted_address = str(top.get("place_name") or "")
            provider_place_id = top.get("id")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            logger.exception("Malformed provider feature payload")
            return GeocodeResponse(
                success=False,
                query=request,
                result=None,
                warnings=[],
                error="Malformed provider payload",
            )

        match_quality = self._match_quality(request, top)
        partial_match = match_quality != "high"

        warnings: list[str] = []
        if partial_match:
            warnings.append("Result is partial or weak match")

        result = GeocodeResult(
            lat=lat,
            lon=lon,
            formatted_address=formatted_address,
            provider="mapbox",
            provider_place_id=str(provider_place_id) if provider_place_id else None,
            match_quality=match_quality,
            partial_match=partial_match,
        )
        return GeocodeResponse(success=True, query=request, result=result, warnings=warnings, error=None)

    def _match_quality(self, request: GeocodeAddressRequest, feature: dict) -> str:
        text_blob = " ".join(
            [
                str(feature.get("place_name", "")),
                str(feature.get("text", "")),
                str(feature.get("address", "")),
            ]
        ).lower()

        city_ok = request.city.lower() in text_blob
        street_ok = (request.street or "").lower() in text_blob if request.street else False
        house_ok = (request.house_number or "").lower() in text_blob if request.house_number else False

        if city_ok and street_ok and (house_ok or not request.house_number):
            return "high"
        if city_ok and (street_ok or not request.street):
            return "medium"
        return "low"
