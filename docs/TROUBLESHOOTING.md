# Troubleshooting Guide

Common issues and solutions for Fluxora installation, configuration, and usage.

---

## 📑 Table of Contents

- [Installation Issues](#installation-issues)
- [API Issues](#api-issues)
- [Database Issues](#database-issues)
- [Model Training Issues](#model-training-issues)
- [Docker Issues](#docker-issues)
- [Kubernetes Issues](#kubernetes-issues)
- [Performance Issues](#performance-issues)
- [Common Error Messages](#common-error-messages)

---

## Installation Issues

### Issue: ModuleNotFoundError: No module named 'fastapi'

**Symptoms:**

```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Dependencies not installed or wrong Python environment

**Solution:**

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

### Issue: Permission denied when installing packages

**Symptoms:**

```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Cause:** Trying to install globally without sudo or conflicts

**Solution:**

```bash
# Option 1: Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option 2: Install with --user flag
pip install --user -r requirements.txt

# Option 3: Use sudo (not recommended)
sudo pip install -r requirements.txt
```

---

### Issue: Python version mismatch

**Symptoms:**

```
SyntaxError: invalid syntax
```

Or features not working as expected.

**Cause:** Python version < 3.9

**Solution:**

```bash
# Check Python version
python --version

# If < 3.9, install Python 3.9+
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.9 python3.9-venv

# Use specific Python version
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## API Issues

### Issue: Port 8000 already in use

**Symptoms:**

```
ERROR: [Errno 98] Address already in use
```

**Cause:** Another process using port 8000

**Solution:**

```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn main:app --port 8001
```

---

### Issue: CORS errors in browser

**Symptoms:**

```
Access to fetch at 'http://localhost:8000/v1/data/' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Cause:** Frontend origin not in CORS whitelist

**Solution:**

```python
# In code/main.py, add your origin
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Add your frontend URL here
]
```

Or set in environment:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

### Issue: 401 Unauthorized on API calls

**Symptoms:**

```json
{ "detail": "Not authenticated" }
```

**Cause:** Missing or invalid authentication token

**Solution:**

```bash
# 1. Register and login to get token
TOKEN=$(curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}' \
  | jq -r '.access_token')

# 2. Use token in Authorization header
curl -X GET http://localhost:8000/v1/predictions/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Verify token is not expired (30-day expiry)
```

---

### Issue: API returns 500 Internal Server Error

**Symptoms:**

```json
{ "detail": "Internal Server Error" }
```

**Cause:** Various backend issues

**Solution:**

```bash
# 1. Check API logs
tail -f logs/fluxora.log

# 2. Run in debug mode
cd code
DEBUG=true python main.py

# 3. Check for specific errors in logs
grep ERROR logs/fluxora.log

# 4. Verify database connection
python -c "from backend.database import engine; engine.connect()"
```

---

## Database Issues

### Issue: Database connection failed

**Symptoms:**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Cause:** Database not running or wrong credentials

**Solution:**

```bash
# For PostgreSQL
# 1. Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# 2. Start PostgreSQL if stopped
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# 3. Verify connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/fluxora

# 4. Test connection manually
psql -U user -d fluxora -h localhost

# For SQLite (development)
# 1. Check file exists
ls -l code/fluxora.db

# 2. Verify permissions
chmod 644 code/fluxora.db
```

---

### Issue: Database tables don't exist

**Symptoms:**

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "users" does not exist
```

**Cause:** Database not initialized

**Solution:**

```bash
# Initialize database
cd code
python -c "from backend.database import init_db; init_db()"

# Or run migrations if using Alembic
alembic upgrade head
```

---

### Issue: Database migration errors

**Symptoms:**

```
ERROR [alembic.env] Can't locate revision identified by 'xxxxx'
```

**Cause:** Migration state mismatch

**Solution:**

```bash
# Reset migrations (CAUTION: loses data)
# 1. Drop all tables
python -c "from backend.database import Base, engine; Base.metadata.drop_all(engine)"

# 2. Recreate tables
python -c "from backend.database import init_db; init_db()"

# For production, use proper migrations
alembic downgrade base
alembic upgrade head
```

---

## Model Training Issues

### Issue: Model file not found

**Symptoms:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'fluxora_model.joblib'
```

**Cause:** Model hasn't been trained yet

**Solution:**

```bash
# Train the model
cd code
python models/train.py

# Verify model file exists
ls -lh fluxora_model.joblib

# Check file size (should be > 1MB)
```

---

### Issue: Out of memory during training

**Symptoms:**

```
MemoryError: Unable to allocate array
```

Or system becomes unresponsive

**Cause:** Insufficient RAM for large datasets

**Solution:**

```python
# 1. Reduce dataset size
df = df.sample(frac=0.5)  # Use 50% of data

# 2. Use batch processing
for chunk in pd.read_csv('data.csv', chunksize=10000):
    process(chunk)

# 3. Reduce model complexity
# In config/config.yaml
model:
  xgboost:
    n_estimators: 100  # Reduce from 500
    max_depth: 4       # Reduce from 8

# 4. Close other applications
# 5. Upgrade RAM if possible
```

---

### Issue: Poor model performance (low R2 score)

**Symptoms:**

```
R2 Score: 0.23
MSE: 456.78
```

**Cause:** Insufficient data, poor features, or hyperparameters

**Solution:**

```bash
# 1. Check data quality
python -c "
import pandas as pd
df = pd.read_csv('data.csv')
print(df.describe())
print(df.isnull().sum())
"

# 2. Increase training data
# Add more historical data

# 3. Tune hyperparameters
cd code
python models/tune_hyperparams.py --n-trials=100

# 4. Try different models
# Edit config/config.yaml
defaults:
  - model: lstm  # Try LSTM instead of xgboost

# 5. Add more features
# Check data/features/feature_engineering.py
```

---

## Docker Issues

### Issue: Docker daemon not running

**Symptoms:**

```
Cannot connect to the Docker daemon. Is the docker daemon running on this host?
```

**Solution:**

```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS
# Open Docker Desktop application

# Windows
# Start Docker Desktop

# Verify Docker is running
docker ps
```

---

### Issue: Docker build fails

**Symptoms:**

```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Solution:**

```bash
# 1. Clear Docker cache
docker system prune -a

# 2. Build without cache
docker-compose build --no-cache

# 3. Check Dockerfile syntax
# 4. Verify requirements.txt exists and is valid

# 5. Build specific service
docker-compose build api
```

---

### Issue: Container exits immediately

**Symptoms:**

```bash
docker-compose ps
# Shows container status as "Exit 1"
```

**Solution:**

```bash
# Check container logs
docker-compose logs api

# Common issues:
# 1. Missing environment variables
#    - Check .env file exists
#    - Verify DATABASE_URL is set

# 2. Port conflicts
#    - Change ports in docker-compose.yml

# 3. Command errors
#    - Verify CMD in Dockerfile is correct

# Run interactively to debug
docker-compose run api /bin/bash
```

---

## Kubernetes Issues

### Issue: Pods in CrashLoopBackOff

**Symptoms:**

```bash
kubectl get pods
# NAME                  READY   STATUS             RESTARTS
# fluxora-api-xxx       0/1     CrashLoopBackOff   5
```

**Solution:**

```bash
# 1. Check pod logs
kubectl logs fluxora-api-xxx

# 2. Describe pod for events
kubectl describe pod fluxora-api-xxx

# 3. Check for common issues:
#    - Missing secrets
kubectl get secrets

#    - Insufficient resources
kubectl describe node

#    - Image pull errors
kubectl describe pod fluxora-api-xxx | grep -A 5 Events

# 4. Verify ConfigMaps
kubectl get configmaps

# 5. Check environment variables
kubectl exec -it fluxora-api-xxx -- env
```

---

### Issue: Service not accessible

**Symptoms:**
Can't access service from outside cluster

**Solution:**

```bash
# 1. Check service exists
kubectl get services

# 2. Verify service type
kubectl describe service fluxora-api

# 3. For LoadBalancer, check external IP
kubectl get service fluxora-api

# 4. For NodePort, use node IP + NodePort
kubectl get nodes -o wide

# 5. Port forward for testing
kubectl port-forward service/fluxora-api 8000:8000

# 6. Check Ingress if used
kubectl get ingress
```

---

## Performance Issues

### Issue: Slow API response times

**Symptoms:**
Requests taking > 5 seconds

**Causes & Solutions:**

```bash
# 1. Check database query performance
# Add indexes
CREATE INDEX idx_timestamp ON energy_data(timestamp);
CREATE INDEX idx_user_id ON energy_data(user_id);

# 2. Enable caching
REDIS_ENABLED=true

# 3. Monitor with Prometheus
curl http://localhost:8000/metrics | grep request_duration

# 4. Profile API endpoints
# Use FastAPI profiling middleware

# 5. Increase workers
uvicorn main:app --workers 4

# 6. Check logs for slow operations
grep "duration" logs/fluxora.log | sort -n -k 5
```

---

### Issue: High memory usage

**Symptoms:**
System running out of RAM

**Solution:**

```bash
# 1. Check memory usage
docker stats  # For containers
top  # For processes

# 2. Limit container memory
# In docker-compose.yml
services:
  api:
    mem_limit: 512m

# 3. Optimize model loading
# Load model once, reuse
model = load_model()  # At startup, not per request

# 4. Use pagination
# Limit results per query
?limit=100&offset=0

# 5. Clear unused data
# Implement data retention policy
```

---

## Common Error Messages

### Error: "JWT token has expired"

**Solution:**

```bash
# Login again to get new token
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

---

### Error: "Circuit breaker is open"

**Solution:**

```bash
# Wait for recovery timeout (default 30 seconds)
# Or reset manually if available

# Check circuit breaker state
# In logs: grep "Circuit" logs/fluxora.log

# Identify underlying issue causing failures
```

---

### Error: "Validation error"

**Solution:**

```json
# Check request payload matches schema
{
  "detail": [
    {
      "loc": ["body", "consumption_kwh"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}

# Add missing fields or correct data types
```

---

### Error: "Database locked" (SQLite)

**Solution:**

```bash
# SQLite doesn't handle concurrent writes well
# Switch to PostgreSQL for production

# Or reduce concurrent requests
# Or implement retry logic
```

---

## Getting Additional Help

### Check Logs

```bash
# API logs
tail -f logs/fluxora.log

# Docker logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -f deployment/fluxora-api

# System logs (Linux)
journalctl -u fluxora -f
```

### Enable Debug Mode

```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Restart application
```

### Community Support

1. **Search existing issues:** [GitHub Issues](https://github.com/abrar2030/Fluxora/issues)
2. **Create new issue:** Use issue templates
3. **Provide details:**
   - Error message (full stack trace)
   - Steps to reproduce
   - Environment (OS, Python version, etc.)
   - Configuration (redact secrets)

---

## Diagnostic Commands

Run these to collect information for bug reports:

```bash
# System information
uname -a
python --version
docker --version
kubectl version

# Application status
curl http://localhost:8000/health
docker-compose ps
kubectl get pods

# Configuration check
cat code/.env | grep -v PASSWORD
grep -r "ERROR" logs/

# Network check
netstat -tuln | grep 8000
curl -v http://localhost:8000/health

# Resource usage
free -h
df -h
docker stats --no-stream
```

---
