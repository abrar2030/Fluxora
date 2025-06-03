import time
import psutil
import os
import json
import threading
from datetime import datetime
from packages.shared.utils.logger import get_logger, get_metrics_logger

logger = get_logger(__name__)
metrics_logger = get_metrics_logger(__name__ + ".metrics")

class SystemMonitor:
    """A comprehensive system monitor to track CPU, memory, disk usage, and network activity."""

    def __init__(self, disk_path: str = None, log_interval: int = 60, metrics_file: str = None):
        """
        Initializes the SystemMonitor.
        Args:
            disk_path (str, optional): The disk path to monitor. Defaults to root (/) on Unix-like systems.
            log_interval (int, optional): Default interval in seconds for continuous monitoring. Defaults to 60.
            metrics_file (str, optional): Path to save metrics logs. If None, uses standard logger.
        """
        self.disk_path = disk_path or ("/" if os.name != "nt" else "C:\\")
        self.log_interval = log_interval
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()

        # Configure metrics logger if file is provided
        if metrics_file:
            self.metrics_logger = get_metrics_logger(__name__ + ".metrics", log_file=metrics_file)
        else:
            self.metrics_logger = metrics_logger

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

    def get_cpu_details(self) -> dict:
        """
        Gets detailed CPU information including per-core usage.
        Returns:
            dict: A dictionary containing CPU details including per-core usage,
                  or an empty dict if an error occurs.
        """
        try:
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "per_core_percent": psutil.cpu_percent(interval=1.0, percpu=True),
                "overall_percent": psutil.cpu_percent(interval=1.0)
            }

            # Add CPU frequency if available
            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info["frequency_mhz"] = {
                        "current": freq.current,
                        "min": freq.min,
                        "max": freq.max
                    }
            except Exception:
                pass

            return cpu_info
        except Exception as e:
            logger.error(f"Error getting detailed CPU info: {e}")
            return {}

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
                "cached": getattr(mem, 'cached', 0),  # May not be available on all platforms
                "buffers": getattr(mem, 'buffers', 0)  # May not be available on all platforms
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}

    def get_swap_usage(self) -> dict:
        """
        Gets the current swap memory usage statistics.
        Returns:
            dict: A dictionary containing swap memory statistics,
                  or an empty dict if an error occurs.
        """
        try:
            swap = psutil.swap_memory()
            return {
                "total": swap.total,
                "used": swap.used,
                "free": swap.free,
                "percent": swap.percent,
                "sin": getattr(swap, 'sin', 0),  # May not be available on all platforms
                "sout": getattr(swap, 'sout', 0)  # May not be available on all platforms
            }
        except Exception as e:
            logger.error(f"Error getting swap usage: {e}")
            return {}

    def get_disk_usage(self, path: str = None) -> dict:
        """
        Gets the disk usage statistics for the specified path.
        Args:
            path (str, optional): The path to check disk usage. Defaults to self.disk_path.
        Returns:
            dict: A dictionary containing total, used, free disk space in bytes, and usage percentage,
                  or an empty dict if an error occurs.
        """
        check_path = path or self.disk_path
        try:
            disk = psutil.disk_usage(check_path)
            return {
                "path": check_path,
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent,
            }
        except Exception as e:
            logger.error(f"Error getting disk usage for path {check_path}: {e}")
            return {}

    def get_disk_io_counters(self, perdisk: bool = False) -> dict:
        """
        Gets disk I/O statistics.
        Args:
            perdisk (bool, optional): Whether to return stats per disk. Defaults to False.
        Returns:
            dict: A dictionary containing disk I/O statistics,
                  or an empty dict if an error occurs.
        """
        try:
            return psutil.disk_io_counters(perdisk=perdisk)._asdict()
        except Exception as e:
            logger.error(f"Error getting disk I/O counters: {e}")
            return {}

    def get_network_io_counters(self, pernic: bool = False) -> dict:
        """
        Gets network I/O statistics.
        Args:
            pernic (bool, optional): Whether to return stats per network interface. Defaults to False.
        Returns:
            dict: A dictionary containing network I/O statistics,
                  or an empty dict if an error occurs.
        """
        try:
            if pernic:
                # Convert each interface's named tuple to dict
                return {nic: stats._asdict() for nic, stats in psutil.net_io_counters(pernic=True).items()}
            else:
                return psutil.net_io_counters(pernic=False)._asdict()
        except Exception as e:
            logger.error(f"Error getting network I/O counters: {e}")
            return {}

    def get_process_info(self, pid: int = None) -> dict:
        """
        Gets information about a specific process or all processes.
        Args:
            pid (int, optional): Process ID to get info for. If None, returns info for all processes.
        Returns:
            dict: A dictionary containing process information,
                  or an empty dict if an error occurs.
        """
        try:
            if pid:
                try:
                    p = psutil.Process(pid)
                    return {
                        "pid": p.pid,
                        "name": p.name(),
                        "status": p.status(),
                        "cpu_percent": p.cpu_percent(interval=0.1),
                        "memory_percent": p.memory_percent(),
                        "memory_info": p.memory_info()._asdict(),
                        "create_time": datetime.fromtimestamp(p.create_time()).isoformat(),
                        "username": p.username(),
                        "cmdline": p.cmdline()
                    }
                except psutil.NoSuchProcess:
                    logger.warning(f"Process with PID {pid} not found")
                    return {}
            else:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent']):
                    processes.append(proc.info)
                return {"processes": processes}
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {}

    def get_system_info(self) -> dict:
        """
        Gets comprehensive system information.
        Returns:
            dict: A dictionary containing system information,
                  or an empty dict if an error occurs.
        """
        try:
            boot_time = psutil.boot_time()
            return {
                "system": {
                    "hostname": os.uname().nodename if hasattr(os, 'uname') else platform.node(),
                    "platform": sys.platform,
                    "boot_time": datetime.fromtimestamp(boot_time).isoformat(),
                    "uptime_seconds": time.time() - boot_time
                },
                "cpu": self.get_cpu_details(),
                "memory": self.get_memory_usage(),
                "swap": self.get_swap_usage(),
                "disk": self.get_disk_usage(),
                "network": self.get_network_io_counters(pernic=True)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}

    def log_system_status(self, interval: float = None):
        """
        Logs the current system status (CPU, memory, disk) at regular intervals.
        Args:
            interval (float, optional): The interval in seconds between status logs.
                                       If None, uses self.log_interval.
        """
        interval = interval or self.log_interval
        logger.info(f"Starting system monitoring. Disk path: {self.disk_path}, Interval: {interval}s")
        try:
            while True:
                cpu = self.get_cpu_usage()
                mem = self.get_memory_usage()
                disk = self.get_disk_usage()
                net = self.get_network_io_counters()

                logger.info(f"CPU: {cpu}%, Memory: {mem.get('percent')}%, Disk ({self.disk_path}): {disk.get('percent')}%")

                # Log detailed metrics in JSON format
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "cpu_percent": cpu,
                    "memory_percent": mem.get('percent'),
                    "disk_percent": disk.get('percent'),
                    "memory_used_gb": mem.get('used', 0) / (1024**3),
                    "memory_total_gb": mem.get('total', 0) / (1024**3),
                    "disk_used_gb": disk.get('used', 0) / (1024**3),
                    "disk_total_gb": disk.get('total', 0) / (1024**3),
                    "network_bytes_sent": net.get('bytes_sent', 0),
                    "network_bytes_recv": net.get('bytes_recv', 0)
                }

                self.metrics_logger.info("system_metrics", extra=metrics)

                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("System monitoring stopped by user.")
        except Exception as e:
            logger.error(f"An error occurred during system monitoring: {e}")

    def start_monitoring_thread(self, interval: float = None):
        """
        Starts system monitoring in a background thread.
        Args:
            interval (float, optional): The interval in seconds between status logs.
                                       If None, uses self.log_interval.
        """
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.warning("Monitoring thread is already running")
            return

        interval = interval or self.log_interval
        self._stop_monitoring.clear()

        def _monitor_thread():
            logger.info(f"Starting system monitoring thread. Interval: {interval}s")
            try:
                while not self._stop_monitoring.is_set():
                    cpu = self.get_cpu_usage(interval=0.1)  # Quick check
                    mem = self.get_memory_usage()
                    disk = self.get_disk_usage()
                    net = self.get_network_io_counters()

                    # Log detailed metrics in JSON format
                    metrics = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "cpu_percent": cpu,
                        "memory_percent": mem.get('percent'),
                        "disk_percent": disk.get('percent'),
                        "memory_used_gb": mem.get('used', 0) / (1024**3),
                        "memory_total_gb": mem.get('total', 0) / (1024**3),
                        "disk_used_gb": disk.get('used', 0) / (1024**3),
                        "disk_total_gb": disk.get('total', 0) / (1024**3),
                        "network_bytes_sent": net.get('bytes_sent', 0),
                        "network_bytes_recv": net.get('bytes_recv', 0)
                    }

                    self.metrics_logger.info("system_metrics", extra=metrics)

                    # Sleep for the interval, but check stop flag periodically
                    for _ in range(int(interval)):
                        if self._stop_monitoring.is_set():
                            break
                        time.sleep(1)
            except Exception as e:
                logger.error(f"Error in monitoring thread: {e}")
            finally:
                logger.info("System monitoring thread stopped")

        self._monitoring_thread = threading.Thread(target=_monitor_thread, daemon=True)
        self._monitoring_thread.start()
        logger.info("System monitoring thread started")

    def stop_monitoring_thread(self):
        """
        Stops the background monitoring thread if it's running.
        """
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            logger.info("Stopping system monitoring thread...")
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            logger.info("System monitoring thread stopped")
        else:
            logger.warning("No monitoring thread is running")

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

    # Example of background monitoring
    logger.info("Starting background monitoring for 30 seconds...")
    monitor.start_monitoring_thread(interval=5)  # Log every 5 seconds

    # Simulate some work
    time.sleep(30)

    # Stop monitoring
    monitor.stop_monitoring_thread()
    logger.info("Background monitoring stopped")
