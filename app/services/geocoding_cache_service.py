from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.config import Settings
from app.domain.schemas.geocode_request import GeocodeAddressRequest
from app.domain.schemas.geocode_response import GeocodeResult


@dataclass(slots=True)
class _CacheItem:
    result: GeocodeResult
    expires_at: datetime


class GeocodingCacheService:
    """Simple in-memory cache service for geocoding results."""

    def __init__(self, settings: Settings) -> None:
        self._enabled = settings.geocoding_cache_enabled
        self._ttl = timedelta(seconds=settings.geocoding_cache_ttl_seconds)
        self._store: dict[str, _CacheItem] = {}

    def make_key(self, request: GeocodeAddressRequest) -> str:
        country_code = (request.country_code or "").upper()
        parts = [
            request.city.strip().lower(),
            (request.street or "").strip().lower(),
            (request.house_number or "").strip().lower(),
            country_code,
        ]
        return "|".join(parts)

    def get(self, request: GeocodeAddressRequest) -> GeocodeResult | None:
        if not self._enabled:
            return None

        key = self.make_key(request)
        item = self._store.get(key)
        if item is None:
            return None
        if datetime.now(tz=timezone.utc) > item.expires_at:
            self._store.pop(key, None)
            return None
        return item.result

    def set(self, request: GeocodeAddressRequest, result: GeocodeResult) -> None:
        if not self._enabled:
            return
        key = self.make_key(request)
        self._store[key] = _CacheItem(result=result, expires_at=datetime.now(tz=timezone.utc) + self._ttl)
