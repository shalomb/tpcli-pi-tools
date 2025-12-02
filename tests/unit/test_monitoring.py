"""Tests for monitoring and observability infrastructure."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tpcli_pi.core.monitoring import (
    HealthCheckResult,
    MonitoringService,
    OperationMetrics,
    OperationStatus,
    SyncOperation,
    get_monitoring_service,
)


class TestOperationMetrics:
    """Tests for OperationMetrics data class."""

    def test_create_operation_metrics(self):
        """Test creating operation metrics."""
        metrics = OperationMetrics(
            operation=SyncOperation.PULL,
            status=OperationStatus.SUCCESS,
            start_time=datetime.now(),
            team="Platform Eco",
            release="PI-4/25",
        )

        assert metrics.operation == SyncOperation.PULL
        assert metrics.status == OperationStatus.SUCCESS
        assert metrics.team == "Platform Eco"
        assert metrics.release == "PI-4/25"
        assert metrics.end_time is None

    def test_finalize_operation(self):
        """Test finalizing operation metrics."""
        start = datetime.now()
        metrics = OperationMetrics(
            operation=SyncOperation.PUSH,
            status=OperationStatus.FAILED,
            start_time=start,
        )

        metrics.finalize()

        assert metrics.end_time is not None
        assert metrics.duration_ms is not None
        assert metrics.duration_ms >= 0

    def test_metrics_to_dict(self):
        """Test converting metrics to dict."""
        metrics = OperationMetrics(
            operation=SyncOperation.INIT,
            status=OperationStatus.SUCCESS,
            start_time=datetime.now(),
            changes_count=5,
            conflict_count=0,
        )
        metrics.finalize()

        data = metrics.to_dict()

        assert data["operation"] == "init"
        assert data["status"] == "success"
        assert data["changes_count"] == 5
        assert "start_time" in data
        assert "end_time" in data


class TestHealthCheckResult:
    """Tests for HealthCheckResult."""

    def test_create_health_check(self):
        """Test creating health check result."""
        result = HealthCheckResult(
            name="api_connectivity",
            healthy=True,
            message="API is reachable",
        )

        assert result.name == "api_connectivity"
        assert result.healthy is True

    def test_health_check_to_dict(self):
        """Test converting health check to dict."""
        result = HealthCheckResult(
            name="git_repo",
            healthy=False,
            message="Repository not initialized",
            details={"repo_path": "/tmp/test"},
        )

        data = result.to_dict()

        assert data["name"] == "git_repo"
        assert data["healthy"] is False
        assert data["details"]["repo_path"] == "/tmp/test"


class TestMonitoringService:
    """Tests for MonitoringService."""

    @pytest.fixture
    def monitoring_service(self):
        """Create a monitoring service for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = MonitoringService(log_dir=Path(tmpdir))
            yield service

    def test_start_operation(self, monitoring_service):
        """Test starting operation tracking."""
        metrics = monitoring_service.start_operation(
            SyncOperation.PULL,
            team="Platform Eco",
            release="PI-4/25",
        )

        assert metrics.operation == SyncOperation.PULL
        assert metrics.team == "Platform Eco"
        assert metrics.release == "PI-4/25"
        assert metrics.status == OperationStatus.FAILED  # Initial status

    def test_end_operation_success(self, monitoring_service):
        """Test completing operation successfully."""
        metrics = monitoring_service.start_operation(SyncOperation.PUSH)
        metrics.changes_count = 10
        metrics.conflict_count = 0

        monitoring_service.end_operation(metrics, OperationStatus.SUCCESS)

        assert metrics.status == OperationStatus.SUCCESS
        assert metrics.end_time is not None
        assert metrics.duration_ms is not None

    def test_end_operation_with_error(self, monitoring_service):
        """Test completing operation with error."""
        metrics = monitoring_service.start_operation(SyncOperation.PULL)

        monitoring_service.end_operation(
            metrics,
            OperationStatus.FAILED,
            error_message="Network timeout",
        )

        assert metrics.status == OperationStatus.FAILED
        assert metrics.error_message == "Network timeout"

    def test_record_metrics(self, monitoring_service):
        """Test recording operation metrics."""
        metrics = monitoring_service.start_operation(SyncOperation.PUSH)

        monitoring_service.record_metrics(
            metrics,
            changes_count=15,
            conflicts=2,
            api_calls=30,
            git_ops=5,
        )

        assert metrics.changes_count == 15
        assert metrics.conflict_count == 2
        assert metrics.api_calls == 30
        assert metrics.git_operations == 5

    def test_health_check_success(self, monitoring_service):
        """Test registering health check that passes."""
        monitoring_service.register_health_check(
            "config_file",
            lambda: True,
            "Config file is readable",
        )

        health = monitoring_service.get_health_status()

        assert health["healthy_checks"] >= 1
        assert health["checks"]["config_file"]["healthy"] is True

    def test_health_check_failure(self, monitoring_service):
        """Test registering health check that fails."""
        monitoring_service.register_health_check(
            "api_token",
            lambda: False,
            "API token is invalid",
        )

        health = monitoring_service.get_health_status()

        assert health["checks"]["api_token"]["healthy"] is False
        assert "invalid" in health["checks"]["api_token"]["message"].lower()

    def test_health_check_exception(self, monitoring_service):
        """Test health check that raises exception."""

        def failing_check():
            raise RuntimeError("Check failed")

        monitoring_service.register_health_check(
            "database",
            failing_check,
            "Database connectivity",
        )

        health = monitoring_service.get_health_status()

        assert health["checks"]["database"]["healthy"] is False
        assert "Error" in health["checks"]["database"]["message"]

    def test_get_metrics_summary_empty(self, monitoring_service):
        """Test getting metrics summary with no operations."""
        summary = monitoring_service.get_metrics_summary()

        assert "message" in summary

    def test_get_metrics_summary(self, monitoring_service):
        """Test getting metrics summary with operations."""
        # Record several operations
        for i in range(3):
            metrics = monitoring_service.start_operation(
                SyncOperation.PULL,
                team=f"Team{i}",
            )
            metrics.changes_count = (i + 1) * 5
            metrics.conflict_count = i
            monitoring_service.end_operation(
                metrics,
                OperationStatus.SUCCESS if i % 2 == 0 else OperationStatus.FAILED,
            )

        summary = monitoring_service.get_metrics_summary(hours=24)

        assert summary["total_operations"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["success_rate"] > 0
        assert summary["avg_duration_ms"] >= 0

    def test_get_metrics_by_operation_type(self, monitoring_service):
        """Test filtering metrics by operation type."""
        # Record pull and push operations
        pull = monitoring_service.start_operation(SyncOperation.PULL)
        monitoring_service.end_operation(pull, OperationStatus.SUCCESS)

        push = monitoring_service.start_operation(SyncOperation.PUSH)
        monitoring_service.end_operation(push, OperationStatus.SUCCESS)

        pull_summary = monitoring_service.get_metrics_summary(
            hours=24, operation=SyncOperation.PULL
        )
        push_summary = monitoring_service.get_metrics_summary(
            hours=24, operation=SyncOperation.PUSH
        )

        assert pull_summary["total_operations"] == 1
        assert push_summary["total_operations"] == 1

    def test_conflicts_analysis(self, monitoring_service):
        """Test conflict analysis."""
        # Record operations with and without conflicts
        for i in range(5):
            metrics = monitoring_service.start_operation(SyncOperation.PULL)
            metrics.conflict_count = 2 if i < 3 else 0
            monitoring_service.end_operation(metrics, OperationStatus.SUCCESS)

        analysis = monitoring_service.get_conflicts_analysis(hours=24)

        assert analysis["total_operations"] == 5
        assert analysis["operations_with_conflicts"] == 3
        assert analysis["total_conflicts"] == 6
        assert analysis["conflict_rate"] == 60.0

    def test_export_metrics_json(self, monitoring_service):
        """Test exporting metrics to JSON."""
        metrics = monitoring_service.start_operation(
            SyncOperation.PUSH,
            team="Test Team",
        )
        metrics.changes_count = 5
        monitoring_service.end_operation(metrics, OperationStatus.SUCCESS)

        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "metrics.json"
            monitoring_service.export_metrics_json(export_path)

            assert export_path.exists()
            data = json.loads(export_path.read_text())

            assert "exported_at" in data
            assert "health_status" in data
            assert "summary_24h" in data
            assert len(data["all_operations"]) == 1

    def test_record_retry(self, monitoring_service):
        """Test recording retry attempts."""
        metrics = monitoring_service.start_operation(SyncOperation.PULL)

        monitoring_service.record_retry(metrics, 1, "Network timeout")

        assert metrics.retry_count == 1

    def test_log_error(self, monitoring_service):
        """Test logging errors."""
        error = RuntimeError("Test error")
        context = {"team": "Platform Eco", "operation": "sync"}

        # Should not raise
        monitoring_service.log_error(SyncOperation.PUSH, error, context)

    def test_singleton_instance(self):
        """Test that get_monitoring_service returns singleton."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service1 = get_monitoring_service(Path(tmpdir))
            service2 = get_monitoring_service()

            assert service1 is service2


class TestMonitoringIntegration:
    """Integration tests for monitoring service."""

    def test_complete_operation_workflow(self):
        """Test complete workflow of an operation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = MonitoringService(log_dir=Path(tmpdir))

            # Start operation
            metrics = service.start_operation(
                SyncOperation.PULL,
                team="Platform Eco",
                release="PI-4/25",
            )

            # Register health checks
            service.register_health_check(
                "config",
                lambda: True,
                "Config loaded",
            )
            service.register_health_check(
                "api",
                lambda: True,
                "API reachable",
            )

            # Record metrics
            service.record_metrics(
                metrics,
                changes_count=10,
                conflicts=1,
                api_calls=20,
                git_ops=5,
            )

            # Complete operation
            service.end_operation(metrics, OperationStatus.SUCCESS)

            # Verify
            summary = service.get_metrics_summary(hours=24)
            assert summary["total_operations"] == 1
            assert summary["successful"] == 1

            health = service.get_health_status()
            assert health["healthy_checks"] == 2

            # Export
            with tempfile.TemporaryDirectory() as export_dir:
                export_file = Path(export_dir) / "metrics.json"
                exported = service.export_metrics_json(export_file)

                data = json.loads(exported)
                assert data["summary_24h"]["total_operations"] == 1
