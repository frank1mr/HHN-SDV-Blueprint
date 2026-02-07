import asyncio
import random
import time

from kuksa_client.grpc.aio import VSSClient
from kuksa_client.grpc import Datapoint, DataEntry, EntryUpdate, Field

SPEED_PATH = "Vehicle.Speed"

async def read_speed_sim(speed_kmh: float, dt: float) -> float:
    # Zielgeschwindigkeit wechselt alle paar Sekunden
    if random.random() < 0.05:  # ca. alle ~2 s bei dt=0.1
        target_kmh = random.choice([0, 30, 50, 80, 100, 120, 130])
    else:
        target_kmh = None

    # Falls kein neues Ziel gezogen wurde, bleib beim aktuellen "Trend"
    if target_kmh is None:
        target_kmh = read_speed_sim.target_kmh

    read_speed_sim.target_kmh = target_kmh

    # einfache Annäherung mit begrenzter Änderung pro Schritt
    max_step_kmh = 3.0  # entspricht ca. 3 km/h pro 100 ms (sehr grob)
    diff = target_kmh - speed_kmh
    step = max(-max_step_kmh, min(max_step_kmh, diff))
    speed_kmh += step

    # kleines Messrauschen
    speed_kmh = max(0.0, speed_kmh + random.uniform(-0.5, 0.5))
    return speed_kmh


read_speed_sim.target_kmh = 0.0


async def main():
    dt = 0.1
    speed_kmh = 0.0

    async with VSSClient("127.0.0.1", 55555) as client:
        while True:
            t0 = time.monotonic()

            speed_kmh = await read_speed_sim(speed_kmh, dt)

            updates = (
                EntryUpdate(
                    DataEntry(
                        SPEED_PATH,
                        value=Datapoint(value=float(speed_kmh)),
                    ),
                    (Field.VALUE,),
                ),
            )
            await client.set(updates=updates)

            # auf ca. dt takten
            await asyncio.sleep(max(0.0, dt - (time.monotonic() - t0)))

asyncio.run(main())
