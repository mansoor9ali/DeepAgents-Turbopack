"""
SRE (Site Reliability Engineering) Tools

Tools for infrastructure operations, incident management, and service health monitoring.
Designed for natural language driven SRE automation with human-in-the-loop approval.

This module provides tools for:
- Service health monitoring
- Log analysis and diagnostics
- Incident management
- Service lifecycle operations (restart, scale, rollback)
- Runbook execution
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict

from langchain.tools import tool
from pydantic import BaseModel, Field


# =============================================================================
# ENUMS (Type-safe parameter options)
# =============================================================================

class ServiceStatus(str, Enum):
    """Service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class LogLevel(str, Enum):
    """Log severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    SEV1 = "sev1"  # Critical - Complete service outage
    SEV2 = "sev2"  # Major - Significant impact
    SEV3 = "sev3"  # Minor - Limited impact
    SEV4 = "sev4"  # Low - Minimal impact


class DiagnosticType(str, Enum):
    """Types of diagnostic checks."""
    CONNECTIVITY = "connectivity"
    PERFORMANCE = "performance"
    RESOURCES = "resources"
    DEPENDENCIES = "dependencies"
    FULL = "full"


class RunbookType(str, Enum):
    """Pre-defined runbook types."""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    ROTATE_LOGS = "rotate_logs"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FAILOVER = "failover"
    HEALTH_CHECK = "health_check"


# =============================================================================
# SCHEMAS
# =============================================================================

class ServiceInfo(BaseModel):
    """Service information schema."""
    name: str = Field(description="Service name")
    namespace: str = Field(default="default", description="Kubernetes namespace")
    environment: str = Field(default="production", description="Environment (production/staging/dev)")


class IncidentInfo(BaseModel):
    """Incident creation schema."""
    title: str = Field(description="Incident title")
    description: str = Field(description="Detailed description")
    severity: IncidentSeverity = Field(description="Incident severity level")
    affected_services: List[str] = Field(description="List of affected services")


# =============================================================================
# SIMULATED DATA (Replace with real integrations)
# =============================================================================

MOCK_SERVICES = {
    "api-gateway": {
        "status": "healthy",
        "replicas": 3,
        "cpu": 45,
        "memory": 62,
        "latency_p99": 120,
        "error_rate": 0.1,
        "version": "v2.4.1",
        "last_deploy": "2024-01-10T14:30:00Z"
    },
    "user-service": {
        "status": "healthy",
        "replicas": 2,
        "cpu": 30,
        "memory": 45,
        "latency_p99": 80,
        "error_rate": 0.05,
        "version": "v1.8.3",
        "last_deploy": "2024-01-08T10:15:00Z"
    },
    "order-service": {
        "status": "degraded",
        "replicas": 3,
        "cpu": 85,
        "memory": 78,
        "latency_p99": 450,
        "error_rate": 2.5,
        "version": "v3.2.0",
        "last_deploy": "2024-01-12T09:00:00Z"
    },
    "payment-service": {
        "status": "healthy",
        "replicas": 4,
        "cpu": 55,
        "memory": 60,
        "latency_p99": 200,
        "error_rate": 0.02,
        "version": "v2.1.5",
        "last_deploy": "2024-01-05T16:45:00Z"
    },
    "inventory-service": {
        "status": "unhealthy",
        "replicas": 2,
        "cpu": 95,
        "memory": 92,
        "latency_p99": 2500,
        "error_rate": 15.3,
        "version": "v1.5.2",
        "last_deploy": "2024-01-11T11:20:00Z"
    },
    "notification-service": {
        "status": "healthy",
        "replicas": 2,
        "cpu": 25,
        "memory": 35,
        "latency_p99": 50,
        "error_rate": 0.1,
        "version": "v1.3.0",
        "last_deploy": "2024-01-02T08:00:00Z"
    },
    "cache-service": {
        "status": "healthy",
        "replicas": 3,
        "cpu": 40,
        "memory": 70,
        "latency_p99": 5,
        "error_rate": 0.01,
        "version": "v1.0.2",
        "last_deploy": "2023-12-20T12:00:00Z"
    },
    "database-primary": {
        "status": "healthy",
        "replicas": 1,
        "cpu": 65,
        "memory": 80,
        "latency_p99": 15,
        "error_rate": 0.0,
        "version": "v14.2",
        "last_deploy": "2023-11-15T03:00:00Z"
    }
}


def _generate_mock_logs(service: str, level: str, count: int) -> List[Dict]:
    """Generate mock log entries."""
    log_messages = {
        "error": [
            "Connection timeout to downstream service",
            "Database query failed: connection refused",
            "Memory allocation failed",
            "Request processing error: null pointer exception",
            "Failed to parse configuration file",
            "Circuit breaker opened for dependency",
        ],
        "warning": [
            "High memory usage detected: 85%",
            "Slow query detected: 2500ms",
            "Connection pool nearly exhausted",
            "Retry attempt 3/5 for external API call",
            "Cache miss rate above threshold",
        ],
        "info": [
            "Service started successfully",
            "Health check passed",
            "Configuration reloaded",
            "New connection established",
            "Request processed successfully",
        ],
    }

    logs = []
    base_time = datetime.now()
    messages = log_messages.get(level, log_messages["info"])

    for i in range(count):
        logs.append({
            "timestamp": (base_time - timedelta(minutes=i*5)).isoformat(),
            "level": level.upper(),
            "service": service,
            "message": random.choice(messages),
            "trace_id": f"trace-{random.randint(10000, 99999)}"
        })

    return logs


# =============================================================================
# TOOLS - READ-ONLY OPERATIONS (No approval required)
# =============================================================================

@tool(
    name_or_callable="list_services",
    description="""List all managed services in the infrastructure.

Use this tool to get an overview of all services, their status, and basic metrics.
This is typically the first tool to use when investigating issues.

Returns:
    JSON list of all services with their current status and basic info
""",
)
async def list_services(
    environment: str = "production",
    status_filter: Optional[ServiceStatus] = None
) -> str:
    """List all managed services.

    Args:
        environment: Environment to list services from
        status_filter: Optional filter by status

    Returns:
        JSON string with service list
    """
    def _execute():
        try:
            services = []
            for name, info in MOCK_SERVICES.items():
                if status_filter and info["status"] != status_filter.value:
                    continue
                services.append({
                    "name": name,
                    "status": info["status"],
                    "replicas": info["replicas"],
                    "version": info["version"],
                    "error_rate": f"{info['error_rate']}%"
                })

            result = {
                "environment": environment,
                "total_services": len(services),
                "services": services,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error listing services: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="check_service_health",
    description="""Check the health status of a specific service.

Use this tool to get detailed health information about a service including:
- Current status (healthy/degraded/unhealthy)
- Resource utilization (CPU, memory)
- Performance metrics (latency, error rate)
- Deployment information

Args:
    service_name: Name of the service to check (e.g., 'api-gateway', 'order-service')
""",
)
async def check_service_health(service_name: str) -> str:
    """Check health status of a service.

    Args:
        service_name: Name of the service

    Returns:
        JSON string with detailed health info
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            info = MOCK_SERVICES[service_name]

            # Determine health issues
            issues = []
            if info["cpu"] > 80:
                issues.append(f"High CPU usage: {info['cpu']}%")
            if info["memory"] > 85:
                issues.append(f"High memory usage: {info['memory']}%")
            if info["latency_p99"] > 500:
                issues.append(f"High latency: {info['latency_p99']}ms p99")
            if info["error_rate"] > 1:
                issues.append(f"Elevated error rate: {info['error_rate']}%")

            result = {
                "service": service_name,
                "status": info["status"],
                "health_check": {
                    "passed": info["status"] == "healthy",
                    "issues": issues if issues else ["No issues detected"]
                },
                "resources": {
                    "cpu_percent": info["cpu"],
                    "memory_percent": info["memory"],
                    "replicas": info["replicas"]
                },
                "performance": {
                    "latency_p99_ms": info["latency_p99"],
                    "error_rate_percent": info["error_rate"]
                },
                "deployment": {
                    "version": info["version"],
                    "last_deploy": info["last_deploy"]
                },
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error checking service health: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="get_service_logs",
    description="""Retrieve logs from a specific service.

Use this tool to analyze logs when investigating issues. You can filter by:
- Log level (error, warning, info)
- Time range (via limit parameter)

Args:
    service_name: Name of the service to get logs from
    log_level: Filter by log level (error, warning, info)
    limit: Maximum number of log entries to retrieve (default: 10)
""",
)
async def get_service_logs(
    service_name: str,
    log_level: LogLevel = LogLevel.ERROR,
    limit: int = 10
) -> str:
    """Retrieve service logs.

    Args:
        service_name: Name of the service
        log_level: Log level to filter
        limit: Max entries to return

    Returns:
        JSON string with log entries
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            logs = _generate_mock_logs(service_name, log_level.value, min(limit, 50))

            result = {
                "service": service_name,
                "log_level": log_level.value,
                "count": len(logs),
                "logs": logs,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error retrieving logs: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="get_service_metrics",
    description="""Get detailed metrics for a service.

Use this tool to get current and historical metrics including:
- CPU and memory usage trends
- Request latency percentiles
- Error rates over time
- Throughput (requests per second)

Args:
    service_name: Name of the service to get metrics for
    time_range: Time range for metrics (e.g., '1h', '6h', '24h')
""",
)
async def get_service_metrics(
    service_name: str,
    time_range: str = "1h"
) -> str:
    """Get detailed service metrics.

    Args:
        service_name: Name of the service
        time_range: Time range for historical data

    Returns:
        JSON string with metrics data
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            info = MOCK_SERVICES[service_name]

            # Generate mock time-series data
            data_points = 6
            cpu_trend = [max(10, info["cpu"] + random.randint(-15, 15)) for _ in range(data_points)]
            memory_trend = [max(20, info["memory"] + random.randint(-10, 10)) for _ in range(data_points)]

            result = {
                "service": service_name,
                "time_range": time_range,
                "current": {
                    "cpu_percent": info["cpu"],
                    "memory_percent": info["memory"],
                    "latency_p50_ms": int(info["latency_p99"] * 0.4),
                    "latency_p95_ms": int(info["latency_p99"] * 0.8),
                    "latency_p99_ms": info["latency_p99"],
                    "error_rate_percent": info["error_rate"],
                    "requests_per_second": random.randint(100, 1000)
                },
                "trends": {
                    "cpu": cpu_trend,
                    "memory": memory_trend,
                    "labels": [f"-{(data_points-i)*10}min" for i in range(data_points)]
                },
                "alerts": {
                    "cpu_threshold": 80,
                    "memory_threshold": 85,
                    "latency_threshold_ms": 500,
                    "error_rate_threshold": 1.0
                },
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error retrieving metrics: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="run_diagnostic",
    description="""Run diagnostic checks on a service.

Use this tool to perform automated diagnostic checks including:
- connectivity: Check network connectivity to dependencies
- performance: Analyze performance bottlenecks
- resources: Check resource utilization and limits
- dependencies: Verify all dependent services are healthy
- full: Run all diagnostic checks

Args:
    service_name: Name of the service to diagnose
    diagnostic_type: Type of diagnostic to run (connectivity, performance, resources, dependencies, full)
""",
)
async def run_diagnostic(
    service_name: str,
    diagnostic_type: DiagnosticType = DiagnosticType.FULL
) -> str:
    """Run diagnostic checks on a service.

    Args:
        service_name: Name of the service
        diagnostic_type: Type of diagnostic to run

    Returns:
        JSON string with diagnostic results
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            info = MOCK_SERVICES[service_name]
            checks = {}
            recommendations = []

            # Connectivity checks
            if diagnostic_type in [DiagnosticType.CONNECTIVITY, DiagnosticType.FULL]:
                checks["connectivity"] = {
                    "database": {"status": "pass", "latency_ms": 5},
                    "cache": {"status": "pass", "latency_ms": 2},
                    "message_queue": {"status": "pass", "latency_ms": 8},
                    "external_api": {"status": "pass" if random.random() > 0.3 else "slow", "latency_ms": random.randint(50, 200)}
                }

            # Performance checks
            if diagnostic_type in [DiagnosticType.PERFORMANCE, DiagnosticType.FULL]:
                perf_status = "pass"
                if info["latency_p99"] > 500:
                    perf_status = "warning"
                    recommendations.append("Consider scaling up replicas to handle load")
                if info["latency_p99"] > 1000:
                    perf_status = "critical"
                    recommendations.append("Investigate slow database queries")

                checks["performance"] = {
                    "status": perf_status,
                    "latency_p99_ms": info["latency_p99"],
                    "throughput_rps": random.randint(100, 500),
                    "slow_queries_detected": info["latency_p99"] > 300
                }

            # Resource checks
            if diagnostic_type in [DiagnosticType.RESOURCES, DiagnosticType.FULL]:
                resource_status = "pass"
                if info["cpu"] > 80 or info["memory"] > 85:
                    resource_status = "warning"
                    recommendations.append("Resource utilization high - consider scaling")
                if info["cpu"] > 90 or info["memory"] > 95:
                    resource_status = "critical"
                    recommendations.append("Critical resource exhaustion - immediate action required")

                checks["resources"] = {
                    "status": resource_status,
                    "cpu_percent": info["cpu"],
                    "memory_percent": info["memory"],
                    "disk_percent": random.randint(40, 70),
                    "pod_restarts_24h": random.randint(0, 5) if info["status"] != "healthy" else 0
                }

            # Dependency checks
            if diagnostic_type in [DiagnosticType.DEPENDENCIES, DiagnosticType.FULL]:
                dep_checks = {}
                for dep_name, dep_info in MOCK_SERVICES.items():
                    if dep_name != service_name:
                        dep_checks[dep_name] = {
                            "status": dep_info["status"],
                            "reachable": True
                        }
                checks["dependencies"] = dep_checks

                # Check for unhealthy dependencies
                unhealthy_deps = [n for n, d in dep_checks.items() if d["status"] != "healthy"]
                if unhealthy_deps:
                    recommendations.append(f"Dependent services unhealthy: {', '.join(unhealthy_deps)}")

            overall_status = "pass"
            for check in checks.values():
                if isinstance(check, dict) and check.get("status") == "critical":
                    overall_status = "critical"
                    break
                elif isinstance(check, dict) and check.get("status") == "warning":
                    overall_status = "warning"

            result = {
                "service": service_name,
                "diagnostic_type": diagnostic_type.value,
                "overall_status": overall_status,
                "checks": checks,
                "recommendations": recommendations if recommendations else ["No issues detected"],
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error running diagnostic: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="analyze_incident",
    description="""Analyze an ongoing or recent incident.

Use this tool to get AI-assisted analysis of an incident including:
- Root cause analysis
- Impact assessment
- Timeline of events
- Recommended remediation steps

Args:
    affected_services: Comma-separated list of affected service names
    symptoms: Description of observed symptoms/issues
""",
)
async def analyze_incident(
    affected_services: str,
    symptoms: str
) -> str:
    """Analyze an incident and provide recommendations.

    Args:
        affected_services: Comma-separated service names
        symptoms: Description of symptoms

    Returns:
        JSON string with incident analysis
    """
    def _execute():
        try:
            services = [s.strip() for s in affected_services.split(",")]

            # Gather data from affected services
            service_data = {}
            for svc in services:
                if svc in MOCK_SERVICES:
                    service_data[svc] = MOCK_SERVICES[svc]

            if not service_data:
                return f"Error: No valid services found. Available: {', '.join(MOCK_SERVICES.keys())}"

            # Generate analysis
            root_causes = []
            mitigations = []

            for svc, data in service_data.items():
                if data["cpu"] > 80:
                    root_causes.append(f"{svc}: High CPU utilization ({data['cpu']}%)")
                    mitigations.append(f"Scale up {svc} replicas or optimize CPU-intensive operations")
                if data["memory"] > 85:
                    root_causes.append(f"{svc}: Memory pressure ({data['memory']}%)")
                    mitigations.append(f"Check {svc} for memory leaks or increase memory limits")
                if data["error_rate"] > 1:
                    root_causes.append(f"{svc}: Elevated error rate ({data['error_rate']}%)")
                    mitigations.append(f"Review {svc} error logs and recent deployments")
                if data["latency_p99"] > 500:
                    root_causes.append(f"{svc}: High latency ({data['latency_p99']}ms)")
                    mitigations.append(f"Check {svc} dependencies and database queries")

            if not root_causes:
                root_causes.append("No obvious issues detected in metrics - may require deeper investigation")

            impact = "high" if any(d["status"] == "unhealthy" for d in service_data.values()) else \
                     "medium" if any(d["status"] == "degraded" for d in service_data.values()) else "low"

            result = {
                "incident_analysis": {
                    "affected_services": services,
                    "symptoms_reported": symptoms,
                    "impact_level": impact
                },
                "root_cause_analysis": root_causes,
                "service_status": {svc: data["status"] for svc, data in service_data.items()},
                "recommended_mitigations": mitigations if mitigations else ["Continue monitoring - no immediate action required"],
                "immediate_actions": [
                    "Check recent deployments for changes",
                    "Review error logs for stack traces",
                    "Verify external dependency status",
                    "Consider rollback if recently deployed"
                ],
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error analyzing incident: {str(e)}"

    return await asyncio.to_thread(_execute)


# =============================================================================
# TOOLS - WRITE OPERATIONS (Require human approval)
# =============================================================================

@tool(
    name_or_callable="restart_service",
    description="""Restart a service.

**REQUIRES APPROVAL** - This action will cause brief downtime.

Use this tool to restart a service when:
- The service is stuck or unresponsive
- Configuration changes need to be applied
- Memory leaks need to be cleared

Args:
    service_name: Name of the service to restart
    reason: Reason for the restart (for audit logging)
""",
)
async def restart_service(
    service_name: str,
    reason: str
) -> str:
    """Restart a service (rolling restart).

    Args:
        service_name: Name of the service
        reason: Reason for restart

    Returns:
        JSON string with restart status
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            info = MOCK_SERVICES[service_name]

            result = {
                "action": "restart_service",
                "service": service_name,
                "status": "completed",
                "details": {
                    "restart_type": "rolling",
                    "replicas_restarted": info["replicas"],
                    "downtime": "0s (rolling restart)",
                    "reason": reason
                },
                "new_status": "healthy",
                "timestamp": datetime.now().isoformat()
            }

            # Simulate the restart fixing the service
            MOCK_SERVICES[service_name]["status"] = "healthy"
            MOCK_SERVICES[service_name]["cpu"] = min(60, info["cpu"])
            MOCK_SERVICES[service_name]["memory"] = min(65, info["memory"])

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error restarting service: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="scale_service",
    description="""Scale a service up or down.

**REQUIRES APPROVAL** - This action affects service capacity and costs.

Use this tool to:
- Scale up: Handle increased load or improve redundancy
- Scale down: Reduce costs during low-traffic periods

Args:
    service_name: Name of the service to scale
    target_replicas: Target number of replicas (1-10)
    reason: Reason for scaling (for audit logging)
""",
)
async def scale_service(
    service_name: str,
    target_replicas: int,
    reason: str
) -> str:
    """Scale service replicas.

    Args:
        service_name: Name of the service
        target_replicas: Target replica count
        reason: Reason for scaling

    Returns:
        JSON string with scaling status
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            if not 1 <= target_replicas <= 10:
                return "Error: target_replicas must be between 1 and 10"

            info = MOCK_SERVICES[service_name]
            old_replicas = info["replicas"]

            result = {
                "action": "scale_service",
                "service": service_name,
                "status": "completed",
                "details": {
                    "previous_replicas": old_replicas,
                    "new_replicas": target_replicas,
                    "scale_direction": "up" if target_replicas > old_replicas else "down",
                    "reason": reason
                },
                "estimated_time": "30-60 seconds",
                "timestamp": datetime.now().isoformat()
            }

            # Update the mock data
            MOCK_SERVICES[service_name]["replicas"] = target_replicas

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error scaling service: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="rollback_deployment",
    description="""Rollback a service to a previous version.

**REQUIRES APPROVAL** - This action will replace the current deployment.

Use this tool when:
- A recent deployment introduced bugs
- Performance degraded after a release
- Urgent rollback is needed to restore service

Args:
    service_name: Name of the service to rollback
    target_version: Version to rollback to (e.g., 'v2.3.0' or 'previous')
    reason: Reason for rollback (for audit logging)
""",
)
async def rollback_deployment(
    service_name: str,
    target_version: str = "previous",
    reason: str = "Rollback to restore service stability"
) -> str:
    """Rollback service to a previous version.

    Args:
        service_name: Name of the service
        target_version: Target version or 'previous'
        reason: Reason for rollback

    Returns:
        JSON string with rollback status
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            info = MOCK_SERVICES[service_name]
            current_version = info["version"]

            # Simulate version decrement for 'previous'
            if target_version == "previous":
                parts = current_version.replace("v", "").split(".")
                parts[-1] = str(max(0, int(parts[-1]) - 1))
                new_version = "v" + ".".join(parts)
            else:
                new_version = target_version

            result = {
                "action": "rollback_deployment",
                "service": service_name,
                "status": "completed",
                "details": {
                    "previous_version": current_version,
                    "rolled_back_to": new_version,
                    "reason": reason,
                    "replicas_updated": info["replicas"]
                },
                "verification": {
                    "health_check": "passed",
                    "readiness_check": "passed"
                },
                "timestamp": datetime.now().isoformat()
            }

            # Update mock data
            MOCK_SERVICES[service_name]["version"] = new_version
            MOCK_SERVICES[service_name]["status"] = "healthy"
            MOCK_SERVICES[service_name]["error_rate"] = 0.1
            MOCK_SERVICES[service_name]["latency_p99"] = 100

            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error rolling back deployment: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="execute_runbook",
    description="""Execute a pre-defined runbook.

**REQUIRES APPROVAL** - Runbooks perform automated remediation steps.

Available runbooks:
- restart_service: Performs rolling restart
- clear_cache: Clears service cache
- rotate_logs: Rotates and archives logs
- scale_up: Doubles current replicas
- scale_down: Halves current replicas
- failover: Triggers failover to secondary
- health_check: Runs comprehensive health checks

Args:
    service_name: Name of the service to run the runbook against
    runbook_type: Type of runbook to execute
    parameters: Optional JSON string with additional parameters
""",
)
async def execute_runbook(
    service_name: str,
    runbook_type: RunbookType,
    parameters: str = "{}"
) -> str:
    """Execute a pre-defined runbook.

    Args:
        service_name: Name of the service
        runbook_type: Type of runbook
        parameters: Additional parameters as JSON

    Returns:
        JSON string with runbook execution results
    """
    def _execute():
        try:
            if service_name not in MOCK_SERVICES:
                available = ", ".join(MOCK_SERVICES.keys())
                return f"Error: Service '{service_name}' not found. Available services: {available}"

            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                params = {}

            info = MOCK_SERVICES[service_name]
            steps_executed = []

            if runbook_type == RunbookType.RESTART_SERVICE:
                steps_executed = [
                    "Draining connections from pod 1",
                    "Restarting pod 1",
                    "Pod 1 healthy, draining pod 2",
                    "Restarting pod 2",
                    "All pods restarted successfully"
                ]
                MOCK_SERVICES[service_name]["status"] = "healthy"

            elif runbook_type == RunbookType.CLEAR_CACHE:
                steps_executed = [
                    "Connecting to cache service",
                    "Flushing cache keys for service",
                    "Cache cleared successfully",
                    "Warming up critical cache entries"
                ]

            elif runbook_type == RunbookType.SCALE_UP:
                new_replicas = min(10, info["replicas"] * 2)
                steps_executed = [
                    f"Current replicas: {info['replicas']}",
                    f"Scaling to: {new_replicas} replicas",
                    "New pods scheduled",
                    "Pods ready and receiving traffic"
                ]
                MOCK_SERVICES[service_name]["replicas"] = new_replicas

            elif runbook_type == RunbookType.HEALTH_CHECK:
                steps_executed = [
                    "Running connectivity checks",
                    "Verifying database connections",
                    "Checking cache connectivity",
                    "Validating external API access",
                    "All health checks passed"
                ]

            else:
                steps_executed = [f"Executed {runbook_type.value} runbook"]

            result = {
                "action": "execute_runbook",
                "runbook": runbook_type.value,
                "service": service_name,
                "status": "completed",
                "steps_executed": steps_executed,
                "parameters_used": params,
                "duration_seconds": random.randint(10, 60),
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error executing runbook: {str(e)}"

    return await asyncio.to_thread(_execute)


@tool(
    name_or_callable="create_incident",
    description="""Create an incident ticket for tracking.

**REQUIRES APPROVAL** - Creating incidents triggers on-call notifications.

Use this tool to create an incident when:
- A significant service disruption is detected
- Multiple services are affected
- Customer-impacting issues are identified

Args:
    title: Short title describing the incident
    description: Detailed description of the issue
    severity: Severity level (sev1=critical, sev2=major, sev3=minor, sev4=low)
    affected_services: Comma-separated list of affected service names
""",
)
async def create_incident(
    title: str,
    description: str,
    severity: IncidentSeverity,
    affected_services: str
) -> str:
    """Create an incident ticket.

    Args:
        title: Incident title
        description: Detailed description
        severity: Severity level
        affected_services: Comma-separated services

    Returns:
        JSON string with incident details
    """
    def _execute():
        try:
            services = [s.strip() for s in affected_services.split(",")]
            incident_id = f"INC-{random.randint(10000, 99999)}"

            result = {
                "action": "create_incident",
                "status": "created",
                "incident": {
                    "id": incident_id,
                    "title": title,
                    "description": description,
                    "severity": severity.value,
                    "affected_services": services,
                    "status": "open",
                    "created_at": datetime.now().isoformat()
                },
                "notifications": {
                    "on_call_paged": severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2],
                    "slack_channel_created": True,
                    "stakeholders_notified": True
                },
                "next_steps": [
                    f"Incident {incident_id} created",
                    "On-call engineer has been notified" if severity in [IncidentSeverity.SEV1, IncidentSeverity.SEV2] else "Ticket assigned to queue",
                    f"Track at: https://incidents.example.com/{incident_id}"
                ]
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error creating incident: {str(e)}"

    return await asyncio.to_thread(_execute)


# =============================================================================
# TOOL COLLECTION
# =============================================================================

# Read-only tools (no approval needed)
READ_ONLY_TOOLS = [
    list_services,
    check_service_health,
    get_service_logs,
    get_service_metrics,
    run_diagnostic,
    analyze_incident,
]

# Write tools (require approval)
WRITE_TOOLS = [
    restart_service,
    scale_service,
    rollback_deployment,
    execute_runbook,
    create_incident,
]

# All tools
TOOLS = READ_ONLY_TOOLS + WRITE_TOOLS


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    def test_tools():
        """Test SRE tools."""
        print("=" * 60)
        print("Testing SRE Tools")
        print("=" * 60)

        print("\n1. List Services:")
        result = list_services.invoke({})
        print(result)

        print("\n2. Check Service Health (order-service):")
        result = check_service_health.invoke({"service_name": "order-service"})
        print(result)

        print("\n3. Get Service Logs (inventory-service):")
        result = get_service_logs.invoke({"service_name": "inventory-service", "log_level": LogLevel.ERROR, "hours_back": 3})
        print(result)

        print("\n4. Run Diagnostic (inventory-service):")
        result = run_diagnostic.invoke({"service_name": "inventory-service", "diagnostic_type": DiagnosticType.FULL})
        print(result)

        print("\n5. Analyze Incident:")
        result = analyze_incident.invoke({"affected_services": "order-service,inventory-service", "symptoms": "Slow checkout times and inventory errors"})
        print(result)

    test_tools()
