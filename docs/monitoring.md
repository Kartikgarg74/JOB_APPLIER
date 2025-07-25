# Monitoring & Observability Guide

This project uses a free-tier compatible stack for metrics, logging, and alerting:
- **Prometheus**: Metrics collection
- **Loki**: Log aggregation
- **Promtail**: Log shipping
- **Grafana**: Visualization & alerting

## Metrics Collection

- **Backend (Python):**
  - Use `prometheus_client` to expose `/metrics` endpoints in API services.
  - Track:
    - API request/response times
    - Error counts/rates
    - User actions (logins, applications, uploads)
    - Resource usage (CPU, memory via nodeexporter)
- **Frontend (Node.js/TypeScript):**
  - Use `prom-client` for custom metrics if needed.

## Logging

- All logs are structured (JSON) and written to `output/centralized.log`.
- Promtail ships logs to Loki for aggregation.
- Logs include context: user, request, agent, error, performance data.

## Log Aggregation & Visualization

- **Promtail**: Configured in `tools/promtail-config.yaml` to watch `output/centralized.log`.
- **Loki**: Receives logs from Promtail.
- **Grafana**: Connects to Loki and Prometheus for dashboards.
- **Dashboards**:
  - Performance (latency, throughput)
  - Error rates
  - User activity (logins, applications, uploads)
  - Log search/filtering

## Alerting

- Grafana can be configured for free-tier email or Slack alerts.
- Example alerts:
  - High error rates
  - Slow response times
  - Unusual user activity

## Example Prometheus Config
See `tools/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'nodeexporter'
    static_configs:
      - targets: ['nodeexporter:9100']
  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
```

## Example Promtail Config
See `tools/promtail-config.yaml`:
```yaml
scrape_configs:
  - job_name: job-applier-logs
    static_configs:
      - targets: [localhost]
        labels:
          job: job-applier
          __path__: /Users/kartikgarg/Downloads/JOB APPLIER/output/centralized.log
```

## Exporting Logs
Use `tools/export_logs.py` to export logs from Loki for analysis or reporting.

## Setup
- Run Prometheus, Loki, Promtail, and Grafana (locally or via Docker Compose).
- Point Grafana to Prometheus and Loki as data sources.
- Import or create dashboards for metrics and logs.

## Best Practices
- Instrument all API endpoints and key business logic with metrics.
- Log all errors, warnings, and key user actions with context.
- Regularly review dashboards and alerts.

---
For more, see [Prometheus docs](https://prometheus.io/), [Grafana docs](https://grafana.com/docs/), and [Loki docs](https://grafana.com/docs/loki/latest/).
