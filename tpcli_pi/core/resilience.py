"""Error recovery and resilience infrastructure for tpcli.

Provides:
- Retry logic with exponential backoff
- Partial failure handling
- API rate limit handling
- Graceful degradation
- Error recovery strategies
"""

import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from tpcli_pi.core.monitoring import get_monitoring_service

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategies for operations."""

    EXPONENTIAL = "exponential"  # 2^attempt
    LINEAR = "linear"  # attempt * base_delay
    FIXED = "fixed"  # constant delay


class RecoverableError(Exception):
    """Base exception for recoverable errors."""

    pass


class RateLimitError(RecoverableError):
    """Raised when API rate limit is hit."""

    def __init__(self, retry_after: int = 60):
        """Initialize rate limit error.

        Args:
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")


class TemporaryError(RecoverableError):
    """Raised for temporary/transient errors."""

    pass


class NetworkError(TemporaryError):
    """Network-related error (timeout, connection refused, etc)."""

    pass


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        backoff_multiplier: float = 2.0,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            strategy: Retry strategy to use
            backoff_multiplier: Multiplier for exponential backoff
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.backoff_multiplier = backoff_multiplier

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        if self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.base_delay * (self.backoff_multiplier ** attempt)
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay * (attempt + 1)
        else:  # FIXED
            delay = self.base_delay

        return min(delay, self.max_delay)


class RetryableOperation:
    """Wrapper for operations that support retries."""

    def __init__(
        self,
        operation_name: str,
        operation_fn: Callable[[], T],
        config: Optional[RetryConfig] = None,
        is_recoverable: Optional[Callable[[Exception], bool]] = None,
    ):
        """Initialize retryable operation.

        Args:
            operation_name: Name of operation (for logging)
            operation_fn: Function to execute
            config: Retry configuration (default: standard config)
            is_recoverable: Function to determine if exception is recoverable
        """
        self.operation_name = operation_name
        self.operation_fn = operation_fn
        self.config = config or RetryConfig()
        self.is_recoverable = is_recoverable or self._default_is_recoverable
        self.attempts = 0
        self.last_error: Optional[Exception] = None

    @staticmethod
    def _default_is_recoverable(error: Exception) -> bool:
        """Default recovery check - checks exception type."""
        return isinstance(error, RecoverableError)

    def execute(self) -> T:
        """Execute operation with retry logic.

        Returns:
            Result of operation

        Raises:
            Exception: If all retries exhausted
        """
        self.attempts = 0

        while self.attempts < self.config.max_attempts:
            try:
                logger.debug(
                    f"Executing {self.operation_name} (attempt {self.attempts + 1}/{self.config.max_attempts})"
                )
                result = self.operation_fn()
                if self.attempts > 0:
                    logger.info(f"{self.operation_name} succeeded after {self.attempts} retries")
                return result

            except Exception as e:
                self.last_error = e
                self.attempts += 1

                if not self.is_recoverable(e):
                    logger.error(f"{self.operation_name} failed with non-recoverable error: {e}")
                    raise

                if self.attempts >= self.config.max_attempts:
                    logger.error(
                        f"{self.operation_name} failed after {self.attempts} attempts: {e}"
                    )
                    raise

                # Calculate delay
                if isinstance(e, RateLimitError):
                    delay = e.retry_after
                else:
                    delay = self.config.get_delay(self.attempts - 1)

                logger.warning(
                    f"{self.operation_name} failed (attempt {self.attempts}): {e}. "
                    f"Retrying in {delay}s..."
                )

                # Record in monitoring (optional - only if available)
                try:
                    monitoring = get_monitoring_service()
                    monitoring.record_retry(
                        metrics=None,  # Would be passed in for real monitoring
                        retry_count=self.attempts,
                        reason=str(e),
                    )
                except Exception:
                    pass  # Monitoring failure shouldn't block retry

                time.sleep(delay)

        raise self.last_error


class PartialFailureHandler:
    """Handles partial failures across multiple operations."""

    def __init__(self):
        """Initialize partial failure handler."""
        self.successful: list[tuple[str, Any]] = []
        self.failed: list[tuple[str, Exception]] = []
        self.errors_by_type: dict[type, list[Exception]] = {}

    def record_success(self, operation_id: str, result: Any) -> None:
        """Record successful operation.

        Args:
            operation_id: Identifier for operation
            result: Result of operation
        """
        self.successful.append((operation_id, result))

    def record_failure(self, operation_id: str, error: Exception) -> None:
        """Record failed operation.

        Args:
            operation_id: Identifier for operation
            error: Exception that occurred
        """
        self.failed.append((operation_id, error))

        error_type = type(error)
        if error_type not in self.errors_by_type:
            self.errors_by_type[error_type] = []
        self.errors_by_type[error_type].append(error)

    @property
    def success_count(self) -> int:
        """Get number of successful operations."""
        return len(self.successful)

    @property
    def failure_count(self) -> int:
        """Get number of failed operations."""
        return len(self.failed)

    @property
    def total_count(self) -> int:
        """Get total number of operations."""
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        """Get success rate (0-100)."""
        if self.total_count == 0:
            return 100.0
        return (self.success_count / self.total_count) * 100

    @property
    def is_partial_success(self) -> bool:
        """Check if there were both successes and failures."""
        return self.success_count > 0 and self.failure_count > 0

    def get_summary(self) -> dict[str, Any]:
        """Get summary of partial failure results.

        Returns:
            Dict with summary statistics
        """
        return {
            "successful": self.success_count,
            "failed": self.failure_count,
            "total": self.total_count,
            "success_rate": self.success_rate,
            "is_partial_success": self.is_partial_success,
            "failed_operations": [op_id for op_id, _ in self.failed],
            "errors_by_type": {
                error_type.__name__: len(errors)
                for error_type, errors in self.errors_by_type.items()
            },
        }


class APIRateLimitHandler:
    """Handles API rate limiting gracefully."""

    def __init__(self, requests_per_minute: int = 60):
        """Initialize rate limit handler.

        Args:
            requests_per_minute: Expected rate limit
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: list[float] = []
        self.current_window_start: float = time.time()

    def check_rate_limit(self) -> None:
        """Check if we're within rate limits.

        Raises:
            RateLimitError: If rate limit would be exceeded
        """
        now = time.time()
        window_duration = 60.0  # 1 minute window

        # Remove old requests outside window
        self.request_times = [
            t for t in self.request_times if now - t < window_duration
        ]

        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = self.request_times[0]
            wait_time = int(window_duration - (now - oldest_request)) + 1
            raise RateLimitError(retry_after=wait_time)

    def record_request(self) -> None:
        """Record that a request was made."""
        self.request_times.append(time.time())

    def get_requests_remaining(self) -> int:
        """Get number of requests remaining in current window.

        Returns:
            Number of requests still available
        """
        now = time.time()
        window_duration = 60.0
        self.request_times = [
            t for t in self.request_times if now - t < window_duration
        ]
        return max(0, self.requests_per_minute - len(self.request_times))

    def get_status(self) -> dict[str, Any]:
        """Get rate limit status.

        Returns:
            Dict with current status
        """
        return {
            "requests_remaining": self.get_requests_remaining(),
            "requests_limit": self.requests_per_minute,
            "requests_made": len(self.request_times),
        }
