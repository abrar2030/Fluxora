# fluxora-ml-core

Framework independent forecasting package behind the Fluxora predictions API.
It depends only on `numpy`, `pandas`, `scikit-learn` and `joblib`, never imports
the backend, and can be used from notebooks or batch jobs.

## Layout

```
ml_core/
├── pyproject.toml
├── README.md
├── src/                     Python package, imported as `src`
│   ├── __init__.py          Public API and __version__
│   ├── py.typed
│   ├── config.py            Hyperparameters, limits, environment settings
│   ├── exceptions.py        Error hierarchy shared with the backend
│   ├── data/
│   │   ├── validation.py    Raw frame validation
│   │   └── resampling.py    UTC normalisation and hourly regularisation
│   ├── features/
│   │   ├── schema.py        Feature names and column order
│   │   ├── holiday_calendar.py  Public-holiday flags for a chosen country
│   │   ├── temporal.py      Calendar and cyclical features
│   │   ├── lags.py          Lag and rolling features
│   │   └── builder.py       Training feature pipeline
│   ├── models/
│   │   ├── bundle.py        Versioned model bundle
│   │   ├── flat_forest.py   Low latency single row forest inference
│   │   └── store.py         Atomic persistence and cached loading
│   ├── training/
│   │   ├── evaluation.py    Metrics and residual interval bounds
│   │   ├── backtest.py      Per-horizon interval calibration from backtests
│   │   ├── trainer.py       Holdout evaluation and final fit
│   │   └── pipeline.py      Train and persist
│   └── inference/
│       └── forecaster.py    Recursive multi step forecasting
└── tests/
    ├── factories.py
    └── unit/
```

Dependencies point one way: `config` and `exceptions` are leaves, `data` and
`features` build on them, `models` holds artefacts, and `training` and
`inference` sit on top.

## Install

```bash
pip install ./ml_core
pip install -e "./ml_core[dev]"
```

## Usage

```python
from src import forecast, load_bundle, run_training_pipeline

run_training_pipeline(frame)
bundle = load_bundle()
result = forecast(bundle, history, horizon_hours=48)
```

`frame` needs `timestamp`, `consumption_kwh` and `user_id` columns. `history`
holds a single user's `timestamp` and `consumption_kwh` readings.

## Configuration

| Variable                | Default                  | Purpose                                                                                                                      |
| :---------------------- | :----------------------- | :--------------------------------------------------------------------------------------------------------------------------- |
| `MODEL_PATH`            | `./fluxora_model.joblib` | Location of the trained model bundle                                                                                         |
| `MODEL_N_ESTIMATORS`    | `100`                    | Trees in the random forest                                                                                                   |
| `MODEL_MAX_DEPTH`       | unset                    | Optional tree depth limit                                                                                                    |
| `MODEL_REFIT_FULL_DATA` | `true`                   | Refit on all data after the holdout evaluation. `false` keeps the holdout model and roughly halves fitting time              |
| `HOLIDAY_COUNTRY`       | `US`                     | Calendar for the `is_holiday` feature: `US`, `NONE`, or an ISO code such as `PK` (needs `pip install "./ml_core[holidays]"`) |

## Development

```bash
cd ml_core
pytest
ruff check .
black --check .
mypy src
```

## Behaviour notes

- **Missing data.** Runs of up to `MAX_FILL_GAP_HOURS` (6) missing hours are linearly
  interpolated, both when building training features and when preparing a forecast
  history. Rows whose own target was interpolated are never used as training targets.
  Longer gaps are not filled: training skips the affected rows and forecasting raises
  `InsufficientHistoryError`.
- **Validation.** `validate_raw_data` reports null `timestamp` / `consumption_kwh` values as
  warnings (training drops those rows) and raises for structural or impossible values.
  Pass `strict_nulls=True` to treat nulls as errors.
- **Holidays.** `is_holiday` is a real model feature. The calendar used is stored in the
  model bundle, so forecasts always use the calendar the model was trained with.
  Timestamps are matched on their UTC calendar date.
- **Prediction intervals.** Bounds are calibrated per forecast horizon (1, 2-3, 4-6, 7-12,
  13-24, 25-48, 49-96 and 97-168 hours ahead) from recursive backtests on the holdout
  period, and are forced to widen with the horizon. Horizons beyond 168 hours reuse the last
  bucket. Buckets without enough backtest samples inherit the previous bucket.
- **Model fitting.** Training fits a holdout model for metrics and interval calibration and,
  by default, a second model on all rows. Set `MODEL_REFIT_FULL_DATA=false` to skip the
  second fit.
- **Stored models.** The bundle format is versioned (currently 3). Models saved by an older
  version are rejected with `ModelLoadError` and must be retrained.
