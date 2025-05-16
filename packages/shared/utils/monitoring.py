import time
import psutil
import os
from packages.shared.utils.logger import get_logger

logger = get_logger(__name__)

class SystemMonitor:
    """A simple system monitor to track CPU, memory, and disk usage."""

    def __init__(self, disk_path: str = None):
        """
        Initializes the SystemMonitor.
        Args:
            disk_path (str, optional): The disk path to monitor. Defaults to root (oldsymbol{"}/\") on Unix-like systems.
        """
        self.disk_path = disk_path or ("/" if os.name != "nt" else "C:\\")

    def get_cpu_usage(self, interval: float = 1.0) -> float:
        """
        Gets the current CPU utilization percentage.
        Args:
            interval (float): The interval in seconds to measure CPU usage over.
        Returns:
            float: CPU utilization percentage.
        """
        try:
            return psutil.cpu_percent(interval=interval)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            return -1.0

    def get_memory_usage(self) -> dict:
        """
        Gets the current memory usage statistics.
        Returns:
            dict: A dictionary containing total, available, percent, used, and free memory in bytes,
                  or an empty dict if an error occurs.
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total,
                "available": mem.available,
                "percent": mem.percent,
                "used": mem.used,
                "free": mem.free,
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}

    def get_disk_usage(self) -> dict:
        """
        Gets the disk usage statistics for the specified path.
        Returns:
            dict: A dictionary containing total, used, free disk space in bytes, and usage percentage,
                  or an empty dict if an error occurs.
        """
        try:
            disk = psutil.disk_usage(self.disk_path)
            return {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }
        except Exception as e:
            logger.error(f"Error getting disk usage for path {self.disk_path}: {e}")
            return {}

    def log_system_status(self, interval: float = 5.0):
        """
        Logs the current system status (CPU, memory, disk) at regular intervals.
        Args:
            interval (float): The interval in seconds between status logs.
        """
        logger.info(f"Starting system monitoring. Disk path: {self.disk_path}")
        try:
            while True:
                cpu = self.get_cpu_usage()
                mem = self.get_memory_usage()
                disk = self.get_disk_usage()

                logger.info(f"CPU: {cpu}%, Memory: {mem.get('percent')}%, Disk ({self.disk_path}): {disk.get('percent')}%" )
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("System monitoring stopped by user.")
        except Exception as e:
            logger.error(f"An error occurred during system monitoring: {e}")

# Example usage (optional, can be removed or commented out)
if __name__ == "__main__":
    monitor = SystemMonitor()
    
    cpu_usage = monitor.get_cpu_usage()
    logger.info(f"Current CPU Usage: {cpu_usage}%")

    memory_info = monitor.get_memory_usage()
    if memory_info:
        logger.info(f"Memory Usage: {memory_info['percent']}% (Used: {memory_info['used'] / (1024**3):.2f}GB / Total: {memory_info['total'] / (1024**3):.2f}GB)")

    disk_info = monitor.get_disk_usage()
    if disk_info:
        logger.info(f"Disk Usage ({monitor.disk_path}): {disk_info['percent']}% (Used: {disk_info['used'] / (1024**3):.2f}GB / Total: {disk_info['total'] / (1024**3):.2f}GB)")
    
    # To run continuous logging, uncomment the following line:
    # logger.info("Starting continuous system status logging. Press Ctrl+C to stop.")
    # monitor.log_system_status(interval=10) # Log every 10 seconds
    pass

