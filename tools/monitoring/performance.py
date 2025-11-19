# tools/monitoring/performance.py
import time

from fluxora.core.alert_handler import AlertHandler
from fluxora.core.logger import get_logger
from prometheus_client import Counter, Gauge, Histogram, Summary
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

logger = get_logger(__name__)
alert_handler = AlertHandler()

# --- Core Metrics ---
# Regression Metrics
MODEL_MAE = Gauge("model_mean_absolute_error", "Model Mean Absolute Error over time")
MODEL_MSE = Gauge("model_mean_squared_error", "Model Mean Squared Error over time")
MODEL_RMSE = Gauge(
    "model_root_mean_squared_error", "Model Root Mean Squared Error over time"
)
MODEL_R2_SCORE = Gauge("model_r_squared_score", "Model R-squared score over time")

# Classification Metrics
MODEL_ACCURACY = Gauge("model_accuracy_score", "Model Accuracy score over time")
MODEL_PRECISION = Gauge(
    "model_precision_score", "Model Precision score over time (macro average)"
)
MODEL_RECALL = Gauge(
    "model_recall_score", "Model Recall score over time (macro average)"
)
MODEL_F1_SCORE = Gauge("model_f1_score", "Model F1 score over time (macro average)")

# Operational Metrics
API_REQUESTS_TOTAL = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["endpoint", "method", "status_code"],
)
API_REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency in seconds",
    ["endpoint", "method"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        float("inf"),
    ),
)
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "Model prediction latency in seconds",
    ["model_name", "model_version"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, float("inf")),
)

# --- Thresholds for Alerts (example) ---
PERFORMANCE_THRESHOLDS = {
    "mae_increase_pct": 10.0,  # Alert if MAE increases by 10% from baseline
    "r2_decrease_pct": 5.0,  # Alert if R2 decreases by 5% from baseline
    "accuracy_drop_abs": 0.05,  # Alert if accuracy drops by 0.05 absolute
}
# Store baseline metrics (in a real system, this might come from a config or a database)
BASELINE_METRICS = {"mae": None, "r2_score": None, "accuracy": None}


def update_baseline_metric(metric_name: str, value: float):
    """Updates a baseline metric value."""
    if metric_name in BASELINE_METRICS:
        BASELINE_METRICS[metric_name] = value
        logger.info(f"Baseline for {metric_name} updated to: {value}")
    else:
        logger.warning(f"Attempted to update unknown baseline metric: {metric_name}")


def log_regression_performance(
    y_true, y_pred, model_name: str = "default", model_version: str = "v1"
):
    """
    Calculates and logs regression performance metrics.
    Args:
        y_true: True target values.
        y_pred: Predicted target values.
        model_name (str): Name of the model.
        model_version (str): Version of the model.
    """
    try:
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = mse**0.5
        r2 = r2_score(y_true, y_pred)

        MODEL_MAE.set(mae)
        MODEL_MSE.set(mse)
        MODEL_RMSE.set(rmse)
        MODEL_R2_SCORE.set(r2)

        logger.info(
            f"Regression Performance ({model_name} {model_version}) - MAE: {mae:.4f}, MSE: {mse:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}"
        )

        # Check against baseline for MAE
        if BASELINE_METRICS["mae"] is not None and mae > BASELINE_METRICS["mae"] * (
            1 + PERFORMANCE_THRESHOLDS["mae_increase_pct"] / 100
        ):
            alert_handler.trigger_alert(
                "REGRESSION_MAE_DEGRADATION",
                details={
                    "model": f"{model_name} {model_version}",
                    "current_mae": mae,
                    "baseline_mae": BASELINE_METRICS["mae"],
                    "threshold_pct": PERFORMANCE_THRESHOLDS["mae_increase_pct"],
                },
                level="WARNING",
            )
        # Check against baseline for R2
        if BASELINE_METRICS["r2_score"] is not None and r2 < BASELINE_METRICS[
            "r2_score"
        ] * (1 - PERFORMANCE_THRESHOLDS["r2_decrease_pct"] / 100):
            alert_handler.trigger_alert(
                "REGRESSION_R2_DEGRADATION",
                details={
                    "model": f"{model_name} {model_version}",
                    "current_r2": r2,
                    "baseline_r2": BASELINE_METRICS["r2_score"],
                    "threshold_pct": PERFORMANCE_THRESHOLDS["r2_decrease_pct"],
                },
                level="WARNING",
            )

    except Exception as e:
        logger.error(
            f"Error calculating regression performance for {model_name} {model_version}: {e}"
        )


def log_classification_performance(
    y_true,
    y_pred,
    y_proba=None,
    model_name: str = "default",
    model_version: str = "v1",
    average: str = "macro",
):
    """
    Calculates and logs classification performance metrics.
    Args:
        y_true: True target labels.
        y_pred: Predicted target labels.
        y_proba: Predicted probabilities (for metrics like ROC AUC, not implemented here yet).
        model_name (str): Name of the model.
        model_version (str): Version of the model.
        average (str): Averaging method for precision, recall, F1 (e.g., 	macro	, 	micro	, 	weighted	).
    """
    try:
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average=average, zero_division=0)
        recall = recall_score(y_true, y_pred, average=average, zero_division=0)
        f1 = f1_score(y_true, y_pred, average=average, zero_division=0)

        MODEL_ACCURACY.set(accuracy)
        MODEL_PRECISION.set(precision)
        MODEL_RECALL.set(recall)
        MODEL_F1_SCORE.set(f1)

        logger.info(
            f"Classification Performance ({model_name} {model_version}, avg: {average}) - Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}"
        )

        # Check against baseline for Accuracy
        if BASELINE_METRICS["accuracy"] is not None and accuracy < (
            BASELINE_METRICS["accuracy"] - PERFORMANCE_THRESHOLDS["accuracy_drop_abs"]
        ):
            alert_handler.trigger_alert(
                "CLASSIFICATION_ACCURACY_DEGRADATION",
                details={
                    "model": f"{model_name} {model_version}",
                    "current_accuracy": accuracy,
                    "baseline_accuracy": BASELINE_METRICS["accuracy"],
                    "threshold_abs_drop": PERFORMANCE_THRESHOLDS["accuracy_drop_abs"],
                },
                level="WARNING",
            )

    except Exception as e:
        logger.error(
            f"Error calculating classification performance for {model_name} {model_version}: {e}"
        )


def update_api_request_metrics(
    endpoint: str, method: str, status_code: int, latency_seconds: float
):
    """
    Updates API request counters and latency histograms.
    Args:
        endpoint (str): The API endpoint path.
        method (str): The HTTP method (e.g., GET, POST).
        status_code (int): The HTTP status code of the response.
        latency_seconds (float): The duration of the request in seconds.
    """
    try:
        API_REQUESTS_TOTAL.labels(
            endpoint=endpoint, method=method, status_code=status_code
        ).inc()
        API_REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(
            latency_seconds
        )
        # logger.debug(f"API metrics updated for {method} {endpoint} -> {status_code} in {latency_seconds:.4f}s")
    except Exception as e:
        logger.error(f"Error updating API request metrics: {e}")


def update_prediction_latency(
    model_name: str, model_version: str, latency_seconds: float
):
    """
    Updates model prediction latency histogram.
    Args:
        model_name (str): Name of the model.
        model_version (str): Version of the model.
        latency_seconds (float): The duration of the prediction in seconds.
    """
    try:
        PREDICTION_LATENCY.labels(
            model_name=model_name, model_version=model_version
        ).observe(latency_seconds)
        # logger.debug(f"Prediction latency for {model_name} {model_version} updated: {latency_seconds:.4f}s")
    except Exception as e:
        logger.error(f"Error updating prediction latency: {e}")


# Example Usage (can be run if prometheus_client is installed and an endpoint is exposed)
if __name__ == "__main__":
    import random

    from prometheus_client import start_http_server

    logger.info("Starting performance monitoring example...")
    # Start up the server to expose the metrics.
    # In a real app, this would be part of your main application server (e.g., Flask, FastAPI)
    # start_http_server(8000) # Exposes metrics on http://localhost:8000/metrics
    # logger.info("Prometheus metrics available on port 8000 /metrics")

    # --- Simulate Regression Model Performance ---
    logger.info("\n--- Simulating Regression Model Performance ---")
    y_true_reg = [3, -0.5, 2, 7, 4.2, 5.5, 6.1, 2.3, 8.0, 9.5]
    y_pred_reg_good = [2.5, 0.0, 2.1, 7.8, 4.0, 5.0, 6.5, 2.0, 7.5, 9.0]
    y_pred_reg_bad = [1.0, 2.0, 4.0, 5.0, 6.0, 3.0, 4.5, 5.0, 5.5, 6.5]

    update_baseline_metric("mae", 0.5)  # Set a baseline MAE
    update_baseline_metric("r2_score", 0.9)

    log_regression_performance(
        y_true_reg,
        y_pred_reg_good,
        model_name="SalesForecaster",
        model_version="v1.0.0",
    )
    log_regression_performance(
        y_true_reg,
        y_pred_reg_bad,
        model_name="OldSalesForecaster",
        model_version="v0.5.0",
    )  # This should trigger MAE alert

    # --- Simulate Classification Model Performance ---
    logger.info("\n--- Simulating Classification Model Performance ---")
    y_true_cls = [0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1]
    y_pred_cls_good = [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1]
    y_pred_cls_bad = [1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]

    update_baseline_metric("accuracy", 0.85)
    log_classification_performance(
        y_true_cls, y_pred_cls_good, model_name="FraudDetector", model_version="v2.1.0"
    )
    log_classification_performance(
        y_true_cls,
        y_pred_cls_bad,
        model_name="LegacyFraudDetector",
        model_version="v1.0.0",
    )  # This should trigger accuracy alert

    # --- Simulate API Requests & Latency ---
    logger.info("\n--- Simulating API Requests & Latency ---")
    endpoints = ["/predict", "/health", "/features"]
    methods = ["POST", "GET"]
    for i in range(100):
        endpoint = random.choice(endpoints)
        method = random.choice(methods) if endpoint != "/health" else "GET"
        status = random.choices([200, 201, 400, 404, 500], weights=[70, 10, 10, 5, 5])[
            0
        ]
        latency = random.uniform(0.001, 1.5)
        update_api_request_metrics(endpoint, method, status, latency)
        time.sleep(0.01)
    logger.info("Simulated 100 API requests.")

    # --- Simulate Prediction Latency ---
    logger.info("\n--- Simulating Prediction Latency ---")
    for i in range(50):
        model_name = random.choice(["SalesForecaster", "FraudDetector"])
        model_version = "v1.0.0" if model_name == "SalesForecaster" else "v2.1.0"
        pred_latency = random.uniform(0.005, 0.250)
        update_prediction_latency(model_name, model_version, pred_latency)
        time.sleep(0.02)
    logger.info("Simulated 50 model predictions.")

    logger.info(
        "\nPerformance monitoring example finished. If prometheus server was started, check metrics endpoint."
    )
