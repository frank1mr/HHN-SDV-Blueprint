import time

from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import DataEntry
from kuksa_client.grpc import DataType
from kuksa_client.grpc import EntryUpdate
from kuksa_client.grpc import Field
from kuksa_client.grpc import Metadata
from kuksa_client.grpc import VSSClient


Sensor_CG = "Vehicle.Powertrain.Transmission.CurrentGear"
Actuator_SG = "Vehicle.Powertrain.Transmission.SelectedGear"

def read_Current_Gear():
    CurrentGear = client.get_current_values([Sensor_CG])
    current_gear_value = CurrentGear[Sensor_CG].value

    # Falls noch kein Wert verfügbar ist
    if current_gear_value is None:
        return None

    return current_gear_value

def read_Selected_Gear():
    SelectedGear = client.get_current_values([Actuator_SG])
    selected_gear_value = SelectedGear[Actuator_SG].value

    # Falls noch kein Wert verfügbar ist
    if selected_gear_value is None:
        return None

    return selected_gear_value

# Aufbau der Verbindung zum KUKSA Databroker
with VSSClient("127.0.0.1", 55555) as client:
    while True:

        # Aktuellen Ist- und Soll-Gang lesen
        CG = read_Current_Gear()
        SG = read_Selected_Gear()

        # Abbruch der Iteration, falls kein Istwert vorhanden ist
        if CG is None:
            time.sleep(0.5)
            continue

        # Schreiben des Ist-Gangs auf das Aktor-Signal SelectedGear
        updates = (
            EntryUpdate(
                DataEntry(
                    Actuator_SG,
                    value=Datapoint(value=CG),
                    metadata=Metadata(data_type=DataType.INT8)
                ),
                (Field.VALUE,)
            ),
        )

        # Übertragen des Updates an den Databroker
        client.set(updates=updates)

        # Zykluszeit der Anwendung
        time.sleep(2)
