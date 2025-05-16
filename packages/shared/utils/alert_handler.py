# packages/shared/utils/alert_handler.py
from packages.shared.utils.logger import get_logger

logger = get_logger(__name__)

class AlertHandler:
    """Handles different types of alerts, e.g., logging, email, Slack."""

    def __init__(self, default_level="WARNING"):
        self.default_level = default_level
        # In a real system, you might initialize email clients, Slack webhooks, etc.
        logger.info("AlertHandler initialized.")

    def trigger_alert(self, alert_type: str, details: dict, level: str = None):
        """
        Triggers an alert.

        Args:
            alert_type (str): A unique identifier for the type of alert (e.g., "DATA_DRIFT_ALERT", "MODEL_PERFORMANCE_DEGRADATION").
            details (dict): A dictionary containing detailed information about the alert.
            level (str, optional): The severity level of the alert (e.g., "INFO", "WARNING", "ERROR", "CRITICAL"). 
                                   Defaults to self.default_level.
        """
        alert_level = level or self.default_level
        log_message = f"ALERT TRIGGERED - Type: {alert_type}, Level: {alert_level}, Details: {details}"
        
        if alert_level.upper() == "INFO":
            logger.info(log_message)
        elif alert_level.upper() == "WARNING":
            logger.warning(log_message)
        elif alert_level.upper() == "ERROR":
            logger.error(log_message)
        elif alert_level.upper() == "CRITICAL":
            logger.critical(log_message)
        else:
            logger.warning(f"Unknown alert level 	{alert_level}	 for alert type 	{alert_type}	. Logging as WARNING. Details: {details}")

        # Placeholder for other notification mechanisms
        # self.send_email_alert(alert_type, details, alert_level)
        # self.send_slack_alert(alert_type, details, alert_level)

    def send_email_alert(self, alert_type: str, details: dict, level: str):
        """Placeholder for sending an email alert."""
        subject = f"ALERT [{level}]: {alert_type}"
        body = f"Alert Details:\n{details}"
        logger.info(f"Simulating email alert: Subject: {subject}, Body: {body[:100]}...")
        # Actual email sending logic would go here

    def send_slack_alert(self, alert_type: str, details: dict, level: str):
        """Placeholder for sending a Slack alert."""
        message = f":warning: *ALERT [{level}]*: {alert_type}\nDetails: ````{details}````"
        logger.info(f"Simulating Slack alert: {message[:100]}...")
        # Actual Slack API call would go here

# Example Usage
if __name__ == "__main__":
    alert_handler = AlertHandler()
    alert_handler.trigger_alert(
        alert_type="TEST_ALERT",
        details={"metric": "CPU Usage", "value": "95%", "threshold": "90%"},
        level="CRITICAL"
    )
    alert_handler.trigger_alert(
        alert_type="LOW_DISK_SPACE",
        details={"path": "/mnt/data", "free_space": "5GB"},
        level="WARNING"
    )

