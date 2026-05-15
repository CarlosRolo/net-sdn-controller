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

def install_flow(switch_id, flow_id, priority, match, actions):
    """Instala un flow rule en un switch via ODL REST API"""
    url = f"{BASE_URL}/opendaylight-inventory:nodes/node/{switch_id}/table/0/flow/{flow_id}"
    
    flow = {
        "flow": [{
            "id": str(flow_id),
            "priority": priority,
            "table_id": 0,
            "match": match,
            "instructions": {
                "instruction": [{
                    "order": 0,
                    "apply-actions": {
                        "action": actions
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
        print(f"[OK] Flow {flow_id} instalado en {switch_id}")
    else:
        print(f"[ERROR] {switch_id} flow {flow_id}: {response.status_code} - {response.text[:100]}")
    
    return response

def install_output_flow(switch_id, flow_id, priority, in_port, out_port):
    """Flow simple: entra por in_port, sale por out_port"""
    match = {"in-port": f"{switch_id}:{in_port}"}
    actions = [{"order": 0, "output-action": {"output-node-connector": str(out_port)}}]
    return install_flow(switch_id, flow_id, priority, match, actions)

def install_flood_flow(switch_id, flow_id=1, priority=1):
    """Flow default: flood a todos los puertos (tabla vacía)"""
    match = {}
    actions = [{"order": 0, "output-action": {"output-node-connector": "FLOOD"}}]
    return install_flow(switch_id, flow_id, priority, match, actions)

def install_all_flood_flows():
    """Instala flood flow en los 4 switches — resuelve el pingall"""
    print("\n=== Instalando flood flows en 4 switches ===")
    for i in range(1, 5):
        switch_id = f"openflow:{i}"
        install_flood_flow(switch_id, flow_id=100+i, priority=1)
    print("=== Listo ===\n")

def delete_flow(switch_id, flow_id):
    """Elimina un flow rule"""
    url = f"{BASE_URL}/opendaylight-inventory:nodes/node/{switch_id}/table/0/flow/{flow_id}"
    response = requests.delete(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        timeout=10
    )
    if response.status_code == 200:
        print(f"[OK] Flow {flow_id} eliminado de {switch_id}")
    else:
        print(f"[ERROR] {switch_id} flow {flow_id}: {response.status_code}")
    return response

def list_flows(switch_id):
    """Lista todos los flows de un switch"""
    url = f"http://{ODL_HOST}:{ODL_PORT}/restconf/operational/opendaylight-inventory:nodes/node/{switch_id}/table/0"
    response = requests.get(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        flows = data.get("flow-node-inventory:table", [{}])[0].get("flow", [])
        print(f"\n=== Flows en {switch_id} ({len(flows)} total) ===")
        for f in flows:
            print(f"  ID: {f.get('id')} | Priority: {f.get('priority')} | Match: {f.get('match', {})}")
    else:
        print(f"[ERROR] No se pudo obtener flows de {switch_id}: {response.status_code}")

if __name__ == "__main__":
    install_all_flood_flows()
    print("\n=== Flows instalados en todos los switches ===")
    for i in range(1, 5):
        list_flows(f"openflow:{i}")
