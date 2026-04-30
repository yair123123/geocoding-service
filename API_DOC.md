# API Spec (Geocoding Service)

מסמך קצר של ה־API בפועל לפי הקוד הקיים.

Base URL: `http://<host>:<port>`

---

## 1) Health Check

### `GET /health`

בדיקת זמינות בסיסית של הסרוויס.

**Response 200**

```json
{
  "status": "ok"
}
```

---

## 2) Geocode Address

### `POST /v1/geocode/address`

מבצע גיאוקוד לכתובת מובנית אחת.

### Request Body

```json
{
  "city": "פתח תקווה",
  "street": "הרצל",
  "house_number": "10",
  "country_code": "IL"
}
```

### שדות Request

- `city` (string, required, 1..120)
- `street` (string, optional, max 120)
- `house_number` (string, optional, max 32)
- `country_code` (string, optional, בדיוק 2 תווים, עובר upper-case אוטומטי)

### Response 200 (הצלחה)

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

### Response 200 (לא נמצא תוצאה)

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
  "warnings": [
    "No geocoding result found"
  ],
  "error": null
}
```

### Response 200 (שגיאת Provider)

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
  "warnings": [],
  "error": "Geocoding provider is unavailable"
}
```

### Response 422 (ולידציה)

אם גוף הבקשה לא תקין (למשל `city` חסר/ריק, או `country_code` לא באורך 2), FastAPI מחזיר שגיאת ולידציה סטנדרטית.

---

## 3) Geocode Batch

### `POST /v1/geocode/batch`

מבצע גיאוקוד לרשימת כתובות ומחזיר תוצאות באותו סדר קלט.

### Request Body

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

### שדות Request

- `addresses` (array, required, 1..100)
- כל פריט במערך הוא `GeocodeAddressRequest` בדיוק כמו ב־`/v1/geocode/address`

### Response 200

```json
{
  "success": true,
  "results": [
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
    },
    {
      "success": false,
      "query": {
        "city": "תל אביב",
        "street": "דיזנגוף",
        "house_number": "50",
        "country_code": "IL"
      },
      "result": null,
      "warnings": [
        "No geocoding result found"
      ],
      "error": null
    }
  ],
  "warnings": [],
  "error": null
}
```

### Response 422 (ולידציה)

אם `addresses` חסר/ריק או חורג ממגבלת הכמות (מעל 100), או אחד הפריטים לא תקין.

---

## הערות אפיון חשובות

- גם במצבי כשל עסקי (אין תוצאה / provider לא זמין), ה־HTTP status נשאר `200`, והאינדיקציה לכשל היא `success: false` בתוך ה־payload.
- `match_quality` ערכים אפשריים: `high` / `medium` / `low`.
- `partial_match` הוא `true` כאשר `match_quality` לא `high`.
- ב־Batch התוצאה לכל כתובת נמצאת בתוך `results[i]`, ובנוסף מעטפת batch עם `success`, `warnings`, `error`.
