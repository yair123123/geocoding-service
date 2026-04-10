from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeocodeAddressRequest(BaseModel):
    """Single structured address payload for geocoding."""

    model_config = ConfigDict(str_strip_whitespace=True)

    city: str = Field(min_length=1, max_length=120)
    street: str | None = Field(default=None, max_length=120)
    house_number: str | None = Field(default=None, max_length=32)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.upper()


class BatchGeocodeRequest(BaseModel):
    addresses: list[GeocodeAddressRequest] = Field(min_length=1, max_length=100)
