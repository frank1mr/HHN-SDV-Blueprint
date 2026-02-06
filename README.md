# Software-Defined Vehicle Training Platform

A modular and containerized Software-Defined Vehicle (SDV) training environment built with Eclipse KUKSA, Eclipse Velocitas, and the Eclipse Autowrx Runtime.
This project is part of the electrotics lab @ Hochschule Heilbronn for an hands-on platform for teaching and experimenting with modern SDV concepts.

## Project Overview

This project provides a complete Software-Defined Vehicle (SDV) training platform that bridges real automotive hardware with a modern, cloud-native SDV software stack. The system combines containerized services, a reduced VSS vehicle model, and CAN-based hardware modules to create a realistic environment for experimenting with SDV concepts.

The stack connects natively to digital.auto through the SDV Runtime, enabling direct deployment of Vehicle Apps to the demonstrator. At the same time, it provides full bidirectional communication with the real CAN hardware, allowing to interact with sensors, actuators, and vehicle functions in real time.

## Software Architecture Overview

<img width="1924" height="1414" alt="image" src="sonstige Dateien/Bilder/Architektur.png" />

The system architecture combines cloud-based SDV tooling with real automotive hardware to form a complete end-to-end Software-Defined Vehicle environment. Development, deployment, and runtime execution are tightly integrated through the digital.auto ecosystem and the Eclipse SDV stack.

On the development side, Vehicle Apps are created in Python using the Velocitas framework. Applications are containerized and deployed directly from the digital.auto platform to the runtime environment. The Autowrx Runtime Cloud acts as the interface layer, handling deployment, OTA management, and communication with the target device via gRPC or MQTT.

On the runtime side, the HHN demonstrator operates as an Autowrx Runtime Target. It integrates the Eclipse Autowrx Runtime, which includes the App Manager and the local KUKSA Databroker. The Databroker exposes a standardized VSS data model, acting as the central data interface for all Vehicle Apps. Incoming CAN signals from the demonstrator’s ECUs flow through the KUKSA Provider (implemented using a dbc-feeder), which converts raw CAN frames into VSS signals and publishes them to the Databroker.

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
