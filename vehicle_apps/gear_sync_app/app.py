import asyncio
import signal

# Async gRPC client from the KUKSA Python SDK
from kuksa_client.grpc.aio import VSSClient
# Datapoint wraps a value together with metadata for GET / SET operations
from kuksa_client.grpc import Datapoint

# VSS signal paths
CURRENT_GEAR_PATH = "Vehicle.Powertrain.Transmission.CurrentGear"
SELECTED_GEAR_PATH = "Vehicle.Powertrain.Transmission.SelectedGear"


async def gear_sync(client: VSSClient) -> None:
    """
    Synchronizes SelectedGear with CurrentGear

    Workflow:
    - Subscribe to CurrentGear
    - React to every update
    - Read the current value of SelectedGear
    - Update SelectedGear if the values differ
    """

    # Endless async loop
    # Yields whenever CurrentGear changes in the Databroker
    async for updates in client.subscribe_current_values([CURRENT_GEAR_PATH]):

        # Extract the Datapoint for CurrentGear from the update map
        dp = updates.get(CURRENT_GEAR_PATH)

        # Guard against invalid updates
        # dp may be None or dp.value may be None
        if dp is None or dp.value is None:
            continue

        # Current gear value reported by the vehicle
        current_gear = dp.value
        print(f"Current gear received: {current_gear}")

        # Explicitly read the current SelectedGear from the Databroker
        # get_current_values returns a mapping: {VSS path -> Datapoint}
        selected_map = await client.get_current_values([SELECTED_GEAR_PATH])

        # Extract the Datapoint for SelectedGear
        selected_dp = selected_map.get(SELECTED_GEAR_PATH)

        # If SelectedGear has never been set, its value may be None
        selected_gear = None if selected_dp is None else selected_dp.value

        # Only update if the values are different
        # This prevents feedback loops and unnecessary SET operations
        if current_gear != selected_gear:

            # Write SelectedGear as a target value
            # Target values are typically consumed by actuators
            await client.set_target_values(
                {SELECTED_GEAR_PATH: Datapoint(value=current_gear)}
            )

            print(f"Updated selected gear to: {current_gear}")


async def main() -> None:
    """
    Application entry point

    - Connects to the Databroker
    - Starts the gear synchronization task
    - Shuts down cleanly on SIGINT / SIGTERM
    """

    # Variant B: Script runs inside Docker Compose
    # Databroker service is reachable via its service name
    host = "127.0.0.1"
    port = 55555

    # Event used to trigger a clean shutdown
    stop_event = asyncio.Event()

    # Get the current asyncio event loop
    loop = asyncio.get_running_loop()

    # Register signal handlers for graceful shutdown
    # Allows clean exit on Ctrl+C or docker stop
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            # Fallback for platforms with limited signal support
            pass

    # Open an asynchronous connection to the Databroker
    async with VSSClient(host, port) as client:

        # Start the gear synchronization as a background task
        task = asyncio.create_task(gear_sync(client))

        # Block until a shutdown signal is received
        await stop_event.wait()

        # Cancel the background task
        task.cancel()

        # Wait for the task to exit cleanly
        try:
            await task
        except asyncio.CancelledError:
            pass


# Script entry point
if __name__ == "__main__":
    asyncio.run(main())
