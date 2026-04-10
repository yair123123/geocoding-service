import logging
from urllib.parse import quote

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    """Raised when the geocoding provider returns unexpected errors."""


class MapboxGeocodingClient:
    """Thin HTTP client for the Mapbox forward geocoding API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.mapbox_geocoding_base_url.rstrip("/")
        self._timeout = settings.http_timeout_seconds
        self._access_token = settings.mapbox_access_token

    async def geocode(self, query: str, country_code: str) -> dict:
        if not self._access_token:
            raise ProviderError("Mapbox access token is missing")

        encoded_query = quote(query, safe="")
        url = f"{self._base_url}/{encoded_query}.json"
        params = {
            "access_token": self._access_token,
            "country": country_code.lower(),
            "limit": 1,
            "autocomplete": "false",
            "language": "he",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.exception("Mapbox request timed out")
            raise ProviderError("Provider timeout") from exc
        except httpx.HTTPStatusError as exc:
            logger.exception("Mapbox request failed with status=%s", exc.response.status_code)
            raise ProviderError("Provider HTTP error") from exc
        except httpx.HTTPError as exc:
            logger.exception("Mapbox request failed")
            raise ProviderError("Provider communication error") from exc

        payload = response.json()
        if not isinstance(payload, dict):
            raise ProviderError("Malformed provider payload")
        return payload
