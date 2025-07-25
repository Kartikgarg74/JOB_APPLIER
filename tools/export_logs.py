import requests
import json
import csv
import sys
from datetime import datetime, timedelta

# Config
LOKI_URL = "http://localhost:3100"
LOG_QUERY = '{job="job-applier"}'
OUTPUT_FILE = "exported_logs.json"
START = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
END = datetime.utcnow().isoformat() + "Z"
LIMIT = 1000


def export_logs(query=LOG_QUERY, start=START, end=END, output=OUTPUT_FILE, as_csv=False):
    params = {
        "query": query,
        "start": start,
        "end": end,
        "limit": LIMIT,
        "direction": "FORWARD",
    }
    url = f"{LOKI_URL}/loki/api/v1/query_range"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    logs = []
    for stream in data.get("data", {}).get("result", []):
        for value in stream.get("values", []):
            ts, log_line = value
            log_entry = json.loads(log_line)
            log_entry["timestamp"] = ts
            logs.append(log_entry)
    if as_csv:
        if logs:
            keys = logs[0].keys()
            with open(output, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(logs)
    else:
        with open(output, "w") as f:
            json.dump(logs, f, indent=2)
    print(f"Exported {len(logs)} logs to {output}")

if __name__ == "__main__":
    as_csv = "--csv" in sys.argv
    export_logs(as_csv=as_csv)
