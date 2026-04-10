from pydantic import BaseModel

from app.domain.schemas.geocode_request import GeocodeAddressRequest


class GeocodeResult(BaseModel):
    lat: float
    lon: float
    formatted_address: str
    provider: str
    provider_place_id: str | None
    match_quality: str
    partial_match: bool


class GeocodeResponse(BaseModel):
    success: bool
    query: GeocodeAddressRequest
    result: GeocodeResult | None
    warnings: list[str]
    error: str | None


class BatchGeocodeResponse(BaseModel):
    success: bool
    results: list[GeocodeResponse]
    warnings: list[str]
    error: str | None
