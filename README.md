# NET-06: SDN Controller with Mininet + OpenDaylight

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![OpenDaylight](https://img.shields.io/badge/OpenDaylight-Oxygen-red)
![Mininet](https://img.shields.io/badge/Mininet-2.3.0-green)
![Grafana](https://img.shields.io/badge/Grafana-13.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A production-grade SDN controller project simulating ISP infrastructure with Mininet (20-node virtual topology), OpenDaylight as the SDN controller, QoS policy management via REST API, and real-time OpenFlow flow visualization in Grafana.

## Architecture

```
+---------------------------------------------+
|           Data Plane (Mininet)               |
|  h1-h5      h6-h10     h11-h15    h16-h20   |
|  Zone 1     Zone 2     Zone 3     Zone 4    |
|  [s1]-------[s2]-------[s3]-------[s4]      |
|   +---------------------------+              |
+------------------+---------------------------+
                   | OpenFlow 1.3
+------------------v---------------------------+
|        Control Plane (OpenDaylight)          |
|         Karaf + RESTCONF + L2Switch          |
+------------------+---------------------------+
                   | REST API
+------------------v---------------------------+
|        Management Plane (Python)             |
|   flow_manager.py   qos_policies.py          |
|   metrics_exporter.py  metrics_server.py     |
+------------------+---------------------------+
                   | JSON/HTTP
+------------------v---------------------------+
|        Visualization (Grafana)               |
|   Real-time OpenFlow flow dashboard          |
+---------------------------------------------+
```

## Features

- **20-node ISP topology** with 4 OpenFlow switches and 4 zones
- **OpenDaylight SDN controller** managing all flow tables via OpenFlow 1.3
- **QoS policies** applied programmatically via RESTCONF REST API
- **Real-time metrics** collected from ODL and visualized in Grafana
- **Flow management** — install, delete, and list flows with Python

## Tech Stack

| Component | Technology |
|---|---|
| Network emulation | Mininet 2.3.0 |
| SDN Controller | OpenDaylight Oxygen |
| Southbound protocol | OpenFlow 1.3 |
| Northbound API | RESTCONF / YANG |
| Flow management | Python 3 + requests |
| Metrics collection | Custom HTTP server |
| Visualization | Grafana 13 + Infinity datasource |
| OS | Ubuntu 20.04 LTS |

## Project Structure

```
net-sdn-controller/
├── topology/
│   └── topo_isp.py          # 20-node ISP topology (4 switches, 4 zones)
├── controller/
│   ├── flows/
│   │   └── flow_manager.py  # Install/delete/list flows via ODL REST API
│   └── qos/
│       └── qos_policies.py  # QoS priority policies per ISP zone
├── metrics/
│   ├── metrics_exporter.py  # Collect flow stats from ODL
│   └── metrics_server.py    # HTTP server exposing metrics for Grafana
├── dashboard/
│   └── grafana_dashboard.json
├── tests/
│   └── test_flows.py
└── docs/
```

## Quick Start

### Requirements

- Ubuntu 20.04 LTS (VM or native)
- Java 8 (openjdk-8-jdk)
- Python 3 + pip
- Mininet 2.3.0

### 1. Install dependencies

```bash
sudo apt update && sudo apt install -y mininet openvswitch-switch python3-pip openjdk-8-jdk
pip3 install requests
```

### 2. Start OpenDaylight

```bash
cd karaf-0.8.4/bin && ./karaf
```

Inside Karaf shell:

```
feature:install odl-restconf-all odl-l2switch-switch odl-l2switch-switch-ui odl-openflowplugin-flow-services-rest odl-mdsal-all
```

### 3. Launch the topology

```bash
sudo python3 topology/topo_isp.py
```

### 4. Apply QoS policies

```bash
python3 controller/qos/qos_policies.py
```

### 5. Start metrics server

```bash
python3 metrics/metrics_server.py &
```

### 6. Open Grafana

Navigate to `http://localhost:3000` and import the dashboard.

## Results

- 20 hosts with **0% packet loss** across 4 OpenFlow switches
- **40 QoS flow rules** installed programmatically via REST API
- **78 active flows** monitored in real-time via Grafana
- Full SDN separation of data plane and control plane demonstrated

## SDN vs Traditional Networks

| Aspect | Traditional | SDN |
|---|---|---|
| Control logic | Distributed (each device) | Centralized (controller) |
| Configuration | CLI per device | REST API / code |
| Policy changes | Manual on each device | Single API call |
| Visibility | SNMP polling | Real-time flow stats |
| Programmability | Limited | Full (Python, REST) |

## Author
 
**Carlos David Rodriguez Lopez**  
Telematic Engineer — ESPOCH  
Riobamba, Chimborazo, Ecuador  
GitHub: [github.com/CarlosRolo](https://github.com/CarlosRolo)  
LinkedIn: [linkedin.com/in/carlosdrodriguezl](https://linkedin.com/in/carlosdrodriguezl)
 
---
 
## License
 
MIT License — see [LICENSE](LICENSE)
