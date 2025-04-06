from feast import FeatureStore, FeatureView, Entity, Field
from feast.types import Float32, Int64, UnixTimestamp

energy_entity = Entity(name="meter_id", description="Smart meter ID")

hourly_features = FeatureView(
    name="hourly_energy_features",
    entities=[energy_entity],
    schema=[
        Field(name="lag_24h", dtype=Float32),
        Field(name="rolling_7d_mean", dtype=Float32),
        Field(name="temperature", dtype=Float32)
    ],
    source=BigQuerySource(
        table_ref="your-project.dataset.hourly_features"
    ),
    ttl=timedelta(days=365)