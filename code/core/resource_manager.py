import json
import os
from typing import Any, Dict


class ResourceManager:
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.prepared_resources = {}
        self.temp_dir = "/tmp/transactions"
        os.makedirs(self.temp_dir, exist_ok=True)

    def prepare(
        self,
        transaction_id: str,
        resource_id: str,
        operation: str,
        data: Dict[str, Any],
    ):
        """
        Prepare a resource for a transaction
        """
        # Store the operation details for later commit or abort
        resource_key = f"{transaction_id}:{resource_id}"
        self.prepared_resources[resource_key] = {"operation": operation, "data": data}

        # Persist the prepared state to disk for recovery
        self._persist_prepared_state(transaction_id, resource_id, operation, data)

        return True

    def commit(self, transaction_id: str):
        """
        Commit all prepared resources for the transaction
        """
        # Find all prepared resources for this transaction
        resources_to_commit = {
            k: v
            for k, v in self.prepared_resources.items()
            if k.startswith(f"{transaction_id}:")
        }

        # Commit each resource
        for resource_key, resource_data in resources_to_commit.items():
            try:
                self._execute_operation(
                    resource_data["operation"], resource_data["data"]
                )
                # Remove from prepared resources
                del self.prepared_resources[resource_key]
                # Remove persisted state
                transaction_id, resource_id = resource_key.split(":", 1)
                self._remove_persisted_state(transaction_id, resource_id)
            except Exception as e:
                # Log the error but continue with other resources
                print(f"Error committing resource {resource_key}: {str(e)}")

        return True

    def abort(self, transaction_id: str):
        """
        Abort all prepared resources for the transaction
        """
        # Find all prepared resources for this transaction
        resources_to_abort = {
            k: v
            for k, v in self.prepared_resources.items()
            if k.startswith(f"{transaction_id}:")
        }

        # Abort each resource
        for resource_key, resource_data in resources_to_abort.items():
            try:
                # Remove from prepared resources
                del self.prepared_resources[resource_key]
                # Remove persisted state
                transaction_id, resource_id = resource_key.split(":", 1)
                self._remove_persisted_state(transaction_id, resource_id)
            except Exception as e:
                # Log the error but continue with other resources
                print(f"Error aborting resource {resource_key}: {str(e)}")

        return True

    def _execute_operation(self, operation: str, data: Dict[str, Any]):
        """
        Execute the operation on the resource
        """
        # Implementation depends on the resource type
        if operation == "create":
            # Create resource
            pass
        elif operation == "update":
            # Update resource
            pass
        elif operation == "delete":
            # Delete resource
            pass
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def _persist_prepared_state(
        self,
        transaction_id: str,
        resource_id: str,
        operation: str,
        data: Dict[str, Any],
    ):
        """
        Persist the prepared state to disk for recovery
        """
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        os.makedirs(transaction_dir, exist_ok=True)

        resource_file = os.path.join(transaction_dir, f"{resource_id}.json")
        with open(resource_file, "w") as f:
            json.dump({"operation": operation, "data": data}, f)

    def _remove_persisted_state(self, transaction_id: str, resource_id: str):
        """
        Remove the persisted state from disk
        """
        resource_file = os.path.join(
            self.temp_dir, transaction_id, f"{resource_id}.json"
        )
        if os.path.exists(resource_file):
            os.remove(resource_file)

        # Remove transaction directory if empty
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        if os.path.exists(transaction_dir) and not os.listdir(transaction_dir):
            os.rmdir(transaction_dir)
