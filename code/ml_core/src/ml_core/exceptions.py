class MLCoreError(Exception):
    pass


class DataValidationError(MLCoreError):
    pass


class InsufficientDataError(MLCoreError):
    pass


class InsufficientHistoryError(MLCoreError):
    pass


class ModelNotFoundError(MLCoreError):
    pass


class ModelLoadError(MLCoreError):
    pass
