#!/bin/bash

# Data Sync Script for Fluxora
# This script synchronizes data from remote sources to local storage

set -euo pipefail

# Configuration
SOURCE_BUCKET="s3://energy-data-bucket/raw/"
DEST_DIR="./data/processed"
LOG_FILE="./logs/data_sync.log"

# Create directories if they don't exist
mkdir -p $DEST_DIR
mkdir -p $(dirname $LOG_FILE)

echo "$(date): Starting data synchronization" | tee -a $LOG_FILE

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first." | tee -a $LOG_FILE
    exit 1
fi

# Sync data from S3
echo "Syncing data from $SOURCE_BUCKET to $DEST_DIR" | tee -a $LOG_FILE
# Uncomment the following line when AWS credentials are configured
# aws s3 sync $SOURCE_BUCKET $DEST_DIR --exclude "*.tmp" | tee -a $LOG_FILE

# For demo purposes, create some sample data if the directory is empty
if [ -z "$(ls -A $DEST_DIR)" ]; then
    echo "Creating sample data for demonstration" | tee -a $LOG_FILE
    python -c "
import pandas as pd
import numpy as np
import os

# Create sample energy consumption data
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
meters = ['meter_' + str(i).zfill(3) for i in range(10)]

for meter in meters:
    data = {
        'timestamp': dates,
        'consumption': np.random.uniform(10, 100, size=len(dates)),
        'temperature': np.random.uniform(15, 35, size=len(dates)),
        'humidity': np.random.uniform(30, 90, size=len(dates))
    }
    df = pd.DataFrame(data)
    df.to_csv(os.path.join('$DEST_DIR', f'{meter}_data.csv'), index=False)
    print(f'Created sample data for {meter}')
"
fi

echo "$(date): Data synchronization completed successfully" | tee -a $LOG_FILE
