"""Tests for error recovery and resilience infrastructure."""

import pytest
from unittest.mock import Mock

from tpcli_pi.core.resilience import (
    APIRateLimitHandler,
    NetworkError,
    PartialFailureHandler,
    RateLimitError,
    RecoverableError,
    RetryConfig,
    RetryStrategy,
    RetryableOperation,
    TemporaryError,
)


class TestRetryConfig:
    """Tests for retry configuration."""

    def test_default_retry_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_exponential_backoff(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL)
        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0

    def test_linear_backoff(self):
        """Test linear backoff calculation."""
        config = RetryConfig(base_delay=2.0, strategy=RetryStrategy.LINEAR)
        assert config.get_delay(0) == 2.0
        assert config.get_delay(1) == 4.0
        assert config.get_delay(2) == 6.0

    def test_fixed_delay(self):
        """Test fixed delay."""
        config = RetryConfig(base_delay=3.0, strategy=RetryStrategy.FIXED)
        assert config.get_delay(0) == 3.0
        assert config.get_delay(1) == 3.0
        assert config.get_delay(2) == 3.0

    def test_max_delay_enforced(self):
        """Test that maximum delay is enforced."""
        config = RetryConfig(base_delay=1.0, max_delay=5.0)
        assert config.get_delay(0) == 1.0
        assert config.get_delay(5) == 5.0  # Capped at max_delay


class TestRetryableOperation:
    """Tests for retryable operations."""

    def test_successful_operation_no_retry(self):
        """Test successful operation without retries."""
        fn = Mock(return_value="success")
        op = RetryableOperation("test", fn)
        result = op.execute()

        assert result == "success"
        assert op.attempts == 0
        fn.assert_called_once()

    def test_operation_succeeds_after_retry(self):
        """Test operation that succeeds after one retry."""
        fn = Mock(side_effect=[
            RecoverableError("Temporary failure"),
            "success"
        ])
        op = RetryableOperation("test", fn)
        result = op.execute()

        assert result == "success"
        assert op.attempts == 1
        assert fn.call_count == 2

    def test_operation_fails_non_recoverable(self):
        """Test that non-recoverable errors are not retried."""
        fn = Mock(side_effect=ValueError("Permanent failure"))
        op = RetryableOperation("test", fn)

        with pytest.raises(ValueError):
            op.execute()

        assert op.attempts == 1
        fn.assert_called_once()

    def test_operation_exhausts_retries(self):
        """Test operation that exhausts all retries."""
        fn = Mock(side_effect=RecoverableError("Always fails"))
        config = RetryConfig(max_attempts=3)
        op = RetryableOperation("test", fn, config)

        with pytest.raises(RecoverableError):
            op.execute()

        assert op.attempts == 3
        assert fn.call_count == 3

    def test_custom_recovery_check(self):
        """Test custom recovery check function."""
        fn = Mock(side_effect=ValueError("Custom error"))
        
        def is_recoverable(e):
            return isinstance(e, ValueError)
        
        op = RetryableOperation("test", fn, is_recoverable=is_recoverable)
        
        with pytest.raises(ValueError):
            op.execute()

        assert op.attempts == 3

    def test_rate_limit_error_handling(self):
        """Test handling of rate limit errors."""
        fn = Mock(side_effect=RateLimitError(retry_after=1))
        config = RetryConfig(max_attempts=2)
        op = RetryableOperation("test", fn, config)

        with pytest.raises(RateLimitError):
            op.execute()

        assert op.attempts == 2


class TestRecoverableErrors:
    """Tests for error types."""

    def test_recoverable_error(self):
        """Test RecoverableError."""
        error = RecoverableError("test")
        assert isinstance(error, Exception)

    def test_temporary_error(self):
        """Test TemporaryError."""
        error = TemporaryError("temporary")
        assert isinstance(error, RecoverableError)

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("timeout")
        assert isinstance(error, TemporaryError)

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError(retry_after=30)
        assert error.retry_after == 30
        assert isinstance(error, RecoverableError)


class TestPartialFailureHandler:
    """Tests for partial failure handling."""

    def test_record_success(self):
        """Test recording successful operation."""
        handler = PartialFailureHandler()
        handler.record_success("op1", "result1")

        assert handler.success_count == 1
        assert handler.failure_count == 0

    def test_record_failure(self):
        """Test recording failed operation."""
        handler = PartialFailureHandler()
        error = ValueError("test")
        handler.record_failure("op1", error)

        assert handler.success_count == 0
        assert handler.failure_count == 1

    def test_mixed_results(self):
        """Test mixed success and failure."""
        handler = PartialFailureHandler()
        handler.record_success("op1", "result1")
        handler.record_failure("op2", ValueError("error"))
        handler.record_success("op3", "result3")

        assert handler.success_count == 2
        assert handler.failure_count == 1
        assert handler.total_count == 3

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        handler = PartialFailureHandler()
        handler.record_success("op1", "result1")
        handler.record_failure("op2", ValueError("error"))

        assert handler.success_rate == 50.0

    def test_is_partial_success(self):
        """Test partial success detection."""
        handler = PartialFailureHandler()
        assert not handler.is_partial_success

        handler.record_success("op1", "result1")
        assert not handler.is_partial_success

        handler.record_failure("op2", ValueError("error"))
        assert handler.is_partial_success

    def test_get_summary(self):
        """Test getting summary."""
        handler = PartialFailureHandler()
        handler.record_success("op1", "result1")
        handler.record_failure("op2", ValueError("error"))
        handler.record_failure("op3", ValueError("another"))

        summary = handler.get_summary()

        assert summary["successful"] == 1
        assert summary["failed"] == 2
        assert summary["total"] == 3
        assert summary["success_rate"] == 1/3 * 100


class TestAPIRateLimitHandler:
    """Tests for API rate limit handling."""

    def test_record_request(self):
        """Test recording requests."""
        handler = APIRateLimitHandler(requests_per_minute=10)
        handler.record_request()
        handler.record_request()

        assert len(handler.request_times) == 2

    def test_requests_remaining(self):
        """Test calculating requests remaining."""
        handler = APIRateLimitHandler(requests_per_minute=5)
        handler.record_request()
        handler.record_request()

        remaining = handler.get_requests_remaining()
        assert remaining == 3

    def test_rate_limit_exceeded(self):
        """Test that rate limit error is raised."""
        handler = APIRateLimitHandler(requests_per_minute=2)
        handler.record_request()
        handler.record_request()

        with pytest.raises(RateLimitError):
            handler.check_rate_limit()

    def test_get_status(self):
        """Test getting rate limit status."""
        handler = APIRateLimitHandler(requests_per_minute=10)
        handler.record_request()
        handler.record_request()

        status = handler.get_status()

        assert status["requests_remaining"] == 8
        assert status["requests_limit"] == 10
        assert status["requests_made"] == 2

