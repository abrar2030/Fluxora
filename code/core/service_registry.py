import os
import requests
from fastapi import FastAPI
from core.logging import get_logger

logger = get_logger(__name__)


def register_service(app: FastAPI, service_name: str, service_version: str) -> Any:
    """
    Register service with the service registry
    """
    registry_url = os.getenv("SERVICE_REGISTRY_URL", "http://service-registry:8500")
    service_id = f"{service_name}-{os.getenv('HOSTNAME', 'unknown')}"
    service_port = int(os.getenv("SERVICE_PORT", "8000"))

    @app.on_event("startup")
    async def startup_event():
        try:
            response = requests.put(
                f"{registry_url}/v1/agent/service/register",
                json={
                    "ID": service_id,
                    "Name": service_name,
                    "Port": service_port,
                    "Check": {
                        "HTTP": f"http://{os.getenv('HOSTNAME')}:{service_port}/health",
                        "Interval": "10s",
                        "Timeout": "1s",
                    },
                    "Meta": {"version": service_version},
                },
            )
            if response.status_code == 200:
                logger.info(f"Successfully registered service {service_id}")
            else:
                logger.info(f"Failed to register service: {response.text}")
        except Exception as e:
            logger.info(f"Error registering service: {str(e)}")

    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            response = requests.put(
                f"{registry_url}/v1/agent/service/deregister/{service_id}"
            )
            if response.status_code == 200:
                logger.info(f"Successfully deregistered service {service_id}")
            else:
                logger.info(f"Failed to deregister service: {response.text}")
        except Exception as e:
            logger.info(f"Error deregistering service: {str(e)}")
