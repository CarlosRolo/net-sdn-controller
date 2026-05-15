import requests
import json

ODL_HOST = "127.0.0.1"
ODL_PORT = 8181
ODL_USER = "admin"
ODL_PASS = "admin"
BASE_URL = f"http://{ODL_HOST}:{ODL_PORT}/restconf/config"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def install_qos_flow(switch_id, flow_id, priority, src_ip, dst_ip, queue_id):
    """Instala flow con QoS — marca tráfico hacia una cola específica"""
    url = f"{BASE_URL}/opendaylight-inventory:nodes/node/{switch_id}/table/0/flow/{flow_id}"

    flow = {
        "flow": [{
            "id": str(flow_id),
            "priority": priority,
            "table_id": 0,
            "match": {
                "ethernet-match": {
                    "ethernet-type": {"type": 2048}
                },
                "ipv4-source": src_ip,
                "ipv4-destination": dst_ip
            },
            "instructions": {
                "instruction": [{
                    "order": 0,
                    "apply-actions": {
                        "action": [{
                            "order": 0,
                            "set-queue-action": {
                                "queue-id": queue_id
                            }
                        }, {
                            "order": 1,
                            "output-action": {
                                "output-node-connector": "NORMAL"
                            }
                        }]
                    }
                }]
            }
        }]
    }

    response = requests.put(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        data=json.dumps(flow),
        timeout=10
    )

    if response.status_code in [200, 201]:
        print(f"[OK] QoS flow {flow_id} instalado en {switch_id} — {src_ip} -> {dst_ip} cola {queue_id}")
    else:
        print(f"[ERROR] {switch_id} flow {flow_id}: {response.status_code}")

    return response

def install_priority_flow(switch_id, flow_id, priority, src_ip, dst_ip):
    """Flow de alta prioridad — reenvio directo sin cola (para VOIP/crítico)"""
    url = f"{BASE_URL}/opendaylight-inventory:nodes/node/{switch_id}/table/0/flow/{flow_id}"

    flow = {
        "flow": [{
            "id": str(flow_id),
            "priority": priority,
            "table_id": 0,
            "match": {
                "ethernet-match": {
                    "ethernet-type": {"type": 2048}
                },
                "ipv4-source": src_ip,
                "ipv4-destination": dst_ip
            },
            "instructions": {
                "instruction": [{
                    "order": 0,
                    "apply-actions": {
                        "action": [{
                            "order": 0,
                            "output-action": {
                                "output-node-connector": "NORMAL"
                            }
                        }]
                    }
                }]
            }
        }]
    }

    response = requests.put(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        data=json.dumps(flow),
        timeout=10
    )

    if response.status_code in [200, 201]:
        print(f"[OK] Priority flow {flow_id} instalado en {switch_id} — {src_ip} -> {dst_ip} ALTA PRIORIDAD")
    else:
        print(f"[ERROR] {switch_id} flow {flow_id}: {response.status_code}")

    return response

def apply_isp_qos_policies():
    """
    Políticas QoS para topología ISP:
    - Zona 1 (h1-h5)   clientes residenciales — prioridad normal
    - Zona 2 (h6-h10)  clientes empresariales — prioridad alta
    - Zona 3 (h11-h15) servidores             — prioridad crítica
    - Zona 4 (h16-h20) gestión                — prioridad máxima
    """
    print("\n=== Aplicando políticas QoS ISP ===\n")

    # Tráfico desde servidores (zona 3) hacia clientes — prioridad crítica
    for switch_id in ["openflow:1", "openflow:2", "openflow:3", "openflow:4"]:
        for i in range(11, 16):
            flow_id = f"qos-server-{switch_id[-1]}-{i}"
            install_priority_flow(
                switch_id=switch_id,
                flow_id=flow_id,
                priority=200,
                src_ip=f"10.0.0.{i}/32",
                dst_ip="10.0.0.0/24"
            )

    # Tráfico desde zona empresarial (h6-h10) — prioridad alta
    for switch_id in ["openflow:1", "openflow:2", "openflow:3", "openflow:4"]:
        for i in range(6, 11):
            flow_id = f"qos-enterprise-{switch_id[-1]}-{i}"
            install_priority_flow(
                switch_id=switch_id,
                flow_id=flow_id,
                priority=150,
                src_ip=f"10.0.0.{i}/32",
                dst_ip="10.0.0.0/24"
            )

    print("\n=== Políticas QoS aplicadas ===")
    print("  Servidores  (h11-h15) → prioridad 200 (crítica)")
    print("  Empresarial (h6-h10)  → prioridad 150 (alta)")
    print("  Residencial (h1-h5)   → prioridad default")
    print("  Gestión     (h16-h20) → prioridad default\n")

if __name__ == "__main__":
    apply_isp_qos_policies()
