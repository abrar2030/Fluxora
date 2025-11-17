import json

import websockets
from fluxora.data.make_dataset import process_real_time_data


async def stream_energy_data():
    async with websockets.connect("wss://realtime-energy.com/ws") as ws:
        while True:
            message = await ws.recv()
            data = json.loads(message)

            # Validate and process
            validated = validate_raw_data(pd.DataFrame([data]))
            processed = process_real_time_data(validated)

            # Write to feature store
            write_to_feature_store(processed)
