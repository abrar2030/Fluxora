# Fluxora API Documentation

## Overview

The Fluxora API provides endpoints for energy consumption prediction and monitoring. It is built using FastAPI and provides a RESTful interface for interacting with the Fluxora energy prediction system.

## Base URL

When running locally:

```
http://localhost:8000
```

When deployed:

```
https://api.fluxora.example.com
```

## Authentication

Authentication is currently not implemented but will be added in future versions using OAuth2 or API keys.

## Endpoints

### Health Check

```
GET /health
```

Returns the health status of the API and the current version.

**Response**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Prediction

```
POST /predict
```

Predicts energy consumption based on provided timestamps, meter IDs, and context features.

**Request Body**

```json
{
  "timestamps": ["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z"],
  "meter_ids": ["meter_001", "meter_002"],
  "context_features": {
    "temperature": [20.5, 21.2],
    "humidity": [65, 70]
  }
}
```

**Response**

```json
{
  "predictions": [45.2, 50.1],
  "confidence_intervals": [
    [40.1, 50.3],
    [45.2, 55.0]
  ],
  "model_version": "0.1.0-test"
}
```

## Error Handling

The API returns standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Internal Server Error

Error responses include a message field with details about the error.

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Data Models

### PredictionRequest

| Field            | Type      | Description                       |
| ---------------- | --------- | --------------------------------- |
| timestamps       | list[str] | List of ISO format timestamps     |
| meter_ids        | list[str] | List of meter identifiers         |
| context_features | dict      | Dictionary of additional features |

### PredictionResponse

| Field                | Type                      | Description                                  |
| -------------------- | ------------------------- | -------------------------------------------- |
| predictions          | list[float]               | Predicted energy consumption values          |
| confidence_intervals | list[tuple[float, float]] | 95% confidence intervals for each prediction |
| model_version        | str                       | Version of the model used for prediction     |

## Rate Limiting

Rate limiting is not currently implemented but will be added in future versions.
