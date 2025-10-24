#!/usr/bin/env python3
"""
Performance Tuning Script for NEOC AI Assistant
Analyzes system resources and recommends optimal configuration
"""

import os
import psutil
import json
from pathlib import Path
from typing import Dict, Any
import argparse

class PerformanceTuner:
    """Performance tuning and optimization recommendations"""

    def __init__(self):
        self.system_info = self._get_system_info()

    def _get_system_info(self) -> Dict[str, Any]:
        """Gather system information for tuning recommendations"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_count()
        disk = psutil.disk_usage('/')

        return {
            'total_memory_gb': memory.total / (1024**3),
            'available_memory_gb': memory.available / (1024**3),
            'cpu_cores': cpu,
            'cpu_logical': psutil.cpu_count(logical=True),
            'disk_total_gb': disk.total / (1024**3),
            'disk_free_gb': disk.free / (1024**3)
        }

    def analyze_current_config(self, config_path: str = ".env") -> Dict[str, Any]:
        """Analyze current configuration settings"""
        config = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value

        return config

    def recommend_configuration(self) -> Dict[str, Any]:
        """Generate optimal configuration recommendations"""
        mem_gb = self.system_info['total_memory_gb']
        cpu_cores = self.system_info['cpu_cores']

        # Base recommendations
        recommendations = {
            'LLM_MODEL': 'phi3:latest',
            'LLM_TEMPERATURE': '0.1',
            'LLM_CONTEXT_WINDOW': '2048',
            'API_HOST': '0.0.0.0',
            'API_PORT': '8000',
            'LOG_LEVEL': 'INFO'
        }

        # Memory-based recommendations
        if mem_gb >= 16:
            # High memory system
            recommendations.update({
                'MAX_MEMORY_MB': '2048',
                'RAG_CACHE_SIZE': '500',
                'LLM_CACHE_SIZE': '100',
                'CHUNK_SIZE': '512',
                'MAX_REQUESTS_PER_MINUTE': '200'
            })
        elif mem_gb >= 8:
            # Medium memory system
            recommendations.update({
                'MAX_MEMORY_MB': '1024',
                'RAG_CACHE_SIZE': '300',
                'LLM_CACHE_SIZE': '50',
                'CHUNK_SIZE': '512',
                'MAX_REQUESTS_PER_MINUTE': '100'
            })
        elif mem_gb >= 4:
            # Low memory system
            recommendations.update({
                'MAX_MEMORY_MB': '512',
                'RAG_CACHE_SIZE': '150',
                'LLM_CACHE_SIZE': '25',
                'CHUNK_SIZE': '256',
                'MAX_REQUESTS_PER_MINUTE': '50'
            })
        else:
            # Very low memory system
            recommendations.update({
                'MAX_MEMORY_MB': '256',
                'RAG_CACHE_SIZE': '100',
                'LLM_CACHE_SIZE': '10',
                'CHUNK_SIZE': '128',
                'MAX_REQUESTS_PER_MINUTE': '25'
            })

        # CPU-based recommendations
        if cpu_cores >= 8:
            recommendations['LLM_TIMEOUT'] = '30'
        elif cpu_cores >= 4:
            recommendations['LLM_TIMEOUT'] = '45'
        else:
            recommendations['LLM_TIMEOUT'] = '60'

        # Security recommendations based on resources
        if mem_gb >= 8:
            recommendations.update({
                'ENABLE_RATE_LIMITING': 'true',
                'ENABLE_INPUT_VALIDATION': 'true',
                'MAX_INPUT_LENGTH': '2000'
            })
        else:
            recommendations.update({
                'ENABLE_RATE_LIMITING': 'true',
                'ENABLE_INPUT_VALIDATION': 'true',
                'MAX_INPUT_LENGTH': '1000'
            })

        return recommendations

    def generate_config_file(self, output_path: str = ".env.optimized") -> None:
        """Generate optimized configuration file"""
        recommendations = self.recommend_configuration()

        with open(output_path, 'w') as f:
            f.write("# NEOC AI Assistant - Optimized Configuration\n")
            f.write(f"# Generated for system with {self.system_info['total_memory_gb']:.1f}GB RAM, {self.system_info['cpu_cores']} CPU cores\n")
            f.write("# Generated on: " + str(psutil.datetime.datetime.now()) + "\n\n")

            for key, value in recommendations.items():
                f.write(f"{key}={value}\n")

        print(f"[SUCCESS] Optimized configuration saved to {output_path}")

    def benchmark_system(self) -> Dict[str, Any]:
        """Run basic system benchmarks"""
        print("[BENCHMARK] Running system benchmarks...")

        # Memory benchmark
        memory_test = []
        for i in range(10):
            memory_test.append("x" * 1000000)  # 1MB strings
            if i % 3 == 0:
                memory_test.pop(0)

        # CPU benchmark (simple calculation)
        import time
        start_time = time.time()
        result = sum(i*i for i in range(1000000))
        cpu_time = time.time() - start_time

        return {
            'memory_operations_per_sec': len(memory_test) / 0.1,  # Rough estimate
            'cpu_operations_per_sec': 1000000 / cpu_time,
            'system_info': self.system_info
        }

    def print_report(self) -> None:
        """Print comprehensive performance report"""
        print("NEOC AI Assistant Performance Analysis Report")
        print("=" * 50)

        print("\n[SYSTEM] System Information:")
        for key, value in self.system_info.items():
            if 'gb' in key.lower():
                print(f"  {key.replace('_', ' ').title()}: {value:.1f} GB")
            else:
                print(f"  {key.replace('_', ' ').title()}: {value}")

        print("\n[CONFIG] Recommended Configuration:")
        recommendations = self.recommend_configuration()
        for key, value in recommendations.items():
            print(f"  {key}: {value}")

        print("\n[TIPS] Performance Tips:")
        mem_gb = self.system_info['total_memory_gb']
        if mem_gb >= 16:
            print("  • High-memory system detected - can handle large caches")
            print("  • Consider increasing MAX_REQUESTS_PER_MINUTE for higher throughput")
        elif mem_gb >= 8:
            print("  • Balanced system - good for production workloads")
            print("  • Monitor memory usage during peak loads")
        else:
            print("  • Memory-constrained system - focus on efficiency")
            print("  • Consider smaller batch sizes and cache limits")

        if self.system_info['cpu_cores'] >= 4:
            print("  • Multi-core CPU - good for concurrent requests")
        else:
            print("  • Limited CPU cores - consider async processing optimizations")

def main():
    parser = argparse.ArgumentParser(description="NEOC AI Assistant Performance Tuner")
    parser.add_argument("--analyze", action="store_true", help="Analyze current configuration")
    parser.add_argument("--generate", action="store_true", help="Generate optimized config")
    parser.add_argument("--benchmark", action="store_true", help="Run system benchmarks")
    parser.add_argument("--output", default=".env.optimized", help="Output config file path")

    args = parser.parse_args()

    tuner = PerformanceTuner()

    if args.analyze:
        current_config = tuner.analyze_current_config()
        print("📋 Current Configuration:")
        for key, value in current_config.items():
            print(f"  {key}: {value}")

    if args.benchmark:
        results = tuner.benchmark_system()
        print("🏃 Benchmark Results:")
        print(".2f")
        print(".0f")

    if args.generate:
        tuner.generate_config_file(args.output)

    if not any([args.analyze, args.generate, args.benchmark]):
        tuner.print_report()

if __name__ == "__main__":
    main()