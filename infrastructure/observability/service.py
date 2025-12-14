"""
Observability service for the AI-driven learning platform.
Implements metrics, tracing, and logging for monitoring and debugging.
"""

import time
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import logging
from dataclasses import dataclass
from contextlib import contextmanager


class LogSeverity(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class LogEntry:
    """Represents a log entry."""
    timestamp: datetime
    level: LogSeverity
    message: str
    service: str
    trace_id: str
    span_id: str
    properties: Dict[str, Any]
    correlation_id: Optional[str] = None


@dataclass
class Metric:
    """Represents a metric."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    description: str = ""


class ObservabilityService:
    def __init__(self):
        self.logs: List[LogEntry] = []
        self.metrics: List[Metric] = []
        self.traces: Dict[str, List[Dict[str, Any]]] = {}
        self.max_logs = 10000  # Keep last 10k logs
        self.max_metrics = 5000  # Keep last 5k metrics
        self.logger = logging.getLogger(__name__)
        
        # Initialize standard metrics
        self.request_count = 0
        self.error_count = 0
        self.request_duration_sum = 0.0
        
    def log(self, level: LogSeverity, message: str, service: str = "unknown",
            trace_id: str = None, span_id: str = None, 
            correlation_id: str = None, **properties):
        """
        Log a message with specified severity.
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        if span_id is None:
            span_id = str(uuid.uuid4())
        
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            service=service,
            trace_id=trace_id,
            span_id=span_id,
            correlation_id=correlation_id,
            properties=properties
        )
        
        self.logs.append(log_entry)
        
        # Maintain log size limit
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        # Also log to Python's standard logging
        log_method = getattr(self.logger, level.value)
        log_method(f"[{service}] {message}", extra=properties)
    
    def info(self, message: str, service: str = "unknown", **properties):
        """Log an info message."""
        self.log(LogSeverity.INFO, message, service, **properties)
    
    def warning(self, message: str, service: str = "unknown", **properties):
        """Log a warning message."""
        self.log(LogSeverity.WARNING, message, service, **properties)
    
    def error(self, message: str, service: str = "unknown", **properties):
        """Log an error message."""
        self.log(LogSeverity.ERROR, message, service, **properties)
        self.error_count += 1
    
    def debug(self, message: str, service: str = "unknown", **properties):
        """Log a debug message."""
        self.log(LogSeverity.DEBUG, message, service, **properties)
    
    def critical(self, message: str, service: str = "unknown", **properties):
        """Log a critical message."""
        self.log(LogSeverity.CRITICAL, message, service, **properties)
    
    def record_metric(self, name: str, value: float, metric_type: MetricType,
                     labels: Dict[str, str] = None, description: str = ""):
        """
        Record a metric.
        """
        if labels is None:
            labels = {}
        
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels,
            timestamp=datetime.utcnow(),
            description=description
        )
        
        self.metrics.append(metric)
        
        # Maintain metric size limit
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        # Update standard metrics
        if name == "http_requests_total":
            self.request_count += 1
        elif name == "http_request_duration_seconds":
            self.request_duration_sum += value
    
    def increment_counter(self, name: str, labels: Dict[str, str] = None):
        """Increment a counter metric."""
        self.record_metric(name, 1, MetricType.COUNTER, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric."""
        self.record_metric(name, value, MetricType.GAUGE, labels)
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Observe a histogram metric."""
        self.record_metric(name, value, MetricType.HISTOGRAM, labels)
    
    def start_trace(self, operation_name: str, service: str = "unknown",
                   trace_id: str = None, **properties) -> str:
        """
        Start a new trace.
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        span_id = str(uuid.uuid4())
        
        trace_data = {
            "trace_id": trace_id,
            "span_id": span_id,
            "operation_name": operation_name,
            "service": service,
            "start_time": datetime.utcnow(),
            "properties": properties,
            "spans": []
        }
        
        self.traces[trace_id] = [trace_data]
        return trace_id
    
    def add_span(self, trace_id: str, operation_name: str, 
                start_time: datetime = None, end_time: datetime = None,
                **properties) -> str:
        """
        Add a span to an existing trace.
        """
        if trace_id not in self.traces:
            raise ValueError(f"Trace {trace_id} does not exist")
        
        span_id = str(uuid.uuid4())
        
        span_data = {
            "span_id": span_id,
            "operation_name": operation_name,
            "start_time": start_time or datetime.utcnow(),
            "end_time": end_time,
            "properties": properties
        }
        
        self.traces[trace_id].append(span_data)
        return span_id
    
    def end_trace(self, trace_id: str, **properties):
        """
        End a trace and add final properties.
        """
        if trace_id not in self.traces:
            raise ValueError(f"Trace {trace_id} does not exist")
        
        # Update the root span with end time and properties
        root_span = self.traces[trace_id][0]
        root_span["end_time"] = datetime.utcnow()
        root_span["properties"].update(properties)
    
    @contextmanager
    def trace_operation(self, operation_name: str, service: str = "unknown", **properties):
        """
        Context manager for tracing operations.
        """
        trace_id = self.start_trace(operation_name, service, **properties)
        start_time = time.time()
        
        try:
            yield trace_id
        except Exception as e:
            self.error(f"Error in operation {operation_name}: {str(e)}", service, trace_id=trace_id)
            raise
        finally:
            duration = time.time() - start_time
            self.end_trace(trace_id, duration=duration, **properties)
            self.observe_histogram("operation_duration_seconds", duration, 
                                 {"operation": operation_name, "service": service})
    
    def get_logs(self, service: str = None, level: LogSeverity = None, 
                limit: int = 100, start_time: datetime = None) -> List[LogEntry]:
        """
        Get logs with optional filtering.
        """
        filtered_logs = self.logs[-limit:]  # Get recent logs
        
        if service:
            filtered_logs = [log for log in filtered_logs if log.service == service]
        
        if level:
            filtered_logs = [log for log in filtered_logs if log.level == level]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs if log.timestamp >= start_time]
        
        return filtered_logs
    
    def get_metrics(self, name: str = None, label_filters: Dict[str, str] = None,
                   start_time: datetime = None) -> List[Metric]:
        """
        Get metrics with optional filtering.
        """
        filtered_metrics = self.metrics
        
        if name:
            filtered_metrics = [metric for metric in filtered_metrics if metric.name == name]
        
        if label_filters:
            filtered_metrics = [
                metric for metric in filtered_metrics
                if all(metric.labels.get(key) == value for key, value in label_filters.items())
            ]
        
        if start_time:
            filtered_metrics = [metric for metric in filtered_metrics if metric.timestamp >= start_time]
        
        return filtered_metrics
    
    def get_traces(self, operation_name: str = None, service: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get traces with optional filtering.
        """
        filtered_traces = {}
        
        for trace_id, trace_data in self.traces.items():
            # Check if the trace matches filters
            root_span = trace_data[0]
            if operation_name and root_span["operation_name"] != operation_name:
                continue
            if service and root_span["service"] != service:
                continue
            
            filtered_traces[trace_id] = trace_data
        
        return filtered_traces
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health metrics.
        """
        return {
            "timestamp": datetime.utcnow(),
            "status": "healthy",
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "uptime_seconds": self.get_uptime(),
            "active_traces": len(self.traces),
            "log_count": len(self.logs),
            "metric_count": len(self.metrics)
        }
    
    def get_uptime(self) -> float:
        """
        Get system uptime in seconds.
        """
        # In a real implementation, this would track when the system started
        # For now, return a placeholder
        return 3600.0  # 1 hour placeholder
    
    def export_logs_json(self) -> str:
        """
        Export logs in JSON format.
        """
        logs_data = []
        for log in self.logs:
            logs_data.append({
                "timestamp": log.timestamp.isoformat(),
                "level": log.level.value,
                "message": log.message,
                "service": log.service,
                "trace_id": log.trace_id,
                "span_id": log.span_id,
                "correlation_id": log.correlation_id,
                "properties": log.properties
            })
        
        return json.dumps(logs_data, default=str)
    
    def export_metrics_json(self) -> str:
        """
        Export metrics in JSON format.
        """
        metrics_data = []
        for metric in self.metrics:
            metrics_data.append({
                "name": metric.name,
                "type": metric.type.value,
                "value": metric.value,
                "labels": metric.labels,
                "timestamp": metric.timestamp.isoformat(),
                "description": metric.description
            })
        
        return json.dumps(metrics_data, default=str)


class ObservabilityMiddleware:
    """
    Middleware for automatic observability.
    """
    def __init__(self, observability_service: ObservabilityService):
        self.observability_service = observability_service
    
    def instrument_request(self, func: Callable) -> Callable:
        """
        Decorator to instrument request handling with observability.
        """
        def wrapper(*args, **kwargs):
            with self.observability_service.trace_operation(
                f"request_{func.__name__}", 
                "api", 
                endpoint=func.__name__,
                args=str(args),
                kwargs=str(kwargs)
            ) as trace_id:
                # Add request counter
                self.observability_service.increment_counter(
                    "http_requests_total", 
                    {"endpoint": func.__name__, "method": "GET"}
                )
                
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Record success metrics
                    duration = time.time() - start_time
                    self.observability_service.observe_histogram(
                        "http_request_duration_seconds",
                        duration,
                        {"endpoint": func.__name__, "status": "success"}
                    )
                    
                    return result
                except Exception as e:
                    # Record error metrics
                    duration = time.time() - start_time
                    self.observability_service.observe_histogram(
                        "http_request_duration_seconds",
                        duration,
                        {"endpoint": func.__name__, "status": "error"}
                    )
                    
                    self.observability_service.increment_counter(
                        "http_requests_errors_total",
                        {"endpoint": func.__name__, "error_type": type(e).__name__}
                    )
                    
                    self.observability_service.error(
                        f"Request failed: {str(e)}",
                        "api",
                        trace_id=trace_id,
                        endpoint=func.__name__,
                        error=str(e)
                    )
                    
                    raise
        
        return wrapper


# Global observability service instance
observability_service = ObservabilityService()