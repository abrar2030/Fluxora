.PHONY: install data train tune deploy monitor test clean

install:
    pip install -r requirements.txt
    prefect config set PREFECT_API_URL="http://localhost:4200/api"

data:
    python src/data/make_dataset.py --config=config/config.yaml

train:
    python src/models/train.py --experiment-name=prod_v1

tune:
    python src/models/tune_hyperparams.py --storage=mlruns

deploy:
    docker-compose build --no-cache
    docker-compose up -d

monitor:
    prefect orion start &
    prometheus --config.file=monitoring/prometheus.yml

test:
    pytest tests/ --cov=src --cov-report=html

clean:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    rm -rf .pytest_cache/ .mlruns/ htmlcov/
