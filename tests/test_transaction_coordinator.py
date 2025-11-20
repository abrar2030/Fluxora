import os
import sys
import unittest
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fluxora.core.transaction_coordinator import (
    TransactionCoordinator,
    TransactionParticipant,
    TransactionStatus,
)


class TestTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        self.coordinator = TransactionCoordinator()

    def test_create_transaction(self):
        """Test that create_transaction returns a valid transaction ID"""
        transaction_id = self.coordinator.create_transaction()
        self.assertIsNotNone(transaction_id)
        self.assertIsInstance(transaction_id, str)
        self.assertTrue(len(transaction_id) > 0)

    def test_register_participant(self):
        """Test that register_participant adds a participant to the transaction"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create a mock participant
        participant = Mock(spec=TransactionParticipant)
        participant.prepare.return_value = True
        participant.commit.return_value = True
        participant.abort.return_value = True

        # Register the participant
        self.coordinator.register_participant(transaction_id, participant)

        # Verify the participant was added
        self.assertIn(transaction_id, self.coordinator.transactions)
        self.assertIn(
            participant, self.coordinator.transactions[transaction_id]["participants"]
        )

    def test_prepare_transaction_success(self):
        """Test that prepare_transaction prepares all participants"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Prepare the transaction
        result = self.coordinator.prepare_transaction(transaction_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the participants were prepared
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.PREPARED,
        )

    def test_prepare_transaction_failure(self):
        """Test that prepare_transaction aborts if any participant fails to prepare"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = False  # This participant will fail
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Prepare the transaction
        result = self.coordinator.prepare_transaction(transaction_id)

        # Verify the result
        self.assertFalse(result)

        # Verify the participants were prepared/aborted
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )

    def test_commit_transaction_success(self):
        """Test that commit_transaction commits all participants"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Set transaction status to PREPARED
        self.coordinator.transactions[transaction_id][
            "status"
        ] = TransactionStatus.PREPARED

        # Commit the transaction
        result = self.coordinator.commit_transaction(transaction_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the participants were committed
        participant1.commit.assert_called_once_with(transaction_id)
        participant2.commit.assert_called_once_with(transaction_id)

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.COMMITTED,
        )

    def test_commit_transaction_not_prepared(self):
        """Test that commit_transaction fails if the transaction is not prepared"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant = Mock(spec=TransactionParticipant)
        participant.prepare.return_value = True
        participant.commit.return_value = True
        participant.abort.return_value = True

        # Register the participant
        self.coordinator.register_participant(transaction_id, participant)

        # Commit the transaction without preparing
        result = self.coordinator.commit_transaction(transaction_id)

        # Verify the result
        self.assertFalse(result)

        # Verify the participant was not committed
        participant.commit.assert_not_called()

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.CREATED,
        )

    def test_abort_transaction(self):
        """Test that abort_transaction aborts all participants"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Abort the transaction
        result = self.coordinator.abort_transaction(transaction_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the participants were aborted
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )

    def test_get_transaction_status(self):
        """Test that get_transaction_status returns the correct status"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Get the initial status
        status = self.coordinator.get_transaction_status(transaction_id)
        self.assertEqual(status, TransactionStatus.CREATED)

        # Change the status
        self.coordinator.transactions[transaction_id][
            "status"
        ] = TransactionStatus.PREPARED

        # Get the updated status
        status = self.coordinator.get_transaction_status(transaction_id)
        self.assertEqual(status, TransactionStatus.PREPARED)

    def test_get_transaction_status_invalid_id(self):
        """Test that get_transaction_status returns None for invalid transaction ID"""
        status = self.coordinator.get_transaction_status("invalid_id")
        self.assertIsNone(status)

    def test_execute_transaction_success(self):
        """Test that execute_transaction successfully executes a transaction"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = True
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Execute the transaction
        result = self.coordinator.execute_transaction(transaction_id)

        # Verify the result
        self.assertTrue(result)

        # Verify the participants were prepared and committed
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.commit.assert_called_once_with(transaction_id)
        participant2.commit.assert_called_once_with(transaction_id)

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.COMMITTED,
        )

    def test_execute_transaction_prepare_failure(self):
        """Test that execute_transaction aborts if prepare fails"""
        # Create a transaction
        transaction_id = self.coordinator.create_transaction()

        # Create mock participants
        participant1 = Mock(spec=TransactionParticipant)
        participant1.prepare.return_value = True
        participant1.commit.return_value = True
        participant1.abort.return_value = True

        participant2 = Mock(spec=TransactionParticipant)
        participant2.prepare.return_value = False  # This participant will fail
        participant2.commit.return_value = True
        participant2.abort.return_value = True

        # Register the participants
        self.coordinator.register_participant(transaction_id, participant1)
        self.coordinator.register_participant(transaction_id, participant2)

        # Execute the transaction
        result = self.coordinator.execute_transaction(transaction_id)

        # Verify the result
        self.assertFalse(result)

        # Verify the participants were prepared and aborted
        participant1.prepare.assert_called_once_with(transaction_id)
        participant2.prepare.assert_called_once_with(transaction_id)
        participant1.abort.assert_called_once_with(transaction_id)
        participant2.abort.assert_called_once_with(transaction_id)
        participant1.commit.assert_not_called()
        participant2.commit.assert_not_called()

        # Verify the transaction status
        self.assertEqual(
            self.coordinator.transactions[transaction_id]["status"],
            TransactionStatus.ABORTED,
        )


if __name__ == "__main__":
    unittest.main()
