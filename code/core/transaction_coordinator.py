import time
import uuid
from enum import Enum
from typing import Optional


class TransactionStatus(Enum):
    CREATED = "CREATED"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


class TransactionParticipant:
    """
    Interface for transaction participants
    """

    def prepare(self, transaction_id: str) -> bool:
        """
        Prepare resources for the transaction
        """
        raise NotImplementedError("Participant must implement prepare method")

    def commit(self, transaction_id: str) -> bool:
        """
        Commit the prepared transaction
        """
        raise NotImplementedError("Participant must implement commit method")

    def abort(self, transaction_id: str) -> bool:
        """
        Abort the transaction
        """
        raise NotImplementedError("Participant must implement abort method")


class TransactionCoordinator:
    """
    Coordinator for distributed transactions
    """

    def __init__(self):
        self.transactions = {}

    def create_transaction(self) -> str:
        """
        Create a new transaction
        """
        transaction_id = str(uuid.uuid4())
        self.transactions[transaction_id] = {
            "status": TransactionStatus.CREATED,
            "participants": [],
            "created_at": time.time(),
        }
        return transaction_id

    def register_participant(
        self, transaction_id: str, participant: TransactionParticipant
    ) -> bool:
        """
        Register a participant in the transaction
        """
        if transaction_id not in self.transactions:
            return False

        self.transactions[transaction_id]["participants"].append(participant)
        return True

    def prepare_transaction(self, transaction_id: str) -> bool:
        """
        Prepare all participants for the transaction
        """
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]

        # Only prepare if in CREATED state
        if transaction["status"] != TransactionStatus.CREATED:
            return False

        # Prepare all participants
        prepared_participants = []
        for participant in transaction["participants"]:
            try:
                if not participant.prepare(transaction_id):
                    # If any participant fails to prepare, abort all participants
                    for p in transaction["participants"]:
                        p.abort(transaction_id)

                    transaction["status"] = TransactionStatus.ABORTED
                    return False

                prepared_participants.append(participant)
            except Exception:
                # If any participant throws an exception, abort all participants
                for p in transaction["participants"]:
                    p.abort(transaction_id)

                transaction["status"] = TransactionStatus.ABORTED
                return False

        # All participants prepared successfully
        transaction["status"] = TransactionStatus.PREPARED
        return True

    def commit_transaction(self, transaction_id: str) -> bool:
        """
        Commit the prepared transaction
        """
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]

        # Only commit if in PREPARED state
        if transaction["status"] != TransactionStatus.PREPARED:
            return False

        # Commit all participants
        for participant in transaction["participants"]:
            try:
                if not participant.commit(transaction_id):
                    # If any participant fails to commit, we're in an inconsistent state
                    # In a real system, we would need a recovery mechanism here
                    return False
            except Exception:
                # If any participant throws an exception, we're in an inconsistent state
                # In a real system, we would need a recovery mechanism here
                return False

        # All participants committed successfully
        transaction["status"] = TransactionStatus.COMMITTED
        return True

    def abort_transaction(self, transaction_id: str) -> bool:
        """
        Abort the transaction
        """
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]

        # Abort all participants
        for participant in transaction["participants"]:
            try:
                participant.abort(transaction_id)
            except Exception:
                # Log the exception but continue aborting other participants
                pass

        # Mark transaction as aborted
        transaction["status"] = TransactionStatus.ABORTED
        return True

    def get_transaction_status(
        self, transaction_id: str
    ) -> Optional[TransactionStatus]:
        """
        Get the status of a transaction
        """
        if transaction_id not in self.transactions:
            return None

        return self.transactions[transaction_id]["status"]

    def execute_transaction(self, transaction_id: str) -> bool:
        """
        Execute a transaction (prepare and commit)
        """
        if not self.prepare_transaction(transaction_id):
            return False

        return self.commit_transaction(transaction_id)
