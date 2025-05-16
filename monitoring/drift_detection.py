from evidently.metric_preset import DataDriftPreset
from evidently.report import Report


def detect_data_drift(current_data, reference_data):
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(
        current_data=current_data,
        reference_data=reference_data,
        column_mapping=config.column_mapping,
    )

    if data_drift_report["data_drift"]["dataset_drift"]:
        alert_handler.trigger_alert(
            "DATA_DRIFT_ALERT", details=data_drift_report.as_dict()
        )

    return data_drift_report
