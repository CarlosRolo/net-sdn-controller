# SDN vs Traditional Networks — Technical Comparison

## Overview

This document compares Software-Defined Networking (SDN) with traditional network architectures, based on hands-on experience building NET-06.

## Architecture Comparison

| Aspect | Traditional | SDN |
|---|---|---|
| Control logic | Distributed per device | Centralized controller |
| Data plane | Coupled with control | Decoupled, dumb forwarding |
| Configuration | CLI on each device | REST API / code |
| Policy changes | Manual per device | Single API call |
| Visibility | SNMP polling | Real-time OpenFlow stats |
| Programmability | Limited (vendor CLI) | Full (Python, REST, YANG) |
| Fault tolerance | Per-device protocols | Controller-managed |
| Scalability | Complex, manual | Programmatic, automated |

## Control Plane

### Traditional

Every router and switch runs its own control plane — OSPF, BGP, STP. Each device independently computes forwarding decisions. Changing a routing policy requires touching every device individually.

### SDN (OpenDaylight)

A single controller holds the global network view. Switches become simple forwarding devices that receive instructions via OpenFlow. A single Python script can reprogram the entire network in seconds.

## Flow Management

### Traditional

Must be repeated on every device. No central audit trail.

    Router(config)# ip route 10.0.2.0 255.255.255.0 10.0.1.1
    Router(config)# ip access-list extended VOIP_PRIORITY
    Router(config-ext-nacl)# permit udp any any range 5060 5061

### SDN (Python + REST API)

One function call installs the policy on any switch in the topology.

    install_priority_flow(
        switch_id="openflow:1",
        flow_id="qos-voip-001",
        priority=200,
        src_ip="10.0.0.11/32",
        dst_ip="10.0.0.0/24"
    )

## QoS Implementation

### Traditional

- Configure queues on each interface manually
- Use DSCP marking per device
- No global view of traffic priorities

### SDN (this project)

- 40 QoS flow rules deployed in seconds via REST API
- Priority tiers: Critical (200) > Enterprise (150) > Residential (default)
- Centrally managed, auditable, version-controlled

## Observability

### Traditional

- SNMP polling every 5 minutes
- No per-flow visibility
- Vendor-specific tools required

### SDN (OpenDaylight + Grafana)

- Real-time per-flow statistics (packet count, byte count, duration)
- 78 flows monitored simultaneously
- Open standards, no vendor lock-in

## When to Use SDN

SDN is the right choice when:

- The network has 10+ devices requiring coordinated policy changes
- Traffic engineering and QoS are critical (ISPs, data centers)
- Automation and programmability are required (DevOps/NetOps)
- Real-time visibility and fast response to network events is needed

Traditional networking remains valid for:

- Small office networks (less than 10 devices)
- Environments with existing vendor investments
- Scenarios where controller availability is a concern

## Real-World SDN Deployments

| Organization | SDN Use Case |
|---|---|
| Google | B4 WAN — OpenFlow-based backbone |
| AWS | VPC networking — SDN-based virtual networks |
| CNT Ecuador | Metro Ethernet SDN migration |
| Facebook | FBOSS — custom SDN for data centers |

## Conclusion

This project demonstrates that SDN fundamentally changes how networks are operated — from manual, device-by-device configuration to programmatic, API-driven infrastructure management. The combination of Mininet + OpenDaylight + Python + Grafana represents a complete NetOps stack applicable to real ISP and data center environments.
