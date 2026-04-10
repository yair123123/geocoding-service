# geocoding-service

Standalone internal HTTP microservice for structured address geocoding. It only accepts generic address fields and returns normalized geocoding results. It has no coupling to rides, telephony, dispatching, Twilio, or business workflow concepts.

## Tech stack

- Python 3.12
- FastAPI
- Pydantic v2 + pydantic-settings
- httpx
- pytest

## Project structure

- `app/main.py` - FastAPI app entry point
- `app/config.py` - environment-based configuration
- `app/dependencies.py` - dependency wiring
- `app/api/routes/health.py` - health endpoint
- `app/api/routes/geocode.py` - geocoding endpoints
- `app/clients/mapbox_geocoding_client.py` - Mapbox HTTP client
- `app/services/address_query_builder.py` - deterministic address query building
- `app/services/geocoding_service.py` - orchestration + normalization
- `app/services/geocoding_cache_service.py` - cache abstraction (in-memory)
- `app/domain/schemas/geocode_request.py` - request schemas
- `app/domain/schemas/geocode_response.py` - response schemas
- `app/utils/logging.py` - logging setup

## Endpoints

### Health

`GET /health`

Response:

```json
{"status": "ok"}
```

### Primary geocode endpoint

`POST /v1/geocode/address`

Request:

```json
{
  "city": "פתח תקווה",
  "street": "הרצל",
  "house_number": "10",
  "country_code": "IL"
}
```

Success response example:

```json
{
  "success": true,
  "query": {
    "city": "פתח תקווה",
    "street": "הרצל",
    "house_number": "10",
    "country_code": "IL"
  },
  "result": {
    "lat": 32.091,
    "lon": 34.887,
    "formatted_address": "הרצל 10, פתח תקווה, ישראל",
    "provider": "mapbox",
    "provider_place_id": "place.123",
    "match_quality": "high",
    "partial_match": false
  },
  "warnings": [],
  "error": null
}
```

No result example:

```json
{
  "success": false,
  "query": {
    "city": "פתח תקווה",
    "street": "הרצל",
    "house_number": "10",
    "country_code": "IL"
  },
  "result": null,
  "warnings": ["No geocoding result found"],
  "error": null
}
```

### Optional batch endpoint

`POST /v1/geocode/batch`

Request:

```json
{
  "addresses": [
    {
      "city": "פתח תקווה",
      "street": "הרצל",
      "house_number": "10",
      "country_code": "IL"
    },
    {
      "city": "תל אביב",
      "street": "דיזנגוף",
      "house_number": "50",
      "country_code": "IL"
    }
  ]
}
```

Returns results in the same input order.

## Query building rules

- Deterministic composition from `street + house_number + city + country`
- default `country_code` to `IL`
- omits empty fields cleanly (no malformed commas)
- supports city-only queries

## Match quality heuristics

- `high`: city + street + house number match (or no house number requested)
- `medium`: city + street match, house number uncertain/missing
- `low`: only city or vague match

Partial/weak matches include warnings.

## Caching

- `GeocodingCacheService` is a pluggable abstraction
- Current implementation: in-memory dictionary with TTL
- Caches successful normalized results

## Environment variables

- `MAPBOX_ACCESS_TOKEN` (required in real runs)
- `MAPBOX_GEOCODING_BASE_URL` (default `https://api.mapbox.com/geocoding/v5/mapbox.places`)
- `HTTP_TIMEOUT_SECONDS` (default `5.0`)
- `DEFAULT_COUNTRY_CODE` (default `IL`)
- `GEOCODING_CACHE_ENABLED` (default `true`)
- `GEOCODING_CACHE_TTL_SECONDS` (default `86400`)
- `APP_ENV` (default `development`)
- `APP_HOST` (default `0.0.0.0`)
- `APP_PORT` (default `8080`)
- `LOG_LEVEL` (default `INFO`)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Run tests

```bash
pytest -q
```

## Design boundaries

- This service is geocoding-only.
- It intentionally has no knowledge of telephony, rides, customers, drivers, dispatch, or business flows.
- Public API response is normalized and stable even if provider implementation changes later.
