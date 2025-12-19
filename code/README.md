# Fluxora Backend

This is the backend API for the Fluxora energy forecasting and optimization platform.

## Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation & Running

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Start the server**:

```bash
# Simple start
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Or use the startup script
./start.sh

# With auto-reload for development
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. **Access the API**:

- API Root: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
code/
├── api/              # API endpoints
│   └── v1/          # API version 1
│       ├── auth.py       # Authentication endpoints
│       ├── data.py       # Data management endpoints
│       ├── analytics.py  # Analytics endpoints
│       └── predictions.py # Prediction endpoints
├── backend/         # Core backend functionality
│   ├── app.py           # Legacy app (not used)
│   ├── database.py      # Database configuration
│   ├── dependencies.py  # FastAPI dependencies
│   ├── security.py      # Authentication & security
│   └── schemas.py       # Request/response schemas
├── core/            # Core utilities
│   ├── config.py        # Configuration management
│   ├── health_check.py  # Health check utilities
│   └── logging_framework.py # Logging utilities
├── crud/            # Database operations
│   ├── user.py          # User CRUD operations
│   └── data.py          # Energy data CRUD operations
├── data/            # Data processing
│   └── features/
│       └── feature_engineering.py # Feature engineering
├── features/        # Feature processing
│   ├── build_features.py    # Feature pipeline
│   └── feature_store.py     # Feature store
├── models/          # Database & ML models
│   ├── base.py          # SQLAlchemy base
│   ├── user.py          # User model
│   ├── data.py          # Energy data model
│   └── predict.py       # Prediction logic
├── schemas/         # Pydantic schemas
│   ├── user.py          # User schemas
│   └── data.py          # Energy data schemas
├── main.py          # Application entry point
├── requirements.txt # Python dependencies
└── start.sh        # Startup script
```

## API Endpoints

### Authentication

- `POST /v1/auth/register` - Register new user
- `POST /v1/auth/token` - Login and get access token

### Data Management

- `POST /v1/data/` - Create energy data record
- `GET /v1/data/` - List energy data records
- `GET /v1/data/query` - Query data by time range

### Analytics

- `GET /v1/analytics/` - Get analytics (week/month/year)

### Predictions

- `GET /v1/predictions/` - Get energy consumption predictions

### System

- `GET /health` - Health check
- `GET /` - API information

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

Key configuration variables:

- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: JWT secret key (MUST change in production)
- `API_PORT`: API server port (default: 8000)

## Database

The application uses SQLite by default for development. For production, configure PostgreSQL:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/fluxora
```

Database tables are automatically created on first startup.

## Development

### Running Tests

```bash
pytest
```

### Code Style

The project follows Python best practices with type hints and documentation.

## Troubleshooting

### Import Errors

Make sure you're running from the `code` directory:

```bash
cd code
python -m uvicorn main:app
```

### Database Errors

Delete the SQLite database and restart:

```bash
rm fluxora.db
python -m uvicorn main:app
```

### Port Already in Use

Change the port:

```bash
python -m uvicorn main:app --port 8001
```

## Notes

- The application includes mock prediction functionality
- Authentication uses JWT tokens
- CORS is configured for common frontend ports
- Default SQLite database: `fluxora.db`
