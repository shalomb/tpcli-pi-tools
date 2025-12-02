"""Monitoring and observability infrastructure for tpcli PI planning system.

Provides:
- Sync operation metrics (latency, success rate, conflicts)
- Health checks and diagnostics
- Performance monitoring
- Error tracking and logging
- Integration with observability tools (extensible)
"""

import json
import logging
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Dict, List, Optional


# ===== Enums & Data Models =====

class SyncOperation(Enum):
    """Types of sync operations."""

    PULL = "pull"
    PUSH = "push"
    INIT = "init"
    STATUS = "status"


class OperationStatus(Enum):
    """Result status of an operation."""

    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"  # e.g., some teams succeeded, some failed
    CONFLICT = "conflict"  # conflicts detected but handled


@dataclass
class OperationMetrics:
    """Metrics for a single sync operation."""

    operation: SyncOperation
    status: OperationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    team: Optional[str] = None
    release: Optional[str] = None
    changes_count: int = 0
    conflict_count: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    api_calls: int = 0
    git_operations: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling datetime serialization."""
        data = asdict(self)
        data["operation"] = self.operation.value
        data["status"] = self.status.value
        data["start_time"] = self.start_time.isoformat()
        if self.end_time:
            data["end_time"] = self.end_time.isoformat()
        return data

    def finalize(self) -> None:
        """Mark operation as complete and calculate duration."""
        self.end_time = datetime.now()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    healthy: bool
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "healthy": self.healthy,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


# ===== Monitoring Service =====

class MonitoringService:
    """Central monitoring service for tpcli operations."""

    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize monitoring service.

        Args:
            log_dir: Directory to store monitoring logs (default: ~/.local/share/tpcli/logs)
        """
        self.log_dir = log_dir or Path.home() / ".local" / "share" / "tpcli" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = self._setup_logger()

        # Metrics storage
        self._metrics_lock = Lock()
        self._operation_metrics: List[OperationMetrics] = []
        self._health_checks: Dict[str, HealthCheckResult] = {}

        # Performance tracking
        self._operation_start_times: Dict[str, float] = {}

    def _setup_logger(self) -> logging.Logger:
        """Set up logging infrastructure."""
        logger = logging.getLogger("tpcli_pi")
        logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(self.log_dir / "tpcli.log")
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    # ===== Operation Tracking =====

    def start_operation(
        self,
        operation: SyncOperation,
        team: Optional[str] = None,
        release: Optional[str] = None,
    ) -> OperationMetrics:
        """Start tracking an operation.

        Args:
            operation: Type of operation
            team: Team being synced (optional)
            release: Release being synced (optional)

        Returns:
            OperationMetrics object for this operation
        """
        metrics = OperationMetrics(
            operation=operation,
            status=OperationStatus.FAILED,  # Optimistic: update on completion
            start_time=datetime.now(),
            team=team,
            release=release,
        )

        self.logger.info(
            f"Starting {operation.value} for {team or 'all'} / {release or 'all'}"
        )

        return metrics

    def end_operation(
        self,
        metrics: OperationMetrics,
        status: OperationStatus,
        error_message: Optional[str] = None,
    ) -> None:
        """Complete tracking an operation.

        Args:
            metrics: OperationMetrics from start_operation
            status: Final status of operation
            error_message: Error message if failed
        """
        metrics.finalize()
        metrics.status = status
        metrics.error_message = error_message

        with self._metrics_lock:
            self._operation_metrics.append(metrics)

        level = (
            logging.ERROR if status == OperationStatus.FAILED else logging.INFO
        )
        self.logger.log(
            level,
            f"Completed {metrics.operation.value}: {status.value} "
            f"({metrics.duration_ms:.0f}ms) - "
            f"Changes: {metrics.changes_count}, Conflicts: {metrics.conflict_count}",
        )

    def record_metrics(
        self,
        metrics: OperationMetrics,
        changes_count: int = 0,
        conflicts: int = 0,
        api_calls: int = 0,
        git_ops: int = 0,
    ) -> None:
        """Record operation metrics.

        Args:
            metrics: OperationMetrics object
            changes_count: Number of changes processed
            conflicts: Number of conflicts detected
            api_calls: Number of API calls made
            git_ops: Number of git operations performed
        """
        metrics.changes_count = changes_count
        metrics.conflict_count = conflicts
        metrics.api_calls = api_calls
        metrics.git_operations = git_ops

    # ===== Health Checks =====

    def register_health_check(
        self, name: str, check_fn: Callable[[], bool], description: str = ""
    ) -> None:
        """Register a health check function.

        Args:
            name: Name of health check
            check_fn: Function that returns True if healthy
            description: Description of what this checks
        """
        try:
            is_healthy = check_fn()
            result = HealthCheckResult(
                name=name,
                healthy=is_healthy,
                message=description,
            )
            with self._metrics_lock:
                self._health_checks[name] = result
            self.logger.info(f"Health check '{name}': {'PASS' if is_healthy else 'FAIL'}")
        except Exception as e:
            result = HealthCheckResult(
                name=name,
                healthy=False,
                message=f"{description} - Error: {str(e)}",
            )
            with self._metrics_lock:
                self._health_checks[name] = result
            self.logger.error(f"Health check '{name}' failed: {str(e)}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status.

        Returns:
            Dict with health status and details
        """
        with self._metrics_lock:
            checks = self._health_checks.copy()

        healthy_count = sum(1 for c in checks.values() if c.healthy)
        total_count = len(checks)

        return {
            "overall_healthy": healthy_count == total_count,
            "healthy_checks": healthy_count,
            "total_checks": total_count,
            "checks": {name: result.to_dict() for name, result in checks.items()},
        }

    # ===== Metrics Analysis =====

    def get_metrics_summary(
        self, hours: int = 24, operation: Optional[SyncOperation] = None
    ) -> Dict[str, Any]:
        """Get summary of recent metrics.

        Args:
            hours: Look back this many hours
            operation: Filter to specific operation type (optional)

        Returns:
            Dict with metrics summary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._metrics_lock:
            recent_metrics = [
                m for m in self._operation_metrics if m.start_time >= cutoff_time
            ]

        if operation:
            recent_metrics = [m for m in recent_metrics if m.operation == operation]

        if not recent_metrics:
            return {"message": f"No metrics in last {hours} hours"}

        # Calculate statistics
        successful = sum(1 for m in recent_metrics if m.status == OperationStatus.SUCCESS)
        failed = sum(1 for m in recent_metrics if m.status == OperationStatus.FAILED)
        conflicts = sum(m.conflict_count for m in recent_metrics)
        changes = sum(m.changes_count for m in recent_metrics)
        durations = [m.duration_ms for m in recent_metrics if m.duration_ms]

        return {
            "period_hours": hours,
            "total_operations": len(recent_metrics),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(recent_metrics)) * 100
            if recent_metrics
            else 0,
            "conflicts_detected": conflicts,
            "changes_processed": changes,
            "avg_duration_ms": sum(durations) / len(durations) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
        }

    def get_conflicts_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze conflict patterns.

        Args:
            hours: Look back this many hours

        Returns:
            Dict with conflict analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._metrics_lock:
            recent_metrics = [
                m for m in self._operation_metrics if m.start_time >= cutoff_time
            ]

        total_ops = len(recent_metrics)
        ops_with_conflicts = sum(1 for m in recent_metrics if m.conflict_count > 0)
        total_conflicts = sum(m.conflict_count for m in recent_metrics)

        # By operation type
        by_type = defaultdict(lambda: {"count": 0, "conflicts": 0})
        for m in recent_metrics:
            by_type[m.operation.value]["count"] += 1
            by_type[m.operation.value]["conflicts"] += m.conflict_count

        return {
            "period_hours": hours,
            "total_operations": total_ops,
            "operations_with_conflicts": ops_with_conflicts,
            "conflict_rate": (ops_with_conflicts / total_ops * 100) if total_ops else 0,
            "total_conflicts": total_conflicts,
            "avg_conflicts_per_op": (
                total_conflicts / total_ops if total_ops else 0
            ),
            "by_operation_type": dict(by_type),
        }

    # ===== Export & Persistence =====

    def export_metrics_json(self, filepath: Optional[Path] = None) -> str:
        """Export metrics to JSON file.

        Args:
            filepath: Path to save JSON (default: logs/metrics.json)

        Returns:
            JSON string
        """
        if not filepath:
            filepath = self.log_dir / "metrics.json"

        with self._metrics_lock:
            data = {
                "exported_at": datetime.now().isoformat(),
                "health_status": self.get_health_status(),
                "summary_24h": self.get_metrics_summary(hours=24),
                "conflicts_24h": self.get_conflicts_analysis(hours=24),
                "all_operations": [m.to_dict() for m in self._operation_metrics],
            }

        filepath.write_text(json.dumps(data, indent=2))
        self.logger.info(f"Metrics exported to {filepath}")

        return json.dumps(data, indent=2)

    # ===== Retry & Error Tracking =====

    def record_retry(
        self, metrics: OperationMetrics, retry_count: int, reason: str
    ) -> None:
        """Record a retry attempt.

        Args:
            metrics: OperationMetrics for the operation
            retry_count: Current retry number
            reason: Reason for retry
        """
        metrics.retry_count = retry_count
        self.logger.warning(
            f"Retry {retry_count} for {metrics.operation.value}: {reason}"
        )

    def log_error(
        self, operation: SyncOperation, error: Exception, context: Optional[Dict] = None
    ) -> None:
        """Log an operation error.

        Args:
            operation: Operation that failed
            error: Exception that occurred
            context: Additional context (optional)
        """
        context_str = f" - {json.dumps(context)}" if context else ""
        self.logger.error(
            f"Error in {operation.value}: {type(error).__name__}: {str(error)}{context_str}"
        )


# ===== Singleton Instance =====

_monitoring_service: Optional[MonitoringService] = None


def get_monitoring_service(log_dir: Optional[Path] = None) -> MonitoringService:
    """Get or create the singleton monitoring service.

    Args:
        log_dir: Directory for logs (only used on first call)

    Returns:
        MonitoringService instance
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService(log_dir)
    return _monitoring_service
