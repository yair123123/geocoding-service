from fastapi import APIRouter, Depends

from app.dependencies import get_geocoding_service
from app.domain.schemas.geocode_request import BatchGeocodeRequest, GeocodeAddressRequest
from app.domain.schemas.geocode_response import BatchGeocodeResponse, GeocodeResponse
from app.services.geocoding_service import GeocodingService

router = APIRouter(prefix="/v1/geocode", tags=["geocode"])


@router.post("/address", response_model=GeocodeResponse)
async def geocode_address(
    request: GeocodeAddressRequest,
    service: GeocodingService = Depends(get_geocoding_service),
) -> GeocodeResponse:
    return await service.geocode_address(request)


@router.post("/batch", response_model=BatchGeocodeResponse)
async def geocode_batch(
    request: BatchGeocodeRequest,
    service: GeocodingService = Depends(get_geocoding_service),
) -> BatchGeocodeResponse:
    results: list[GeocodeResponse] = []
    for address in request.addresses:
        results.append(await service.geocode_address(address))

    return BatchGeocodeResponse(success=True, results=results, warnings=[], error=None)
