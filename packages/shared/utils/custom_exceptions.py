class EnergyForecastingError(Exception):
    """Base exception class for all project-specific errors"""
    
class DataValidationError(EnergyForecastingError):
    """Raised when data fails quality checks"""
    
class ModelServicingError(EnergyForecastingError):
    """Raised when model serving fails"""
    
class FeatureStoreConnectionError(EnergyForecastingError):
    """Raised when unable to connect to feature store"""
    
class TemporalCoherenceError(EnergyForecastingError):
    """Raised when time series data has gaps/inconsistencies"""