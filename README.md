# Software-Defined Vehicle Training Platform

A modular and containerized Software-Defined Vehicle (SDV) training environment built with Eclipse KUKSA, Eclipse Velocitas, and the Eclipse Autowrx Runtime.
This project is part of the electrotics lab @ Hochschule Heilbronn for an hands-on platform for teaching and experimenting with modern SDV concepts.

---

## Project Overview

This project provides a complete Software-Defined Vehicle (SDV) training platform that bridges real automotive hardware with a modern, cloud-native SDV software stack. The system combines containerized services, a reduced VSS vehicle model, and CAN-based hardware modules to create a realistic environment for experimenting with SDV concepts.

The stack connects natively to digital.auto through the SDV Runtime, enabling direct deployment of Vehicle Apps to the demonstrator. At the same time, it provides full bidirectional communication with the real CAN hardware, allowing to interact with sensors, actuators, and vehicle functions in real time.

---

## Software Architecture Overview

<img width="1924" height="1414" alt="image" src="sonstige Dateien/Bilder/Software_Stack.svg" />

The system architecture combines cloud-based SDV tooling with real automotive hardware to form a complete end-to-end Software-Defined Vehicle environment. Development, deployment, and runtime execution are tightly integrated through the digital.auto ecosystem and the Eclipse SDV stack.

On the development side, Vehicle Apps are created in Python using the Velocitas framework. Applications are containerized and deployed directly from the digital.auto platform to the runtime environment. The Autowrx Runtime Cloud acts as the interface layer, handling deployment, OTA management, and communication with the target device via gRPC or MQTT.

On the runtime side, the HHN demonstrator operates as an Autowrx Runtime Target. It integrates the Eclipse Autowrx Runtime, which includes the App Manager and the local KUKSA Databroker. The Databroker exposes a standardized VSS data model, acting as the central data interface for all Vehicle Apps. Incoming CAN signals from the demonstrator’s ECUs flow through the KUKSA Provider (implemented using a dbc-feeder), which converts raw CAN frames into VSS signals and publishes them to the Databroker.

---

## Hardware Architecture Overview

The HHN SDV Demonstrator is built as a compact and modular hardware platform that exposes essential vehicle functions in a clear and accessible form. All components are mounted on a multi-layer acrylic baseplate, providing full visibility of wiring, ECUs, and signal paths.

<img width="3240" height="1804" alt="HHN-SDV-Demo-CAD v51" src="sonstige Dateien/Bilder/Aufbau.png" />

**Mechanical Structure**

- Multi-layer transparent acrylic baseplate

- Mounted standoffs for all ECUs and controllers

- 3D-printed display mount

- Cut-outs for Raspberry Pi access (SD card, USB, Ethernet)

- Integrated cable routing paths

The system follows a simplified zonal vehicle architecture: two separate CAN networks connect multiple function-specific ECUs to two Portenta H7 zone controllers. These controllers forward all CAN signals to the Raspberry-Pi-based runtime system, where the KUKSA Provider converts them into VSS signals for the SDV software stack.

Dual front-mounted displays provide real-time visualizations of dashboards, vehicle data, and running Vehicle Apps. Cut-outs in the baseplate offer direct access to the embedded Raspberry Pis for maintenance, updates, and debugging.
Overall, the hardware layout is optimized for education and experimentation, enabling students to interact directly with automotive signals and SDV runtime components.

---

## Hardware Components and wiring

<img width="922" height="777" alt="image" src="sonstige Dateien/Bilder/Schaltplan.png" />

**Core Computing & Runtime**

- Raspberry Pi (Primary runtime: Autowrx Runtime, KUKSA Databroker)

- Raspberry Pi (Secondary system: dashboard or visualization)

- 2× Arduino Portenta H7 (Zone controllers for front and rear CAN networks)

- 1x Dashboard display module

- 1x System and data visualization display 

**CAN Infrastructure**

- Two independent CAN buses (Front CAN + Rear CAN)

- CAN transceiver boards integrated on each ECU module

- CAN shield / CAN power interface for Raspberry Pi

- Twisted-pair CAN wiring harness for all modules

**Power & Connectivity**

- 230 V AC power supply

- DC power distribution module

- Stabilized 5 V / 12 V power rails for ECUs and controllers

---

## Quickstart

### Reading and Writing Signals with the KUKSA CLI

The fastest way to work with the SDV demonstrator and to read or write VSS signals is by using the KUKSA CLI. It serves as the central tool for direct interaction with the KUKSA Databroker.

After a system reboot, the KUKSA CLI is started automatically. This allows commands to be entered and signals to be read or written immediately after login without any additional preparation.

If the CLI does not open automatically in exceptional cases, it can be started at any time via the desktop application **KUKSA CLI**. A single click on the corresponding icon opens a terminal and automatically establishes a connection to the Databroker.

### KUKSA CLI can be started manually:

    docker run -it --name kuksa-cli --rm --network host \
    ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 127.0.0.1:55555

Once the connection to the KUKSA Databroker is established, VSS signals can be read and written.  

### How to read a signal:

    kuksa.val.v1 > get Vehicle.Speed
    [get]  OK
    Vehicle.Speed: NotAvailable

### How to subscribe to a signal:

    kuksa.val.v1 > subscribe Vehicle.Speed
    [subscribe]  OK
    Vehicle.Speed: NotAvailable
    
### Publish Sensor values:

    kuksa.val.v1 > publish Vehicle.Speed 100
    [publish]  OK
    kuksa.val.v1 > get Vehicle.Speed
    [get]  OK
    Vehicle.Speed: 100.00 km/h

### Actuator signals:

    kuksa.val.v1 > actuate Vehicle.Body.Lights.Beam.High.IsOn true
    [actuate]  OK

### To exit the KUKSA CLI:

    kuksa.val.v1 > quit
    Bye bye!


---

### Connection to digital.auto Playground

The deployment and execution of Vehicle Apps as well as the use of OTA functionality is performed via the web based user interface of the digital.auto Playground. It represents the central interface between the cloud environment and the Eclipse Autowrx Runtime running on the demonstrator.

The Playground is accessed via the following URL:

    https://playground.digital.auto

After logging in, navigate to Vehicle Catalog and then to Vehicle Models. The overview lists all available vehicle models, including both user defined and publicly available ones.

For the SDV demonstrator, the vehicle model HHN SDV Blueprint is selected. Next, open the Vehicle API tab, which provides the abstracted VSS interfaces of the vehicle. These interfaces form the basis for the development and execution of Vehicle Apps.

In the next step, switch to the Prototype Library tab and select the desired Vehicle App. Under SDV Code, the associated application code can be reviewed. To interact with the runtime, the integrated terminal is opened using the arrow icon at the bottom of the interface.

Within the terminal section, the active runtime running on the demonstrator can be selected under Runtime. This runtime was configured when starting the Docker container. In this project, it is named HHNSDV. If the runtime is not yet available, it can be added via Add Runtime by entering and confirming the name.

After successful selection, the runtime becomes available in the Playground. The selected Vehicle App can then be deployed and started directly on the demonstrator using the Play button.

This establishes the connection between the cloud environment and the local runtime and enables OTA based execution of Vehicle Apps. For a more detailed documentation including video guidance, please refer to the ILIAS course.

---

## Common Problems and Error Sources

### KUKSA CLI does not connect to the Databroker  
In most cases, the Databroker is not running or is listening on a different port. Verify that the corresponding Docker container is active:

    docker ps -a

Also ensure that the gRPC port is set correctly, typically 55555, and that both the CLI and Databroker are running in the same network context, for example using --network host.

### Signals can be read but not written  
This occurs when attempting to write to a signal defined as a sensor in the VSS model. Write access is only permitted for actuator signals. Additionally, verify that the signal is correctly defined as an actuator and loaded into the Databroker.

### Written values are immediately overwritten  
In this case, a feeder, simulation, or another application is typically writing cyclically to the same signal. This is common for sensor signals supplied via a DBC feeder or simulation.

### Values are visible in the CLI but do not reach CAN or UDP  
The cause is usually a missing or incorrect mapping. Verify the DBC file, the mapping between the CAN signal and the VSS path, and ensure that the feeder is started correctly. Also check whether the CAN interface, for example vcan0, is present and active.

### Docker containers do not start automatically after system reboot  
Either the --restart always option was not set when starting the container, or a systemd or autostart mechanism is missing.

### Asynchronous KUKSA SDK applications do not behave as expected  
This is typically due to a misunderstanding between one time reads and subscription logic. Asynchronous clients often only deliver values on change or require explicit loops. For simple tests, the synchronous variant is often more robust.

### Changes to VSS or mapping files have no effect  
After modifying the VSS model, mapping files, or DBC files, the Databroker and affected feeders usually need to be restarted. Without a restart, changes are not applied.

### Databroker cannot be reached  
Check whether required ports are occupied:

    ps aux | grep databroker
    grpcurl -plaintext localhost:55555 list
    journalctl -u kuksa-databroker

### Containers are missing or stopped  
If one or more containers are missing or parts of the demonstrator do not function as expected, follow a structured recovery procedure.

### Check all containers:

    docker ps -a

### If a container is stopped, restart it:

    docker start <container_name>

### If a container is in a faulty state, restart it:

    docker restart <container_name>

### If a container is missing entirely, recreate it using the following commands.

## SDV Runtime:

    docker run -d --name sdv-runtime --restart always --network host \
      -e RUNTIME_NAME="sdv-runtime" \
      -e KUKSA_DATABROKER_METADATA_FILE=/vss/hhn_sdv_vss.json \
      -v /home/hhn-sdv-demo/sdvDemonstrator/kuksa_databrocker:/vss \
      ghcr.io/eclipse-autowrx/sdv-runtime:latest

## Databroker (standalone, optional):

    docker run -d --name kuksa-server --restart always --network host \
      -v /home/hhn-sdv-demo/sdvDemonstrator/kuksa_databrocker:/vss \
      ghcr.io/eclipse-kuksa/kuksa-databroker:main --insecure \
      --vss /vss/hhn_sdv_vss.json

## KUKSA CLI:

    docker run -it --name kuksa-cli --rm --network host \
      ghcr.io/eclipse-kuksa/kuksa-databroker-cli:main --server 127.0.0.1:55555

## CAN Provider:

    docker compose up -d

## CAN-UDP Bridge:

    docker build -t can_udp_bridge ./

    docker run -d --name can_udp_bridge --restart always --network host can_udp_bridge

## Gear Sync App:

    docker build -t gear_sync_app ./

    docker run -d --name gear_sync_app --restart always --network host gear_sync_app

