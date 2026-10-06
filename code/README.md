# Fluxora

Energy data management and ML-powered consumption forecasting platform.

## Project Structure

```
code/
├── backend/                  FastAPI REST API
│   ├── app/
│   │   ├── api/v1/           Route handlers (auth, data, analytics, predictions, users)
│   │   ├── core/             Security, circuit breaker, retry, fallback, error handling
│   │   ├── crud/             Database access helpers
│   │   ├── db/               SQLAlchemy engine and session factory
│   │   ├── models/           ORM models
│   │   ├── schemas/          Pydantic schemas
│   │   └── services/         Adapter between the database and ml_core
│   ├── migrations/           Alembic migrations
│   ├── tests/                pytest suite (api, integration, unit)
│   ├── main.py               Uvicorn entry point
│   ├── requirements.txt      Runtime dependencies
│   ├── requirements-dev.txt  Runtime plus test dependencies
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── ml_core/                  Installable forecasting package (src layout)
    ├── pyproject.toml        Package metadata, dependencies, tool config
    ├── README.md
    ├── src/ml_core/
    │   ├── config.py         Hyperparameters, limits, environment settings
    │   ├── exceptions.py     Error types shared with the backend
    │   ├── data/             Validation and hourly resampling
    │   ├── features/         Calendar, lag and rolling features
    │   ├── models/           Model bundle, fast inference, persistence
    │   ├── training/         Evaluation, trainer, train-and-save pipeline
    │   └── inference/        Recursive multi-step forecasting
    └── tests/                pytest suite for the package
```

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements-dev.txt
pip install -e ../ml_core
```

Python 3.10 or newer is required. If `ml_core` is not installed, the backend
falls back to `ml_core/src` in this repository.

### 2. Configure environment

```bash
cp .env.example .env
```

`.env` is loaded automatically from `backend/` at startup. Variables already
present in the process environment take precedence. When `ENV=production` the
API refuses to start unless `SECRET_KEY` is a unique value of at least 32
characters.

### 3. Run database migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start the API server

```bash
cd backend
python main.py
```

API docs are available at http://localhost:8000/docs

### 5. Run tests

```bash
cd backend
pytest

cd ../ml_core
pytest
```

### Docker

```bash
cd backend
SECRET_KEY="$(openssl rand -hex 32)" docker compose up --build
```

The build context is this directory so the image can install `ml_core` as a
package next to `backend`. The database and the trained model live in the `fluxora_data`
volume.

## Forecasting Workflow

1. Users log readings through `POST /v1/data/`.
2. A superuser trains the shared model with `POST /v1/predictions/train`. All
   users' readings are resampled to an hourly grid per user so that lag and
   rolling features always mean the same number of hours. Training needs at
   least 100 hourly samples with complete history, otherwise the endpoint
   returns 422. Metrics come from a time ordered 20 percent holdout, and the
   final model is refit on all data.
3. `GET /v1/predictions/?days=N` forecasts the next N days (1 to 90) for the
   current user from their own recent history. The forecast starts at the next
   full hour. It returns 409 when no model has been trained, 422 when the
   user's recent history is too short, too sparse, or older than 7 days, and
   503 when the stored model cannot be read.
4. `GET /v1/predictions/model` reports whether a model exists, when it was
   trained, its holdout metrics, and the interval level.

Each prediction carries a 90 percent interval built from the empirical
5th and 95th percentile of one-step holdout residuals. Intervals describe
one-step error and are therefore optimistic for long horizons.

The model file is a versioned bundle (estimator, feature columns, lags,
windows, interval offsets, metrics) written atomically, so serving always
uses the exact feature layout the model was trained on. Bundles from older
versions are rejected with an instruction to retrain.

## Configuration

| Variable             | Default                  | Purpose                                  |
| :------------------- | :----------------------- | :--------------------------------------- |
| `MODEL_PATH`         | `./fluxora_model.joblib` | Location of the trained model bundle     |
| `MODEL_N_ESTIMATORS` | `100`                    | Trees in the random forest               |
| `MODEL_MAX_DEPTH`    | unset                    | Optional tree depth limit                |
| `DATABASE_URL`       | `sqlite:///./fluxora.db` | SQLAlchemy database URL                  |
| `SECRET_KEY`         | development placeholder  | JWT signing key, mandatory in production |

## ml_core Package

`ml_core` is a self-contained package with its own `pyproject.toml`, tests and
README. It depends only on `numpy`, `pandas`, `scikit-learn`, and `joblib`, so
it can be used from notebooks or batch jobs without FastAPI or SQLAlchemy, and
it never imports the backend. The backend uses it through
`app/services/ml_service.py`. See `ml_core/README.md` for the module layout and
dependency direction.
