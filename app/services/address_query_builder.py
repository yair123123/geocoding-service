from app.config import Settings
from app.domain.schemas.geocode_request import GeocodeAddressRequest

_COUNTRY_NAMES: dict[str, str] = {
    "IL": "ישראל",
}


class AddressQueryBuilder:
    """Build deterministic provider query strings from structured addresses."""

    def __init__(self, settings: Settings) -> None:
        self._default_country = settings.default_country_code.upper()

    def normalize_request(self, request: GeocodeAddressRequest) -> GeocodeAddressRequest:
        country_code = (request.country_code or self._default_country).upper()
        return request.model_copy(update={"country_code": country_code})

    def build_query(self, request: GeocodeAddressRequest) -> str:
        normalized = self.normalize_request(request)

        street_and_number = " ".join(
            item for item in [normalized.street, normalized.house_number] if item and item.strip()
        ).strip()

        components = [street_and_number, normalized.city.strip(), self._country_display_name(normalized.country_code)]
        return ", ".join(component for component in components if component)

    def _country_display_name(self, country_code: str) -> str:
        return _COUNTRY_NAMES.get(country_code.upper(), country_code.upper())
