class FluxoraError(Exception):
    pass


class DataValidationError(FluxoraError):
    pass


class ModelServicingError(FluxoraError):
    pass


class FeatureStoreConnectionError(FluxoraError):
    pass


class TemporalCoherenceError(FluxoraError):
    pass


class ResourceNotFoundError(FluxoraError):
    pass


class AuthenticationError(FluxoraError):
    pass


class AuthorizationError(FluxoraError):
    pass
