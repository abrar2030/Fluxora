from typing import Any

import pandas as pd

from ..exceptions import DataValidationError


class ValidationResult:
    def __init__(
        self,
        success: bool,
        errors: list[str] | None = None,
        warnings: list[str] | None = None,
    ) -> None:
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []

    def __repr__(self) -> str:
        return (
            f"ValidationResult(success={self.success}, errors={self.errors}, "
            f"warnings={self.warnings})"
        )


def _null_message(column: str, count: int, total: int, strict: bool) -> str:
    message = f"Column '{column}' contains {count} null value(s) out of {total} rows"
    return message + "." if strict else message + "; those rows are ignored."


def validate_raw_data(df: Any, *, strict_nulls: bool = False) -> ValidationResult:
    """Validate a raw consumption frame.

    Missing values in ``timestamp`` or ``consumption_kwh`` are reported as
    warnings by default because the training pipeline drops those rows. Pass
    ``strict_nulls=True`` to treat them as errors instead. Structural problems
    (missing columns) and impossible values (negative consumption, out-of-range
    weather readings) always raise ``DataValidationError``.
    """
    errors: list[str] = []
    warnings: list[str] = []

    for col in ("timestamp", "consumption_kwh"):
        if col not in df.columns:
            errors.append(f"Missing required column: '{col}'")
    if errors:
        raise DataValidationError(f"Data validation failed: {errors}")

    total = len(df)
    for col in ("timestamp", "consumption_kwh"):
        nulls = int(df[col].isnull().sum())
        if nulls:
            message = _null_message(col, nulls, total, strict_nulls)
            (errors if strict_nulls else warnings).append(message)

    if (df["consumption_kwh"].dropna() < 0).any():
        errors.append("Column 'consumption_kwh' contains negative values.")

    if "cost_usd" in df.columns and df["cost_usd"].dropna().lt(0).any():
        errors.append("Column 'cost_usd' contains negative values.")

    if "temperature_c" in df.columns:
        temp = df["temperature_c"].dropna()
        if (temp < -100).any() or (temp > 100).any():
            errors.append(
                "Column 'temperature_c' has values outside plausible range [-100, 100]."
            )

    if "humidity_percent" in df.columns:
        hum = df["humidity_percent"].dropna()
        if (hum < 0).any() or (hum > 100).any():
            errors.append(
                "Column 'humidity_percent' has values outside range [0, 100]."
            )

    if errors:
        raise DataValidationError(f"Data validation failed: {errors}")

    return ValidationResult(success=True, warnings=warnings)


def validate_energy_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {
            "valid": False,
            "row_count": 0,
            "null_counts": {},
            "warnings": ["DataFrame is empty."],
        }

    warnings: list[str] = []
    null_counts: dict[str, int] = df.isnull().sum().to_dict()

    if "consumption_kwh" in df.columns and null_counts.get("consumption_kwh", 0):
        warnings.append(
            f"consumption_kwh has {null_counts['consumption_kwh']} null values."
        )

    if "timestamp" in df.columns:
        try:
            pd.to_datetime(df["timestamp"])
        except (ValueError, TypeError):
            warnings.append("Some 'timestamp' values could not be parsed as datetime.")

    return {
        "valid": not warnings,
        "row_count": len(df),
        "null_counts": null_counts,
        "warnings": warnings,
    }
