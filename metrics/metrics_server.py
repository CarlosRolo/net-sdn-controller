# -*- coding: utf-8 -*-
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

ODL_HOST = "127.0.0.1"
ODL_PORT = 8181
ODL_USER = "admin"
ODL_PASS = "admin"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def get_all_metrics():
    all_metrics = []
    for i in range(1, 5):
        switch_id = f"openflow:{i}"
        try:
            url = f"http://{ODL_HOST}:{ODL_PORT}/restconf/operational/opendaylight-inventory:nodes/node/{switch_id}/table/0"
            r = requests.get(url, headers=HEADERS, auth=(ODL_USER, ODL_PASS), timeout=5)
            if r.status_code == 200:
                flows = r.json().get("flow-node-inventory:table", [{}])[0].get("flow", [])
                for flow in flows:
                    stats = flow.get("opendaylight-flow-statistics:flow-statistics", {})
                    all_metrics.append({
                        "switch": switch_id,
                        "flow_id": flow.get("id", "unknown"),
                        "priority": flow.get("priority", 0),
                        "packets": int(stats.get("packet-count", 0)),
                        "bytes": int(stats.get("byte-count", 0)),
                        "duration_sec": int(stats.get("duration", {}).get("second", 0))
                    })
        except Exception as e:
            print(f"[ERROR] {switch_id}: {e}")
    return all_metrics

class MetricsHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_json(200, {"status": "ok"})
        elif self.path == "/metrics":
            metrics = get_all_metrics()
            self.send_json(200, {
                "timestamp": datetime.now().isoformat(),
                "total_flows": len(metrics),
                "total_packets": sum(m["packets"] for m in metrics),
                "total_bytes": sum(m["bytes"] for m in metrics),
                "flows": metrics
            })
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path == "/search":
            self.send_json(200, ["total_packets", "total_bytes", "total_flows"])

        elif self.path == "/query":
            metrics = get_all_metrics()
            total_packets = sum(m["packets"] for m in metrics)
            total_bytes = sum(m["bytes"] for m in metrics)
            now_ms = int(datetime.now().timestamp() * 1000)
            self.send_json(200, [
                {"target": "total_packets", "datapoints": [[total_packets, now_ms]]},
                {"target": "total_bytes", "datapoints": [[total_bytes, now_ms]]},
                {"target": "total_flows", "datapoints": [[len(metrics), now_ms]]}
            ])
        else:
            self.send_json(404, {"error": "not found"})

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 9090), MetricsHandler)
    print("[INFO] Metrics server corriendo en http://0.0.0.0:9090")
    server.serve_forever()
