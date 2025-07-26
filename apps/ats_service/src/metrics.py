from prometheus_client import Counter, Gauge, Histogram
import time

ats_score_counter = Counter('ats_scores_total', 'Total ATS scores calculated')
job_search_counter = Counter('ats_job_searches_total', 'Total job searches performed')
error_counter = Counter('ats_errors_total', 'Total error responses')
uptime_gauge = Gauge('ats_uptime_seconds', 'Application uptime in seconds')
startup_time = time.time()
request_count = Counter('ats_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('ats_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])
