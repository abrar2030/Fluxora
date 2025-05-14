from prometheus_client import Gauge, Counter

MODEL_MAE = Gauge('model_mae', 'Model MAE over time')
API_REQUESTS = Counter('api_requests_total', 'Total API requests')

def log_performance(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    MODEL_MAE.set(mae)
    
def update_request_counter():
    API_REQUESTS.inc()