# -*- coding: utf-8 -*-
import requests
import json
import time
from datetime import datetime

ODL_HOST = "127.0.0.1"
ODL_PORT = 8181
ODL_USER = "admin"
ODL_PASS = "admin"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_flow_stats(switch_id):
    """Obtiene estadisticas de flows de un switch via ODL REST API"""
    url = f"http://{ODL_HOST}:{ODL_PORT}/restconf/operational/opendaylight-inventory:nodes/node/{switch_id}/table/0"
    
    response = requests.get(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"[ERROR] No se pudo obtener stats de {switch_id}: {response.status_code}")
        return []
    
    data = response.json()
    flows = data.get("flow-node-inventory:table", [{}])[0].get("flow", [])
    return flows

def get_node_stats(switch_id):
    """Obtiene estadisticas del nodo (puertos) de un switch"""
    url = f"http://{ODL_HOST}:{ODL_PORT}/restconf/operational/opendaylight-inventory:nodes/node/{switch_id}"
    
    response = requests.get(
        url,
        headers=HEADERS,
        auth=(ODL_USER, ODL_PASS),
        timeout=10
    )
    
    if response.status_code != 200:
        return {}
    
    return response.json()

def parse_flow_metrics(switch_id, flows):
    """Parsea flows y extrae metricas relevantes"""
    metrics = []
    
    for flow in flows:
        stats = flow.get("opendaylight-flow-statistics:flow-statistics", {})
        packets = stats.get("packet-count", 0)
        bytes_count = stats.get("byte-count", 0)
        duration = stats.get("duration", {})
        duration_sec = duration.get("second", 0)
        
        metric = {
            "switch": switch_id,
            "flow_id": flow.get("id", "unknown"),
            "priority": flow.get("priority", 0),
            "packets": int(packets),
            "bytes": int(bytes_count),
            "duration_sec": int(duration_sec),
            "match": flow.get("match", {})
        }
        metrics.append(metric)
    
    return metrics

def print_metrics_table(all_metrics):
    """Imprime tabla de metricas en consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*70}")
    print(f"  METRICAS DE FLUJOS SDN - {timestamp}")
    print(f"{'='*70}")
    print(f"{'Switch':<15} {'Flow ID':<25} {'Prio':<6} {'Paquetes':<12} {'Bytes':<12} {'Seg':<8}")
    print(f"{'-'*70}")
    
    total_packets = 0
    total_bytes = 0
    
    for m in all_metrics:
        flow_id = str(m['flow_id'])[:24]
        print(f"{m['switch']:<15} {flow_id:<25} {m['priority']:<6} {m['packets']:<12} {m['bytes']:<12} {m['duration_sec']:<8}")
        total_packets += m['packets']
        total_bytes += m['bytes']
    
    print(f"{'-'*70}")
    print(f"{'TOTAL':<15} {'':<25} {'':<6} {total_packets:<12} {total_bytes:<12}")
    print(f"{'='*70}\n")

def export_to_json(all_metrics, filename="metrics/flow_metrics.json"):
    """Exporta metricas a JSON para consumo externo"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_flows": len(all_metrics),
        "total_packets": sum(m['packets'] for m in all_metrics),
        "total_bytes": sum(m['bytes'] for m in all_metrics),
        "flows": all_metrics
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"[OK] Metricas exportadas a {filename}")
    return data

def collect_all_metrics():
    """Recopila metricas de todos los switches"""
    all_metrics = []
    
    for i in range(1, 5):
        switch_id = f"openflow:{i}"
        flows = get_flow_stats(switch_id)
        metrics = parse_flow_metrics(switch_id, flows)
        all_metrics.extend(metrics)
        print(f"[OK] {switch_id}: {len(flows)} flows recopilados")
    
    return all_metrics

def monitor_loop(interval=10, iterations=3):
    """Loop de monitoreo continuo"""
    print(f"\n[INFO] Iniciando monitoreo - intervalo {interval}s - {iterations} iteraciones")
    
    for i in range(iterations):
        print(f"\n[INFO] Recopilando metricas ({i+1}/{iterations})...")
        all_metrics = collect_all_metrics()
        print_metrics_table(all_metrics)
        export_to_json(all_metrics)
        
        if i < iterations - 1:
            print(f"[INFO] Siguiente recopilacion en {interval} segundos...")
            time.sleep(interval)
    
    print("\n[INFO] Monitoreo completado.")

if __name__ == "__main__":
    monitor_loop(interval=10, iterations=3)
