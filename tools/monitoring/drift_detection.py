# tools/monitoring/drift_detection.py
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
# Assuming config and alert_handler are in packages.shared.utils
from packages.shared.utils import config # Import the config module directly
from packages.shared.utils.alert_handler import AlertHandler
from packages.shared.utils.logger import get_logger

logger = get_logger(__name__)
alert_handler = AlertHandler() # Initialize alert handler

def detect_data_drift(current_data: pd.DataFrame, reference_data: pd.DataFrame, column_mapping_override: dict = None):
    """
    Detects data drift between current and reference datasets using Evidently.

    Args:
        current_data (pd.DataFrame): The current dataset for drift analysis.
        reference_data (pd.DataFrame): The reference (baseline) dataset.
        column_mapping_override (dict, optional): A dictionary to override the default column mapping from config.
                                                 This allows for flexibility if datasets have different column names
                                                 than what is globally configured.
    Returns:
        Report: The Evidently data drift report object.
        bool: True if dataset drift is detected, False otherwise.
    """
    logger.info("Starting data drift detection...")

    # Use override if provided, otherwise use global config
    active_column_mapping = column_mapping_override if column_mapping_override is not None else config.column_mapping

    if not active_column_mapping:
        logger.error("Column mapping is not defined. Cannot perform data drift detection.")
        # Potentially raise an error or return a specific status
        return None, False

    try:
        data_drift_report = Report(metrics=[DataDriftPreset()])
        data_drift_report.run(
            current_data=current_data,
            reference_data=reference_data,
            column_mapping=active_column_mapping
        )

        # Check for dataset level drift
        # The exact key might depend on the Evidently version, adjust if necessary
        # Based on common Evidently report structure for DataDriftPreset
        drift_info = data_drift_report.as_dict().get("data_drift", {})
        dataset_drift_detected = drift_info.get("data", {}).get("metrics", {}).get("dataset_drift", False)
        # Fallback if the above path is not found, check older/alternative structures
        if not isinstance(dataset_drift_detected, bool):
             dataset_drift_detected = drift_info.get("metrics", [{}])[0].get("dataset_drift", False) # common in older versions

        if dataset_drift_detected:
            logger.warning("DATA DRIFT DETECTED!")
            alert_handler.trigger_alert(
                "DATA_DRIFT_ALERT",
                details={"report_summary": drift_info, "message": "Significant data drift detected in the dataset."},
                level="WARNING"
            )
        else:
            logger.info("No significant data drift detected at the dataset level.")

        return data_drift_report, dataset_drift_detected

    except Exception as e:
        logger.error(f"Error during data drift detection: {e}")
        alert_handler.trigger_alert(
            "DRIFT_DETECTION_ERROR",
            details={"error_message": str(e)},
            level="ERROR"
        )
        return None, False

# Example Usage (assumes dummy data and config)
if __name__ == "__main__":
    logger.info("Running drift_detection.py example...")

    # Create dummy data for demonstration
    # Reference data (e.g., training data or a stable period)
    ref_data = pd.DataFrame({
        config.column_mapping["numerical_features"][0]: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        config.column_mapping["numerical_features"][1]: [10, 20, 30, 40, 50, 50, 40, 30, 20, 10, 11, 12, 13, 14, 15],
        config.column_mapping["categorical_features"][0]: ["A", "B", "A", "C", "B", "A", "C", "A", "B", "C", "A", "B", "A", "C", "B"],
        config.column_mapping["target"]: [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    })

    # Current data (e.g., recent production data)
    # Introduce some drift for demonstration
    current_data_drifted = pd.DataFrame({
        config.column_mapping["numerical_features"][0]: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], # Shifted distribution
        config.column_mapping["numerical_features"][1]: [15, 25, 35, 45, 55, 60, 55, 45, 35, 25, 10, 20, 30, 40, 50], # Shifted distribution
        config.column_mapping["categorical_features"][0]: ["B", "C", "B", "A", "C", "B", "A", "B", "C", "A", "B", "C", "B", "A", "C"], # Changed proportions
        config.column_mapping["target"]: [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1] # Potentially different target distribution
    })

    current_data_no_drift = ref_data.copy()
    current_data_no_drift[config.column_mapping["numerical_features"][0]] = current_data_no_drift[config.column_mapping["numerical_features"][0]] + 0.1 # Minor noise, no real drift


    logger.info("\n--- Testing with Drifted Data ---")
    drift_report_drifted, detected_drift_drifted = detect_data_drift(current_data_drifted, ref_data)
    if drift_report_drifted:
        # drift_report_drifted.save_html("drift_report_drifted.html")
        # logger.info("Drift report for drifted data saved to drift_report_drifted.html")
        logger.info(f"Drift detected in drifted data: {detected_drift_drifted}")
        # print(drift_report_drifted.as_dict())

    logger.info("\n--- Testing with Non-Drifted Data ---")
    drift_report_no_drift, detected_drift_no_drift = detect_data_drift(current_data_no_drift, ref_data)
    if drift_report_no_drift:
        # drift_report_no_drift.save_html("drift_report_no_drift.html")
        # logger.info("Drift report for non-drifted data saved to drift_report_no_drift.html")
        logger.info(f"Drift detected in non-drifted data: {detected_drift_no_drift}")

    # Example with column_mapping_override
    logger.info("\n--- Testing with Column Mapping Override (using drifted data) ---")
    custom_mapping = config.column_mapping.copy()
    custom_mapping["numerical_features"] = ["new_feature1_name", "new_feature2_name"]
    custom_mapping["categorical_features"] = ["new_category_a_name"]
    custom_mapping["target"] = "new_target_name"

    current_data_custom_names = current_data_drifted.copy()
    current_data_custom_names.columns = ["new_feature1_name", "new_feature2_name", "new_category_a_name", "new_target_name"]

    ref_data_custom_names = ref_data.copy()
    ref_data_custom_names.columns = ["new_feature1_name", "new_feature2_name", "new_category_a_name", "new_target_name"]

    drift_report_override, detected_drift_override = detect_data_drift(current_data_custom_names, ref_data_custom_names, column_mapping_override=custom_mapping)
    if drift_report_override:
        # drift_report_override.save_html("drift_report_override.html")
        # logger.info("Drift report with override saved to drift_report_override.html")
        logger.info(f"Drift detected with override: {detected_drift_override}")

