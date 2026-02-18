# API Documentation

## Basic Endpoints
- GET / → System Information
- GET /docs → Swagger UI
- GET /redoc → ReDoc

## Paper Endpoints
- POST /api/papers/create → Create Paper
- GET /api/papers/{id} → Get Paper
- POST /api/papers/{id}/version → Add Version

## Data Endpoints
- POST /api/data/ingest → Ingest 4D Data
- GET /api/data/{id} → Get Data

## User Endpoints
- POST /api/users/login → Login
- GET /api/users/me → Current User