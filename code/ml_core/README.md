# fluxora-ml-core

Framework independent forecasting package behind the Fluxora predictions API.
It depends only on `numpy`, `pandas`, `scikit-learn` and `joblib`, never imports
the backend, and can be used from notebooks or batch jobs.

## Layout

```
ml_core/
├── pyproject.toml
├── README.md
├── src/ml_core/
│   ├── __init__.py          Public API and __version__
│   ├── py.typed
│   ├── config.py            Hyperparameters, limits, environment settings
│   ├── exceptions.py        Error hierarchy shared with the backend
│   ├── data/
│   │   ├── validation.py    Raw frame validation
│   │   └── resampling.py    UTC normalisation and hourly regularisation
│   ├── features/
│   │   ├── schema.py        Feature names and column order
│   │   ├── temporal.py      Calendar and cyclical features
│   │   ├── lags.py          Lag and rolling features
│   │   └── builder.py       Training feature pipeline
│   ├── models/
│   │   ├── bundle.py        Versioned model bundle
│   │   ├── flat_forest.py   Low latency single row forest inference
│   │   └── store.py         Atomic persistence and cached loading
│   ├── training/
│   │   ├── evaluation.py    Metrics and residual interval bounds
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
from ml_core import forecast, load_bundle, run_training_pipeline

run_training_pipeline(frame)
bundle = load_bundle()
result = forecast(bundle, history, horizon_hours=48)
```

`frame` needs `timestamp`, `consumption_kwh` and `user_id` columns. `history`
holds a single user's `timestamp` and `consumption_kwh` readings.

## Configuration

| Variable             | Default                  | Purpose                              |
| :------------------- | :----------------------- | :----------------------------------- |
| `MODEL_PATH`         | `./fluxora_model.joblib` | Location of the trained model bundle |
| `MODEL_N_ESTIMATORS` | `100`                    | Trees in the random forest           |
| `MODEL_MAX_DEPTH`    | unset                    | Optional tree depth limit            |

## Development

```bash
cd ml_core
pytest
ruff check .
black --check .
mypy src
```
