import pandas as pd
import pytest


class TestDataValidator:
    def test_valid_dataframe_passes(self):
        from src.data.validation import validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
                "consumption_kwh": [10.0, 20.0, 15.0, 30.0, 25.0],
            }
        )
        result = validate_raw_data(df)
        assert result.success is True
        assert result.errors == []

    def test_missing_required_column_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {"timestamp": pd.date_range("2024-01-01", periods=3, freq="h")}
        )
        with pytest.raises(DataValidationError, match="consumption_kwh"):
            validate_raw_data(df)

    def test_missing_timestamp_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame({"consumption_kwh": [10.0, 20.0]})
        with pytest.raises(DataValidationError, match="timestamp"):
            validate_raw_data(df)

    def test_negative_consumption_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, -5.0, 20.0],
            }
        )
        with pytest.raises(DataValidationError, match="negative"):
            validate_raw_data(df)

    def test_null_consumption_is_a_warning_by_default(self):
        from src.data.validation import validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, None, 20.0],
            }
        )
        result = validate_raw_data(df)
        assert result.success is True
        assert result.errors == []
        assert len(result.warnings) == 1
        assert "1 null value(s) out of 3 rows" in result.warnings[0]

    def test_null_timestamp_is_a_warning_by_default(self):
        from src.data.validation import validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": [pd.Timestamp("2024-01-01"), None],
                "consumption_kwh": [10.0, 20.0],
            }
        )
        result = validate_raw_data(df)
        assert any("'timestamp'" in warning for warning in result.warnings)

    def test_strict_nulls_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, None, 20.0],
            }
        )
        with pytest.raises(DataValidationError, match="null"):
            validate_raw_data(df, strict_nulls=True)

    def test_nulls_do_not_hide_negative_values(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, None, -5.0],
            }
        )
        with pytest.raises(DataValidationError, match="negative"):
            validate_raw_data(df)

    def test_humidity_out_of_range_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
                "consumption_kwh": [10.0, 20.0],
                "humidity_percent": [50.0, 150.0],
            }
        )
        with pytest.raises(DataValidationError, match="humidity"):
            validate_raw_data(df)

    def test_temperature_out_of_range_raises(self):
        from src.data.validation import DataValidationError, validate_raw_data

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=2, freq="h"),
                "consumption_kwh": [10.0, 20.0],
                "temperature_c": [20.0, 999.0],
            }
        )
        with pytest.raises(DataValidationError, match="temperature"):
            validate_raw_data(df)

    def test_validate_energy_dataframe_empty(self):
        from src.data.validation import validate_energy_dataframe

        result = validate_energy_dataframe(pd.DataFrame())
        assert result["valid"] is False
        assert result["row_count"] == 0

    def test_validate_energy_dataframe_valid(self):
        from src.data.validation import validate_energy_dataframe

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=4, freq="h"),
                "consumption_kwh": [10.0, 20.0, 15.0, 25.0],
            }
        )
        result = validate_energy_dataframe(df)
        assert result["valid"] is True
        assert result["row_count"] == 4

    def test_validate_energy_dataframe_null_consumption_warning(self):
        from src.data.validation import validate_energy_dataframe

        df = pd.DataFrame(
            {
                "timestamp": pd.date_range("2024-01-01", periods=3, freq="h"),
                "consumption_kwh": [10.0, None, 20.0],
            }
        )
        result = validate_energy_dataframe(df)
        assert result["valid"] is False
        assert len(result["warnings"]) > 0
