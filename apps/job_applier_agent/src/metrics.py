from prometheus_client import Counter, Gauge, Histogram

signup_counter = Counter('signups_total', 'Total user signups')
login_counter = Counter('logins_total', 'Total user logins')
job_apply_counter = Counter('job_applications_total', 'Total job applications')
profile_update_counter = Counter('profile_updates_total', 'Total profile updates')
uptime_gauge = Gauge('app_uptime_seconds', 'Application uptime in seconds')
error_counter = Counter('errors_total', 'Total error responses')
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status_code'])
request_latency = Histogram('api_request_latency_seconds', 'API request latency in seconds', ['method', 'endpoint'])
