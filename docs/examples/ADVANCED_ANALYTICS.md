# Advanced Analytics Example

Learn how to perform advanced analytics on energy consumption data using Fluxora's analytics API.

---

## Overview

This example demonstrates:

- Retrieving analytics data for different time periods
- Calculating efficiency metrics
- Identifying consumption patterns
- Generating reports and visualizations

---

## Prerequisites

```bash
pip install requests pandas matplotlib seaborn
```

---

## Complete Analytics Script

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Configuration
API_BASE = "http://localhost:8000"
TOKEN = "your_access_token_here"  # From login

headers = {"Authorization": f"Bearer {TOKEN}"}

# Fetch analytics data for different periods
def get_analytics(period='month'):
    """
    Get analytics data from API.

    Args:
        period: 'week', 'month', or 'year'
    """
    response = requests.get(
        f"{API_BASE}/v1/analytics/",
        headers=headers,
        params={"period": period}
    )
    return response.json()

# Get monthly analytics
monthly_data = get_analytics('month')
df_monthly = pd.DataFrame(monthly_data)

print(f"Received {len(df_monthly)} data points")
print(df_monthly.head())

# Calculate key metrics
total_consumption = df_monthly['consumption'].sum()
total_cost = df_monthly['cost'].sum()
avg_efficiency = df_monthly['efficiency'].mean()
avg_temperature = df_monthly['temperature'].mean()

print("\n=== Monthly Summary ===")
print(f"Total Consumption: {total_consumption:.2f} kWh")
print(f"Total Cost: ${total_cost:.2f}")
print(f"Average Efficiency: {avg_efficiency:.2f}%")
print(f"Average Temperature: {avg_temperature:.2f}°C")

# Identify peak consumption days
top_days = df_monthly.nlargest(5, 'consumption')
print("\n=== Top 5 Consumption Days ===")
for _, row in top_days.iterrows():
    print(f"{row['label']}: {row['consumption']:.2f} kWh (${row['cost']:.2f})")

# Visualization 1: Consumption and Cost Trend
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(df_monthly['label'], df_monthly['consumption'], marker='o', color='steelblue')
plt.title('Energy Consumption Trend')
plt.ylabel('Consumption (kWh)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(df_monthly['label'], df_monthly['cost'], marker='o', color='green')
plt.title('Cost Trend')
plt.ylabel('Cost (USD)')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('consumption_trend.png', dpi=300, bbox_inches='tight')
print("\nSaved: consumption_trend.png")

# Visualization 2: Efficiency vs Temperature
plt.figure(figsize=(10, 6))
plt.scatter(df_monthly['temperature'], df_monthly['efficiency'],
            s=100, alpha=0.6, c='coral')
plt.xlabel('Temperature (°C)')
plt.ylabel('Efficiency (%)')
plt.title('Efficiency vs Temperature Correlation')
plt.grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(df_monthly['temperature'].dropna(),
               df_monthly['efficiency'][df_monthly['temperature'].notna()], 1)
p = np.poly1d(z)
plt.plot(df_monthly['temperature'].sort_values(),
         p(df_monthly['temperature'].sort_values()),
         "r--", alpha=0.8, label='Trend')
plt.legend()

plt.savefig('efficiency_correlation.png', dpi=300, bbox_inches='tight')
print("Saved: efficiency_correlation.png")

# Weekly comparison
weekly_data = get_analytics('week')
df_weekly = pd.DataFrame(weekly_data)

print("\n=== Weekly Analysis ===")
print(f"Week Total: {df_weekly['consumption'].sum():.2f} kWh")
print(f"Week Average: {df_weekly['consumption'].mean():.2f} kWh/day")
print(f"Week Peak: {df_weekly['consumption'].max():.2f} kWh")

# Cost analysis
cost_per_kwh = df_monthly['cost'].sum() / df_monthly['consumption'].sum()
print(f"\n=== Cost Analysis ===")
print(f"Average Cost per kWh: ${cost_per_kwh:.4f}")
print(f"Projected Annual Cost: ${total_cost * 12:.2f}")

# Generate report
report = f"""
FLUXORA ENERGY ANALYTICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== CONSUMPTION SUMMARY ===
Period: Last 30 days
Total Consumption: {total_consumption:.2f} kWh
Average Daily: {total_consumption / len(df_monthly):.2f} kWh
Peak Day: {df_monthly.nlargest(1, 'consumption')['label'].values[0]}
Peak Consumption: {df_monthly['consumption'].max():.2f} kWh

=== COST ANALYSIS ===
Total Cost: ${total_cost:.2f}
Average Cost/Day: ${total_cost / len(df_monthly):.2f}
Cost per kWh: ${cost_per_kwh:.4f}
Projected Annual: ${total_cost * 12:.2f}

=== EFFICIENCY METRICS ===
Average Efficiency: {avg_efficiency:.2f}%
Best Efficiency: {df_monthly['efficiency'].max():.2f}%
Worst Efficiency: {df_monthly['efficiency'].min():.2f}%

=== ENVIRONMENTAL FACTORS ===
Average Temperature: {avg_temperature:.2f}°C
Temperature Range: {df_monthly['temperature'].min():.1f}°C - {df_monthly['temperature'].max():.1f}°C

=== RECOMMENDATIONS ===
1. Peak consumption occurs around {df_monthly.nlargest(1, 'consumption')['label'].values[0]}
2. Consider load shifting to off-peak hours
3. Efficiency correlates with temperature - optimize HVAC usage
4. Potential annual savings: ${(total_cost * 0.15) * 12:.2f} (15% reduction target)
"""

with open('energy_report.txt', 'w') as f:
    f.write(report)

print("\n" + report)
print("\nReport saved to: energy_report.txt")
```

**Expected Output:**

```
Received 30 data points
   label  consumption    cost  temperature  efficiency
0  2025-12-01      1205.3  120.53         21.5        78.2
...

=== Monthly Summary ===
Total Consumption: 35678.90 kWh
Total Cost: $3567.89
Average Efficiency: 76.45%
Average Temperature: 22.31°C

=== Top 5 Consumption Days ===
2025-12-15: 1345.67 kWh ($134.57)
2025-12-22: 1298.45 kWh ($129.85)
...

Saved: consumption_trend.png
Saved: efficiency_correlation.png

[Full report output]
```

---

## Advanced Analysis: Anomaly Detection

```python
import numpy as np
from scipy import stats

# Detect anomalies using Z-score method
df_monthly['z_score'] = np.abs(stats.zscore(df_monthly['consumption']))
anomalies = df_monthly[df_monthly['z_score'] > 2]

print(f"\n=== Anomaly Detection ===")
print(f"Detected {len(anomalies)} anomalous days:")
for _, row in anomalies.iterrows():
    print(f"{row['label']}: {row['consumption']:.2f} kWh (Z-score: {row['z_score']:.2f})")

# Visualize anomalies
plt.figure(figsize=(12, 6))
plt.plot(df_monthly['label'], df_monthly['consumption'], 'b-', label='Normal')
plt.scatter(anomalies['label'], anomalies['consumption'],
            color='red', s=100, label='Anomaly', zorder=5)
plt.xlabel('Date')
plt.ylabel('Consumption (kWh)')
plt.title('Consumption with Anomaly Detection')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('anomaly_detection.png', dpi=300, bbox_inches='tight')
print("Saved: anomaly_detection.png")
```

---

## Next Steps

- **[Custom Model Training](CUSTOM_TRAINING.md)** - Train models on your data
- **[Basic Prediction Example](BASIC_PREDICTION.md)** - Get started with predictions
- **[API Reference](../API.md)** - Complete API documentation

---

**Questions?** Check the [Troubleshooting Guide](../TROUBLESHOOTING.md).
