"""
Monitoring and observability for NEOC AI Assistant
Provides performance metrics, health checks, and system monitoring
"""
import time
import psutil
import threading
from typing import Dict, Any, List
from collections import deque
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collect and aggregate system and application metrics"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = deque(maxlen=max_history)
        self.start_time = time.time()
        self.lock = threading.Lock()

        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitoring_thread.start()

    def record_metric(self, name: str, value: float, tags: Dict[str, Any] = None) -> None:
        """Record a metric - O(1)"""
        with self.lock:
            metric = {
                'timestamp': time.time(),
                'name': name,
                'value': value,
                'tags': tags or {}
            }
            self.metrics_history.append(metric)

    def get_metrics(self, name: str = None, since: float = None) -> List[Dict]:
        """Get metrics with optional filtering - O(n)"""
        with self.lock:
            metrics = list(self.metrics_history)

        # Filter by name
        if name:
            metrics = [m for m in metrics if m['name'] == name]

        # Filter by time
        if since:
            metrics = [m for m in metrics if m['timestamp'] >= since]

        return metrics

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics - O(n)"""
        metrics = self.get_metrics()

        if not metrics:
            return {}

        # Group by metric name
        aggregated = {}
        for metric in metrics:
            name = metric['name']
            if name not in aggregated:
                aggregated[name] = {
                    'count': 0,
                    'sum': 0,
                    'min': float('inf'),
                    'max': float('-inf'),
                    'avg': 0
                }

            aggregated[name]['count'] += 1
            aggregated[name]['sum'] += metric['value']
            aggregated[name]['min'] = min(aggregated[name]['min'], metric['value'])
            aggregated[name]['max'] = max(aggregated[name]['max'], metric['value'])

        # Calculate averages
        for stats in aggregated.values():
            stats['avg'] = stats['sum'] / stats['count'] if stats['count'] > 0 else 0

        return aggregated

    def _background_monitor(self) -> None:
        """Background monitoring thread"""
        while True:
            try:
                # System metrics
                self.record_metric('cpu_percent', psutil.cpu_percent(interval=1))
                self.record_metric('memory_percent', psutil.virtual_memory().percent)
                self.record_metric('disk_usage_percent',
                                 psutil.disk_usage('/').percent)

                # Application uptime
                uptime = time.time() - self.start_time
                self.record_metric('app_uptime_seconds', uptime)

                time.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)  # Wait longer on error


class HealthChecker:
    """Health check system for various components"""

    def __init__(self):
        self.checks = {}
        self.last_results = {}

    def register_check(self, name: str, check_func, interval: int = 60):
        """Register a health check - O(1)"""
        self.checks[name] = {
            'func': check_func,
            'interval': interval,
            'last_run': 0
        }

    def run_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check - O(1)"""
        if name not in self.checks:
            return {'status': 'unknown', 'message': f'Check {name} not registered'}

        check_info = self.checks[name]
        current_time = time.time()

        # Check if we need to run the check
        if current_time - check_info['last_run'] < check_info['interval']:
            return self.last_results.get(name, {'status': 'unknown'})

        try:
            start_time = time.time()
            result = check_info['func']()
            check_time = time.time() - start_time

            health_result = {
                'status': 'healthy' if result else 'unhealthy',
                'check_time': check_time,
                'timestamp': current_time,
                'message': 'Check passed' if result else 'Check failed'
            }

            check_info['last_run'] = current_time
            self.last_results[name] = health_result

            return health_result

        except Exception as e:
            health_result = {
                'status': 'error',
                'error': str(e),
                'timestamp': current_time
            }
            self.last_results[name] = health_result
            return health_result

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks - O(n)"""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)

        # Overall health
        unhealthy_checks = [name for name, result in results.items()
                          if result.get('status') != 'healthy']

        results['overall'] = {
            'status': 'healthy' if not unhealthy_checks else 'unhealthy',
            'unhealthy_checks': unhealthy_checks,
            'total_checks': len(self.checks)
        }

        return results


class PerformanceMonitor:
    """Monitor function performance"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector

    def monitor_function(self, func_name: str):
        """Decorator to monitor function performance"""
        def decorator(func):
            import asyncio
            from functools import wraps

            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        self.metrics.record_metric(
                            f'function_execution_time',
                            execution_time,
                            {'function': func_name}
                        )
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        self.metrics.record_metric(
                            f'function_error',
                            execution_time,
                            {'function': func_name, 'error': str(e)}
                        )
                        raise
                return async_wrapper
            else:
                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        self.metrics.record_metric(
                            f'function_execution_time',
                            execution_time,
                            {'function': func_name}
                        )
                        return result
                    except Exception as e:
                        execution_time = time.time() - start_time
                        self.metrics.record_metric(
                            f'function_error',
                            execution_time,
                            {'function': func_name, 'error': str(e)}
                        )
                        raise
                return sync_wrapper
        return decorator

    def time_block(self, name: str):
        """Context manager for timing code blocks"""
        class Timer:
            def __init__(self, monitor, block_name):
                self.monitor = monitor
                self.block_name = block_name
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.start_time:
                    execution_time = time.time() - self.start_time
                    self.monitor.metrics.record_metric(
                        f'block_execution_time',
                        execution_time,
                        {'block': self.block_name}
                    )

        return Timer(self, name)


# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
performance_monitor = PerformanceMonitor(metrics_collector)


def init_monitoring():
    """Initialize monitoring system"""

    # Register health checks
    def check_ollama():
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_vectorstore():
        try:
            from .document_processor import document_processor
            return document_processor.vectorstore is not None
        except:
            return False

    def check_memory():
        memory = psutil.virtual_memory()
        return memory.percent < 90  # Less than 90% usage

    health_checker.register_check('ollama', check_ollama, interval=60)
    health_checker.register_check('vectorstore', check_vectorstore, interval=30)
    health_checker.register_check('memory', check_memory, interval=10)

    logger.info("Monitoring system initialized")


# Convenience functions for API endpoints
def get_system_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics"""
    return {
        'system': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime': time.time() - metrics_collector.start_time
        },
        'application': metrics_collector.get_aggregated_metrics(),
        'health': health_checker.run_all_checks()
    }