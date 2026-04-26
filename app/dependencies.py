from functools import lru_cache

from fastapi import Depends

from app.clients.mapbox_geocoding_client import MapboxGeocodingClient
from app.config import Settings, get_settings
from app.services.address_query_builder import AddressQueryBuilder
from app.services.geocoding_cache_service import GeocodingCacheService
from app.services.geocoding_service import GeocodingService


@lru_cache(maxsize=1)
def get_query_builder() -> AddressQueryBuilder:
    return AddressQueryBuilder(settings=get_settings())


@lru_cache(maxsize=1)
def get_mapbox_client() -> MapboxGeocodingClient:
    return MapboxGeocodingClient(settings=get_settings())


@lru_cache(maxsize=1)
def get_geocoding_cache_service() -> GeocodingCacheService:
    return GeocodingCacheService(settings=get_settings())


def get_geocoding_service(
    query_builder: AddressQueryBuilder = Depends(get_query_builder),
    provider_client: MapboxGeocodingClient = Depends(get_mapbox_client),
    cache_service: GeocodingCacheService = Depends(get_geocoding_cache_service),
) -> GeocodingService:
    return GeocodingService(
        query_builder=query_builder,
        provider_client=provider_client,
        cache_service=cache_service,
    )


def get_app_settings() -> Settings:
    return get_settings()