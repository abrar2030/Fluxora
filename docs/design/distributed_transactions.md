# Distributed Transaction Protocols Design

## Overview

This document outlines the design for implementing distributed transaction protocols in the Fluxora energy forecasting platform. The design aims to ensure data consistency across distributed services, particularly in the context of horizontal scaling and microservices architecture.

## Design Goals

1. Ensure data consistency across distributed services
2. Support atomic operations spanning multiple services
3. Provide resilience against partial failures
4. Minimize performance impact on normal operations
5. Enable recovery from transaction failures
6. Integrate with the existing horizontal scaling infrastructure

## Transaction Patterns Analysis

### Two-Phase Commit (2PC)

**Pros:**
- Strong consistency guarantees
- Well-established protocol
- Atomic commit across multiple services

**Cons:**
- Blocking protocol (participants wait for coordinator)
- Vulnerable to coordinator failures
- Higher latency due to multiple network roundtrips
- Reduced availability during failures

### Saga Pattern

**Pros:**
- Non-blocking operations
- Higher availability
- Better performance characteristics
- Suitable for long-running transactions

**Cons:**
- Eventually consistent (not immediately consistent)
- Requires compensating transactions
- More complex programming model
- Potential for partial failures

### Outbox Pattern

**Pros:**
- Ensures reliable message delivery
- Compatible with event-driven architecture
- Minimizes dual-writes problems
- Works well with message brokers

**Cons:**
- Requires polling or CDC for outbox table
- Additional storage requirements
- Potential for message duplication

## Selected Approach

After analyzing the transaction patterns, we have selected a **hybrid approach** combining the **Saga Pattern** with the **Outbox Pattern** for the Fluxora platform. This approach provides:

1. **Eventual consistency** with reliable message delivery
2. **High availability** during network partitions
3. **Fault tolerance** through compensating transactions
4. **Scalability** compatible with horizontal scaling

## Architecture Components

### 1. Transaction Coordinator

A central service responsible for orchestrating distributed transactions across multiple services. The coordinator will:

- Track transaction state and participants
- Coordinate transaction steps
- Handle timeouts and retries
- Manage compensating transactions
- Provide transaction logging and monitoring

**Implementation**: We will implement a dedicated Transaction Coordinator service using a stateful design with persistent storage.

### 2. Outbox Service

A service that ensures reliable message delivery between services by using the outbox pattern. The outbox service will:

- Store outgoing messages in a local outbox table
- Reliably deliver messages to destination services
- Handle message retries and deduplication
- Provide message ordering guarantees
- Support message filtering and routing

**Implementation**: We will implement an Outbox Service that uses a database table for message storage and a background worker for message delivery.

### 3. Saga Orchestrator

A service that implements the saga pattern for coordinating complex business transactions. The saga orchestrator will:

- Define and execute transaction steps
- Handle compensating transactions for rollbacks
- Manage transaction state and recovery
- Provide transaction monitoring and logging
- Support parallel and sequential execution

**Implementation**: We will implement a Saga Orchestrator service that uses a state machine approach for transaction management.

## Implementation Details

### Transaction Coordinator Implementation

```python
# transaction_coordinator.py
import uuid
import time
from enum import Enum
from typing import Dict, List, Optional
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

class TransactionState(Enum):
    STARTED = "STARTED"
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    COMMITTING = "COMMITTING"
    COMMITTED = "COMMITTED"
    ABORTING = "ABORTING"
    ABORTED = "ABORTED"

class ParticipantState(Enum):
    PREPARING = "PREPARING"
    PREPARED = "PREPARED"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"
    FAILED = "FAILED"

class Participant(BaseModel):
    service_name: str
    service_url: str
    state: ParticipantState
    prepare_endpoint: str = "/transaction/prepare"
    commit_endpoint: str = "/transaction/commit"
    abort_endpoint: str = "/transaction/abort"

class Transaction(BaseModel):
    id: str
    state: TransactionState
    participants: List[Participant]
    created_at: float
    updated_at: float
    timeout_seconds: int = 30

# In-memory storage for demonstration
# In production, use a persistent database
transactions: Dict[str, Transaction] = {}

app = FastAPI(title="Transaction Coordinator")

@app.post("/transactions")
async def create_transaction(background_tasks: BackgroundTasks):
    """
    Create a new distributed transaction
    """
    transaction_id = str(uuid.uuid4())
    transaction = Transaction(
        id=transaction_id,
        state=TransactionState.STARTED,
        participants=[],
        created_at=time.time(),
        updated_at=time.time()
    )
    transactions[transaction_id] = transaction

    # Start transaction timeout monitor
    background_tasks.add_task(monitor_transaction_timeout, transaction_id)

    return {"transaction_id": transaction_id, "state": transaction.state.value}

@app.post("/transactions/{transaction_id}/participants")
async def add_participant(transaction_id: str, participant: Participant):
    """
    Add a participant to a transaction
    """
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transactions[transaction_id]
    if transaction.state != TransactionState.STARTED:
        raise HTTPException(status_code=400, detail="Transaction already in progress")

    participant.state = ParticipantState.PREPARING
    transaction.participants.append(participant)
    transaction.updated_at = time.time()

    return {"transaction_id": transaction_id, "participant_added": participant.service_name}

@app.post("/transactions/{transaction_id}/prepare")
async def prepare_transaction(transaction_id: str, background_tasks: BackgroundTasks):
    """
    Prepare all participants for commit
    """
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transactions[transaction_id]
    if transaction.state != TransactionState.STARTED:
        raise HTTPException(status_code=400, detail="Transaction in invalid state")

    transaction.state = TransactionState.PREPARING
    transaction.updated_at = time.time()

    # Start prepare phase in background
    background_tasks.add_task(execute_prepare_phase, transaction_id)

    return {"transaction_id": transaction_id, "state": transaction.state.value}

@app.post("/transactions/{transaction_id}/commit")
async def commit_transaction(transaction_id: str, background_tasks: BackgroundTasks):
    """
    Commit the transaction if all participants are prepared
    """
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transactions[transaction_id]
    if transaction.state != TransactionState.PREPARED:
        raise HTTPException(status_code=400, detail="Transaction not prepared")

    # Check if all participants are prepared
    all_prepared = all(p.state == ParticipantState.PREPARED for p in transaction.participants)
    if not all_prepared:
        raise HTTPException(status_code=400, detail="Not all participants are prepared")

    transaction.state = TransactionState.COMMITTING
    transaction.updated_at = time.time()

    # Start commit phase in background
    background_tasks.add_task(execute_commit_phase, transaction_id)

    return {"transaction_id": transaction_id, "state": transaction.state.value}

@app.post("/transactions/{transaction_id}/abort")
async def abort_transaction(transaction_id: str, background_tasks: BackgroundTasks):
    """
    Abort the transaction
    """
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transactions[transaction_id]
    if transaction.state in [TransactionState.COMMITTED, TransactionState.ABORTED]:
        raise HTTPException(status_code=400, detail="Transaction already completed")

    transaction.state = TransactionState.ABORTING
    transaction.updated_at = time.time()

    # Start abort phase in background
    background_tasks.add_task(execute_abort_phase, transaction_id)

    return {"transaction_id": transaction_id, "state": transaction.state.value}

@app.get("/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """
    Get transaction details
    """
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction = transactions[transaction_id]
    return {
        "transaction_id": transaction.id,
        "state": transaction.state.value,
        "participants": [
            {
                "service_name": p.service_name,
                "state": p.state.value
            }
            for p in transaction.participants
        ],
        "created_at": transaction.created_at,
        "updated_at": transaction.updated_at
    }

async def execute_prepare_phase(transaction_id: str):
    """
    Execute the prepare phase of the transaction
    """
    transaction = transactions[transaction_id]
    all_prepared = True

    for participant in transaction.participants:
        try:
            response = requests.post(
                f"{participant.service_url}{participant.prepare_endpoint}",
                json={"transaction_id": transaction_id}
            )
            if response.status_code == 200:
                participant.state = ParticipantState.PREPARED
            else:
                participant.state = ParticipantState.FAILED
                all_prepared = False
        except Exception:
            participant.state = ParticipantState.FAILED
            all_prepared = False

    if all_prepared:
        transaction.state = TransactionState.PREPARED
    else:
        # If any participant failed to prepare, abort the transaction
        transaction.state = TransactionState.ABORTING
        await execute_abort_phase(transaction_id)

    transaction.updated_at = time.time()

async def execute_commit_phase(transaction_id: str):
    """
    Execute the commit phase of the transaction
    """
    transaction = transactions[transaction_id]
    all_committed = True

    for participant in transaction.participants:
        if participant.state == ParticipantState.PREPARED:
            try:
                response = requests.post(
                    f"{participant.service_url}{participant.commit_endpoint}",
                    json={"transaction_id": transaction_id}
                )
                if response.status_code == 200:
                    participant.state = ParticipantState.COMMITTED
                else:
                    participant.state = ParticipantState.FAILED
                    all_committed = False
            except Exception:
                participant.state = ParticipantState.FAILED
                all_committed = False

    if all_committed:
        transaction.state = TransactionState.COMMITTED
    else:
        # In a real system, this would require manual intervention
        # as we're in an inconsistent state
        transaction.state = TransactionState.FAILED

    transaction.updated_at = time.time()

async def execute_abort_phase(transaction_id: str):
    """
    Execute the abort phase of the transaction
    """
    transaction = transactions[transaction_id]

    for participant in transaction.participants:
        if participant.state in [ParticipantState.PREPARING, ParticipantState.PREPARED]:
            try:
                response = requests.post(
                    f"{participant.service_url}{participant.abort_endpoint}",
                    json={"transaction_id": transaction_id}
                )
                if response.status_code == 200:
                    participant.state = ParticipantState.ABORTED
            except Exception:
                participant.state = ParticipantState.FAILED

    transaction.state = TransactionState.ABORTED
    transaction.updated_at = time.time()

async def monitor_transaction_timeout(transaction_id: str):
    """
    Monitor transaction for timeout
    """
    while transaction_id in transactions:
        transaction = transactions[transaction_id]

        # If transaction is completed, stop monitoring
        if transaction.state in [TransactionState.COMMITTED, TransactionState.ABORTED]:
            break

        # Check for timeout
        current_time = time.time()
        if current_time - transaction.updated_at > transaction.timeout_seconds:
            # Transaction timed out, abort it
            transaction.state = TransactionState.ABORTING
            await execute_abort_phase(transaction_id)
            break

        # Sleep for a short time before checking again
        await asyncio.sleep(1)
```

### Outbox Service Implementation

```python
# outbox_service.py
import asyncio
import uuid
import time
from enum import Enum
from typing import Dict, List, Optional
import json
import requests
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./outbox.db"  # Use PostgreSQL in production
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class OutboxMessage(Base):
    __tablename__ = "outbox_messages"

    id = Column(String, primary_key=True, index=True)
    destination_service = Column(String, index=True)
    payload = Column(Text)
    created_at = Column(Float)
    processed = Column(Boolean, default=False)
    processed_at = Column(Float, nullable=True)
    retry_count = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

class MessageStatus(Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class OutboxMessageModel(BaseModel):
    destination_service: str
    payload: Dict

app = FastAPI(title="Outbox Service")

@app.post("/messages")
async def create_message(message: OutboxMessageModel):
    """
    Create a new outbox message
    """
    db = SessionLocal()
    try:
        message_id = str(uuid.uuid4())
        db_message = OutboxMessage(
            id=message_id,
            destination_service=message.destination_service,
            payload=json.dumps(message.payload),
            created_at=time.time(),
            processed=False,
            processed_at=None,
            retry_count=0
        )
        db.add(db_message)
        db.commit()
        return {"message_id": message_id, "status": MessageStatus.PENDING.value}
    finally:
        db.close()

@app.get("/messages/{message_id}")
async def get_message(message_id: str):
    """
    Get message details
    """
    db = SessionLocal()
    try:
        message = db.query(OutboxMessage).filter(OutboxMessage.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return {
            "message_id": message.id,
            "destination_service": message.destination_service,
            "payload": json.loads(message.payload),
            "created_at": message.created_at,
            "processed": message.processed,
            "processed_at": message.processed_at,
            "retry_count": message.retry_count,
            "status": MessageStatus.DELIVERED.value if message.processed else MessageStatus.PENDING.value
        }
    finally:
        db.close()

@app.on_event("startup")
async def start_message_processor():
    """
    Start the background message processor
    """
    asyncio.create_task(process_messages())

async def process_messages():
    """
    Process pending outbox messages
    """
    while True:
        try:
            db = SessionLocal()
            # Get unprocessed messages
            messages = db.query(OutboxMessage).filter(
                OutboxMessage.processed == False
            ).order_by(OutboxMessage.created_at).limit(10).all()

            for message in messages:
                try:
                    # Get service URL from service registry
                    service_url = get_service_url(message.destination_service)
                    if not service_url:
                        continue

                    # Send message to destination service
                    response = requests.post(
                        f"{service_url}/messages",
                        json=json.loads(message.payload)
                    )

                    if response.status_code == 200:
                        # Mark message as processed
                        message.processed = True
                        message.processed_at = time.time()
                    else:
                        # Increment retry count
                        message.retry_count += 1
                except Exception as e:
                    print(f"Error processing message {message.id}: {str(e)}")
                    message.retry_count += 1

            db.commit()
        except Exception as e:
            print(f"Error in message processor: {str(e)}")
        finally:
            db.close()

        # Sleep before next processing cycle
        await asyncio.sleep(1)

def get_service_url(service_name: str) -> Optional[str]:
    """
    Get service URL from service registry
    """
    try:
        registry_url = "http://service-registry:8500"
        response = requests.get(f"{registry_url}/v1/catalog/service/{service_name}")
        if response.status_code == 200:
            services = response.json()
            if services:
                service = services[0]
                return f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        return None
    except Exception as e:
        print(f"Error getting service URL: {str(e)}")
        return None
```

### Saga Orchestrator Implementation

```python
# saga_orchestrator.py
import uuid
import time
import json
from enum import Enum
from typing import Dict, List, Optional, Callable
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

class SagaState(Enum):
    STARTED = "STARTED"
    EXECUTING = "EXECUTING"
    COMPENSATING = "COMPENSATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class StepState(Enum):
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"

class SagaStep(BaseModel):
    id: str
    service_name: str
    action_endpoint: str
    compensation_endpoint: str
    state: StepState
    payload: Dict
    result: Optional[Dict] = None

class Saga(BaseModel):
    id: str
    name: str
    state: SagaState
    steps: List[SagaStep]
    current_step_index: int
    created_at: float
    updated_at: float

# In-memory storage for demonstration
# In production, use a persistent database
sagas: Dict[str, Saga] = {}

app = FastAPI(title="Saga Orchestrator")

@app.post("/sagas")
async def create_saga(name: str, steps: List[Dict], background_tasks: BackgroundTasks):
    """
    Create a new saga with the specified steps
    """
    saga_id = str(uuid.uuid4())

    saga_steps = []
    for i, step_data in enumerate(steps):
        step = SagaStep(
            id=f"{saga_id}-step-{i}",
            service_name=step_data["service_name"],
            action_endpoint=step_data["action_endpoint"],
            compensation_endpoint=step_data["compensation_endpoint"],
            state=StepState.PENDING,
            payload=step_data["payload"]
        )
        saga_steps.append(step)

    saga = Saga(
        id=saga_id,
        name=name,
        state=SagaState.STARTED,
        steps=saga_steps,
        current_step_index=0,
        created_at=time.time(),
        updated_at=time.time()
    )

    sagas[saga_id] = saga

    # Start saga execution in background
    background_tasks.add_task(execute_saga, saga_id)

    return {"saga_id": saga_id, "state": saga.state.value}

@app.get("/sagas/{saga_id}")
async def get_saga(saga_id: str):
    """
    Get saga details
    """
    if saga_id not in sagas:
        raise HTTPException(status_code=404, detail="Saga not found")

    saga = sagas[saga_id]
    return {
        "saga_id": saga.id,
        "name": saga.name,
        "state": saga.state.value,
        "steps": [
            {
                "id": step.id,
                "service_name": step.service_name,
                "state": step.state.value,
                "result": step.result
            }
            for step in saga.steps
        ],
        "current_step_index": saga.current_step_index,
        "created_at": saga.created_at,
        "updated_at": saga.updated_at
    }

async def execute_saga(saga_id: str):
    """
    Execute the saga steps in sequence
    """
    saga = sagas[saga_id]
    saga.state = SagaState.EXECUTING

    while saga.current_step_index < len(saga.steps):
        step = saga.steps[saga.current_step_index]
        step.state = StepState.EXECUTING

        try:
            # Get service URL from service registry
            service_url = get_service_url(step.service_name)
            if not service_url:
                step.state = StepState.FAILED
                await compensate_saga(saga_id)
                return

            # Execute step action
            response = requests.post(
                f"{service_url}{step.action_endpoint}",
                json=step.payload
            )

            if response.status_code == 200:
                step.state = StepState.EXECUTED
                step.result = response.json()
                saga.current_step_index += 1
            else:
                step.state = StepState.FAILED
                await compensate_saga(saga_id)
                return
        except Exception as e:
            print(f"Error executing step {step.id}: {str(e)}")
            step.state = StepState.FAILED
            await compensate_saga(saga_id)
            return

        saga.updated_at = time.time()

    # All steps executed successfully
    saga.state = SagaState.COMPLETED
    saga.updated_at = time.time()

async def compensate_saga(saga_id: str):
    """
    Compensate the saga by executing compensation steps in reverse order
    """
    saga = sagas[saga_id]
    saga.state = SagaState.COMPENSATING

    for i in range(saga.current_step_index - 1, -1, -1):
        step = saga.steps[i]
        if step.state == StepState.EXECUTED:
            step.state = StepState.COMPENSATING

            try:
                # Get service URL from service registry
                service_url = get_service_url(step.service_name)
                if not service_url:
                    step.state = StepState.FAILED
                    continue

                # Execute step compensation
                response = requests.post(
                    f"{service_url}{step.compensation_endpoint}",
                    json={"step_id": step.id, "original_payload": step.payload}
                )

                if response.status_code == 200:
                    step.state = StepState.COMPENSATED
                else:
                    step.state = StepState.FAILED
            except Exception as e:
                print(f"Error compensating step {step.id}: {str(e)}")
                step.state = StepState.FAILED

            saga.updated_at = time.time()

    saga.state = SagaState.FAILED
    saga.updated_at = time.time()

def get_service_url(service_name: str) -> Optional[str]:
    """
    Get service URL from service registry
    """
    try:
        registry_url = "http://service-registry:8500"
        response = requests.get(f"{registry_url}/v1/catalog/service/{service_name}")
        if response.status_code == 200:
            services = response.json()
            if services:
                service = services[0]
                return f"http://{service['ServiceAddress']}:{service['ServicePort']}"
        return None
    except Exception as e:
        print(f"Error getting service URL: {str(e)}")
        return None
```

## Kubernetes Deployment

### Transaction Coordinator Deployment

```yaml
# transaction-coordinator.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: transaction-coordinator
  namespace: fluxora
spec:
  replicas: 3
  selector:
    matchLabels:
      app: transaction-coordinator
  template:
    metadata:
      labels:
        app: transaction-coordinator
    spec:
      containers:
      - name: transaction-coordinator
        image: fluxora/transaction-coordinator:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
        env:
        - name: SERVICE_REGISTRY_URL
          value: "http://service-registry:8500"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: transaction-coordinator
  namespace: fluxora
spec:
  selector:
    app: transaction-coordinator
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Outbox Service Deployment

```yaml
# outbox-service.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: outbox-service
  namespace: fluxora
spec:
  replicas: 3
  selector:
    matchLabels:
      app: outbox-service
  template:
    metadata:
      labels:
        app: outbox-service
    spec:
      containers:
      - name: outbox-service
        image: fluxora/outbox-service:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
        env:
        - name: SERVICE_REGISTRY_URL
          value: "http://service-registry:8500"
        - name: DATABASE_URL
          value: "postgresql://user:password@postgres:5432/outbox"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: outbox-service
  namespace: fluxora
spec:
  selector:
    app: outbox-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Saga Orchestrator Deployment

```yaml
# saga-orchestrator.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: saga-orchestrator
  namespace: fluxora
spec:
  replicas: 3
  selector:
    matchLabels:
      app: saga-orchestrator
  template:
    metadata:
      labels:
        app: saga-orchestrator
    spec:
      containers:
      - name: saga-orchestrator
        image: fluxora/saga-orchestrator:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "200m"
            memory: "256Mi"
        env:
        - name: SERVICE_REGISTRY_URL
          value: "http://service-registry:8500"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: saga-orchestrator
  namespace: fluxora
spec:
  selector:
    app: saga-orchestrator
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

## Integration with Existing Services

### Transaction Participant Interface

Each service that participates in distributed transactions must implement the following interface:

```python
# transaction_participant.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class TransactionRequest(BaseModel):
    transaction_id: str

def add_transaction_endpoints(app: FastAPI, resource_manager):
    """
    Add transaction participant endpoints to the FastAPI application
    """
    @app.post("/transaction/prepare")
    async def prepare_transaction(request: TransactionRequest):
        """
        Prepare resources for the transaction
        """
        try:
            # Prepare resources but don't commit yet
            resource_manager.prepare(request.transaction_id)
            return {"status": "prepared"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/transaction/commit")
    async def commit_transaction(request: TransactionRequest):
        """
        Commit the prepared transaction
        """
        try:
            # Commit the prepared resources
            resource_manager.commit(request.transaction_id)
            return {"status": "committed"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/transaction/abort")
    async def abort_transaction(request: TransactionRequest):
        """
        Abort the transaction
        """
        try:
            # Release any prepared resources
            resource_manager.abort(request.transaction_id)
            return {"status": "aborted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

### Resource Manager Implementation

Each service must implement a resource manager to handle transaction operations:

```python
# resource_manager.py
from typing import Dict, Any
import json
import os

class ResourceManager:
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.prepared_resources = {}
        self.temp_dir = "/tmp/transactions"
        os.makedirs(self.temp_dir, exist_ok=True)

    def prepare(self, transaction_id: str, resource_id: str, operation: str, data: Dict[str, Any]):
        """
        Prepare a resource for a transaction
        """
        # Store the operation details for later commit or abort
        resource_key = f"{transaction_id}:{resource_id}"
        self.prepared_resources[resource_key] = {
            "operation": operation,
            "data": data
        }

        # Persist the prepared state to disk for recovery
        self._persist_prepared_state(transaction_id, resource_id, operation, data)

        return True

    def commit(self, transaction_id: str):
        """
        Commit all prepared resources for the transaction
        """
        # Find all prepared resources for this transaction
        resources_to_commit = {k: v for k, v in self.prepared_resources.items() if k.startswith(f"{transaction_id}:")}

        # Commit each resource
        for resource_key, resource_data in resources_to_commit.items():
            try:
                self._execute_operation(resource_data["operation"], resource_data["data"])
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
        resources_to_abort = {k: v for k, v in self.prepared_resources.items() if k.startswith(f"{transaction_id}:")}

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

    def _persist_prepared_state(self, transaction_id: str, resource_id: str, operation: str, data: Dict[str, Any]):
        """
        Persist the prepared state to disk for recovery
        """
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        os.makedirs(transaction_dir, exist_ok=True)

        resource_file = os.path.join(transaction_dir, f"{resource_id}.json")
        with open(resource_file, "w") as f:
            json.dump({
                "operation": operation,
                "data": data
            }, f)

    def _remove_persisted_state(self, transaction_id: str, resource_id: str):
        """
        Remove the persisted state from disk
        """
        resource_file = os.path.join(self.temp_dir, transaction_id, f"{resource_id}.json")
        if os.path.exists(resource_file):
            os.remove(resource_file)

        # Remove transaction directory if empty
        transaction_dir = os.path.join(self.temp_dir, transaction_id)
        if os.path.exists(transaction_dir) and not os.listdir(transaction_dir):
            os.rmdir(transaction_dir)
```

### Outbox Pattern Integration

Each service that needs to send messages to other services should use the outbox pattern:

```python
# outbox_client.py
import requests
from typing import Dict, Any

class OutboxClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.outbox_service_url = "http://outbox-service:8000"

    def send_message(self, destination_service: str, payload: Dict[str, Any]):
        """
        Send a message to another service via the outbox
        """
        try:
            response = requests.post(
                f"{self.outbox_service_url}/messages",
                json={
                    "destination_service": destination_service,
                    "payload": {
                        "sender": self.service_name,
                        "content": payload
                    }
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error sending message: {response.text}")
                return None
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return None
```

### Saga Pattern Integration

Services can initiate sagas for complex business transactions:

```python
# saga_client.py
import requests
from typing import Dict, List, Any

class SagaClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.saga_orchestrator_url = "http://saga-orchestrator:8000"

    def start_saga(self, saga_name: str, steps: List[Dict[str, Any]]):
        """
        Start a new saga with the specified steps
        """
        try:
            response = requests.post(
                f"{self.saga_orchestrator_url}/sagas",
                json={
                    "name": saga_name,
                    "steps": steps
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error starting saga: {response.text}")
                return None
        except Exception as e:
            print(f"Error starting saga: {str(e)}")
            return None

    def get_saga_status(self, saga_id: str):
        """
        Get the status of a saga
        """
        try:
            response = requests.get(
                f"{self.saga_orchestrator_url}/sagas/{saga_id}"
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting saga status: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting saga status: {str(e)}")
            return None
```

## Testing Strategy

The distributed transaction components will be tested as follows:

1. **Unit Testing**: Each component will have comprehensive unit tests to verify its functionality.
2. **Integration Testing**: The components will be tested together to ensure they work as expected.
3. **Failure Testing**: The system will be tested under failure conditions to verify its resilience.
4. **Performance Testing**: The system will be subjected to performance tests to verify its scalability.

## Conclusion

This design provides a comprehensive approach to implementing distributed transaction protocols for the Fluxora platform. By combining the Saga Pattern with the Outbox Pattern, the design ensures data consistency across distributed services while maintaining high availability and performance. The implementation includes a transaction coordinator, outbox service, and saga orchestrator, along with the necessary integration points for existing services.
