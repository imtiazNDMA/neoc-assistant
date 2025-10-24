# Health API

The Health API provides endpoints for monitoring the health and status of NEOC AI Assistant services and components.

## Base URL

```
http://localhost:8000
```

## Endpoints

### GET /health

Get comprehensive health status of all system components.

#### Request

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": 3600,
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "memory_used": 3670016000,
    "memory_total": 8589934592,
    "disk_percent": 23.1,
    "disk_free": 243269632,
    "disk_total": 1000204886016
  },
  "services": {
    "llm_service": {
      "status": "healthy",
      "response_time": 0.8,
      "model_loaded": "phi3:latest",
      "last_check": "2024-01-15T10:30:00Z"
    },
    "rag_pipeline": {
      "status": "healthy",
      "documents_count": 150,
      "chunks_count": 12500,
      "vector_store_size": 524288000,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "vector_store": {
      "status": "healthy",
      "connection": "connected",
      "collections_count": 3,
      "last_check": "2024-01-15T10:30:00Z"
    },
    "cache_service": {
      "status": "healthy",
      "hit_rate": 0.85,
      "memory_usage": 52428800,
      "last_check": "2024-01-15T10:30:00Z"
    }
  },
  "config_valid": true,
  "dependencies": {
    "ollama": {
      "status": "healthy",
      "version": "0.1.0",
      "models_available": ["phi3:latest", "llama2:7b"]
    },
    "chromadb": {
      "status": "healthy",
      "version": "0.4.15",
      "collections": ["neoc_documents"]
    }
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall system status: "healthy", "degraded", "unhealthy" |
| `version` | string | Application version |
| `timestamp` | string | Health check timestamp (ISO 8601) |
| `uptime` | integer | System uptime in seconds |
| `system` | object | System resource metrics |
| `services` | object | Individual service health status |
| `config_valid` | boolean | Whether configuration is valid |
| `dependencies` | object | External dependency status |

#### System Metrics

| Field | Type | Description |
|-------|------|-------------|
| `cpu_percent` | float | CPU usage percentage |
| `memory_percent` | float | Memory usage percentage |
| `memory_used` | integer | Memory used in bytes |
| `memory_total` | integer | Total memory in bytes |
| `disk_percent` | float | Disk usage percentage |
| `disk_free` | integer | Free disk space in bytes |
| `disk_total` | integer | Total disk space in bytes |

#### Service Status

Each service object contains:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service status: "healthy", "degraded", "unhealthy" |
| `response_time` | float | Average response time in seconds |
| `last_check` | string | Last health check timestamp |

### GET /metrics

Get detailed Prometheus-compatible metrics.

#### Request

```http
GET /metrics
Accept: text/plain
```

#### Response

```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1234
python_gc_objects_collected_total{generation="1"} 567
python_gc_objects_collected_total{generation="2"} 89

# HELP neoc_requests_total Total number of requests
# TYPE neoc_requests_total counter
neoc_requests_total{method="GET",endpoint="/health"} 150
neoc_requests_total{method="POST",endpoint="/api/chat/"} 1250

# HELP neoc_response_time_seconds Response time in seconds
# TYPE neoc_response_time_seconds histogram
neoc_response_time_seconds_bucket{le="0.1"} 890
neoc_response_time_seconds_bucket{le="0.5"} 1200
neoc_response_time_seconds_bucket{le="1.0"} 1350
neoc_response_time_seconds_bucket{le="2.5"} 1420
neoc_response_time_seconds_bucket{le="5.0"} 1450
neoc_response_time_seconds_bucket{le="10.0"} 1470
neoc_response_time_seconds_bucket{le="+Inf"} 1500
neoc_response_time_seconds_count 1500
neoc_response_time_seconds_sum 2100.5

# HELP neoc_memory_usage_bytes Current memory usage
# TYPE neoc_memory_usage_bytes gauge
neoc_memory_usage_bytes 3670016000

# HELP neoc_cache_hit_rate Cache hit rate ratio
# TYPE neoc_cache_hit_rate gauge
neoc_cache_hit_rate 0.85

# HELP neoc_llm_tokens_total Total tokens used by LLM
# TYPE neoc_llm_tokens_total counter
neoc_llm_tokens_total{model="phi3:latest"} 45670

# HELP neoc_documents_processed_total Total documents processed
# TYPE neoc_documents_processed_total counter
neoc_documents_processed_total 150

# HELP neoc_vector_search_time_seconds Vector search response time
# TYPE neoc_vector_search_time_seconds histogram
neoc_vector_search_time_seconds_bucket{le="0.01"} 1200
neoc_vector_search_time_seconds_bucket{le="0.05"} 1350
neoc_vector_search_time_seconds_bucket{le="0.1"} 1420
neoc_vector_search_time_seconds_bucket{le="+Inf"} 1450
neoc_vector_search_time_seconds_count 1450
neoc_vector_search_time_seconds_sum 45.2
```

#### Available Metrics

**HTTP Metrics:**
- `neoc_requests_total`: Total requests by method and endpoint
- `neoc_response_time_seconds`: Response time distribution
- `neoc_requests_in_progress`: Currently active requests

**System Metrics:**
- `neoc_memory_usage_bytes`: Current memory usage
- `neoc_cpu_usage_percent`: CPU usage percentage
- `neoc_disk_usage_bytes`: Disk usage
- `neoc_network_bytes_total`: Network I/O

**Application Metrics:**
- `neoc_cache_hit_rate`: Cache performance
- `neoc_llm_tokens_total`: LLM token usage by model
- `neoc_documents_processed_total`: Document processing count
- `neoc_vector_search_time_seconds`: Vector search performance

**Error Metrics:**
- `neoc_errors_total`: Errors by type and component
- `neoc_rate_limit_hits_total`: Rate limit violations

### GET /health/ready

Kubernetes readiness probe endpoint.

#### Request

```http
GET /health/ready
```

#### Response (Healthy)

```json
{
  "status": "ready",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "ready",
    "llm_service": "ready",
    "vector_store": "ready"
  }
}
```

#### Response (Not Ready)

```json
{
  "status": "not_ready",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "ready",
    "llm_service": "starting",
    "vector_store": "error"
  }
}
```

### GET /health/live

Kubernetes liveness probe endpoint.

#### Request

```http
GET /health/live
```

#### Response (Alive)

```json
{
  "status": "alive",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Response (Not Alive)

```json
{
  "status": "dead",
  "timestamp": "2024-01-15T10:30:00Z",
  "error": "Service unresponsive"
}
```

## Health Check Configuration

### Health Check Intervals

```python
HEALTH_CHECK_CONFIG = {
    "system_check_interval": 30,      # seconds
    "service_check_interval": 60,     # seconds
    "dependency_check_interval": 300, # seconds (5 minutes)
    "timeout": 10,                    # seconds
    "retries": 3
}
```

### Health Thresholds

```python
HEALTH_THRESHOLDS = {
    "cpu_percent": 90,           # Alert if > 90%
    "memory_percent": 95,        # Alert if > 95%
    "disk_percent": 95,          # Alert if > 95%
    "response_time": 5.0,        # Alert if > 5 seconds
    "error_rate": 0.05,          # Alert if > 5%
    "cache_hit_rate": 0.7        # Alert if < 70%
}
```

## Monitoring Integration

### Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'neoc-ai-assistant'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 15s
    metrics_path: '/metrics'
```

### Grafana Dashboard

Key metrics to monitor:

1. **Request Rate**: `rate(neoc_requests_total[5m])`
2. **Response Time**: `histogram_quantile(0.95, rate(neoc_response_time_seconds_bucket[5m]))`
3. **Error Rate**: `rate(neoc_errors_total[5m]) / rate(neoc_requests_total[5m])`
4. **Memory Usage**: `neoc_memory_usage_bytes`
5. **Cache Performance**: `neoc_cache_hit_rate`

### Alerting Rules

```yaml
# alert_rules.yml
groups:
  - name: neoc_alerts
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(neoc_response_time_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"

      - alert: HighErrorRate
        expr: rate(neoc_errors_total[5m]) / rate(neoc_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: LowCacheHitRate
        expr: neoc_cache_hit_rate < 0.7
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate detected"
```

## Troubleshooting

### Common Health Issues

#### Service Unhealthy

**Symptoms:**
- Health endpoint returns `"status": "unhealthy"`
- Individual services show `"status": "unhealthy"`

**Possible Causes:**
1. **LLM Service Down**: Ollama not running or model not loaded
2. **Vector Store Issues**: ChromaDB connection problems
3. **Memory Issues**: System running out of memory
4. **Disk Issues**: Storage full or corrupted

**Resolution Steps:**
1. Check service logs
2. Verify dependencies are running
3. Check system resources
4. Restart affected services

#### High Response Times

**Symptoms:**
- `response_time` > 5 seconds
- Slow API responses

**Possible Causes:**
1. **High Load**: Too many concurrent requests
2. **Cache Misses**: Low cache hit rate
3. **LLM Latency**: Model inference slow
4. **Database Issues**: Slow vector searches

**Resolution Steps:**
1. Check current load
2. Monitor cache performance
3. Optimize queries
4. Scale resources if needed

#### Memory Issues

**Symptoms:**
- `memory_percent` > 90%
- Out of memory errors

**Possible Causes:**
1. **Memory Leaks**: Objects not being garbage collected
2. **Large Documents**: Processing very large files
3. **Cache Growth**: Cache consuming too much memory

**Resolution Steps:**
1. Monitor memory usage patterns
2. Clear caches if needed
3. Restart service to free memory
4. Optimize memory usage

### Diagnostic Commands

#### Check Service Status

```bash
# Quick health check
curl http://localhost:8000/health

# Detailed metrics
curl http://localhost:8000/metrics

# Check specific service
curl http://localhost:8000/health/ready
```

#### Monitor Logs

```bash
# View application logs
tail -f logs/app.log

# View LLM service logs
tail -f logs/llm_service.log

# View monitoring logs
tail -f logs/monitoring.log
```

#### System Diagnostics

```bash
# Check system resources
top
df -h
free -h

# Check running processes
ps aux | grep neoc

# Check network connections
netstat -tlnp | grep 8000
```

## Best Practices

### Health Check Design

1. **Lightweight Checks**: Health checks should be fast and not impact performance
2. **Dependency Checks**: Verify critical dependencies are available
3. **Timeout Handling**: Set appropriate timeouts for all checks
4. **Graceful Degradation**: System should work even if some checks fail

### Monitoring Strategy

1. **Key Metrics**: Focus on metrics that matter for user experience
2. **Alert Thresholds**: Set appropriate thresholds for different severity levels
3. **Dashboard Design**: Create dashboards for different audiences (dev, ops, business)
4. **Historical Data**: Keep historical metrics for trend analysis

### Incident Response

1. **Alert Classification**: Different response procedures for different alert types
2. **Escalation Paths**: Clear escalation procedures for critical issues
3. **Post-Mortem**: Analyze incidents to prevent recurrence
4. **Documentation**: Keep runbooks updated for common issues

## Examples

### Health Check Script

```python
import requests
import json
import time
from typing import Dict, Any

def check_health(base_url: str = "http://localhost:8000") -> Dict[str, Any]:
    """Comprehensive health check"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        health_data = response.json()

        # Check overall status
        overall_status = health_data.get("status")
        if overall_status != "healthy":
            return {
                "status": "unhealthy",
                "issues": [f"Overall status: {overall_status}"]
            }

        # Check individual services
        services = health_data.get("services", {})
        issues = []

        for service_name, service_info in services.items():
            if service_info.get("status") != "healthy":
                issues.append(f"{service_name}: {service_info.get('status')}")

        # Check system resources
        system = health_data.get("system", {})
        if system.get("memory_percent", 0) > 90:
            issues.append("High memory usage")
        if system.get("cpu_percent", 0) > 95:
            issues.append("High CPU usage")

        return {
            "status": "healthy" if not issues else "degraded",
            "issues": issues,
            "data": health_data
        }

    except Exception as e:
        return {
            "status": "error",
            "issues": [str(e)]
        }

# Continuous monitoring
def monitor_health(interval: int = 60):
    """Monitor health continuously"""
    while True:
        result = check_health()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if result["status"] != "healthy":
            print(f"[{timestamp}] HEALTH ISSUE: {result['status']}")
            for issue in result["issues"]:
                print(f"  - {issue}")
        else:
            print(f"[{timestamp}] Health check passed")

        time.sleep(interval)

if __name__ == "__main__":
    # Single check
    result = check_health()
    print(json.dumps(result, indent=2))

    # Or continuous monitoring
    # monitor_health()
```

### Prometheus Query Examples

```promql
# Request rate per second
rate(neoc_requests_total[5m])

# 95th percentile response time
histogram_quantile(0.95, rate(neoc_response_time_seconds_bucket[5m]))

# Error rate percentage
rate(neoc_errors_total[5m]) / rate(neoc_requests_total[5m]) * 100

# Memory usage trend
neoc_memory_usage_bytes / 1024 / 1024  # Convert to MB

# Cache performance
neoc_cache_hit_rate * 100  # Convert to percentage
```

## Support

For health monitoring support:

- **Documentation**: https://neoc-ai-assistant.readthedocs.io/monitoring/
- **Issues**: https://github.com/your-org/neoc-ai-assistant/issues
- **Metrics**: Access metrics at `/metrics` endpoint