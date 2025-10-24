"""
Security module for NEOC AI Assistant
Implements input validation, rate limiting, and security measures
"""

import hashlib
import logging
import re
import time
from collections import defaultdict
from functools import wraps
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation with security checks"""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"data:",  # Data URLs
        r"vbscript:",  # VBScript
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>.*?</iframe>",  # Iframes
        r"<object[^>]*>.*?</object>",  # Objects
        r"<embed[^>]*>.*?</embed>",  # Embeds
        r"union\s+select",  # SQL injection
        r";\s*drop\s+table",  # SQL injection
        r"--",  # SQL comments
        r"/\*.*\*/",  # SQL comments
    ]

    def __init__(self, max_length: int = 1000):
        self.max_length = max_length
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.DANGEROUS_PATTERNS
        ]

    def validate_text(self, text: str) -> Tuple[bool, str]:
        """Validate text input for security issues - O(n) time"""
        if not text or not isinstance(text, str):
            return False, "Input must be a non-empty string"

        # Length check - O(1)
        if len(text) > self.max_length:
            return False, f"Input too long (max {self.max_length} characters)"

        # Check for dangerous patterns - O(n)
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                logger.warning(
                    f"Dangerous pattern detected in input: {pattern.pattern}"
                )
                return False, "Input contains potentially dangerous content"

        # Check for excessive special characters
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if special_chars / len(text) > 0.5:
            return False, "Input contains too many special characters"

        return True, "Valid"

    def sanitize_text(self, text: str) -> str:
        """Sanitize text by removing dangerous content - O(n)"""
        # Remove script tags and similar
        for pattern in self.compiled_patterns:
            text = pattern.sub("", text)

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text.strip())

        return text


class RateLimiter:
    """Token bucket rate limiter for API protection"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60.0
        self.tokens_per_second = self.requests_per_second

        # In-memory storage (use Redis in production)
        self.buckets: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.last_cleanup = time.time()

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed - O(1)"""
        current_time = time.time()

        # Periodic cleanup of old entries
        if current_time - self.last_cleanup > 300:  # 5 minutes
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time

        # Get or create bucket for client
        bucket = self.buckets[client_id]

        # Refill tokens based on time passed
        time_passed = current_time - bucket.get("last_time", current_time)
        bucket["last_time"] = current_time

        # Calculate tokens to add
        tokens_to_add = time_passed * self.tokens_per_second
        bucket["tokens"] = min(
            bucket.get("tokens", self.requests_per_minute) + tokens_to_add,
            self.requests_per_minute,
        )

        # Check if we have enough tokens
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True

        return False

    def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up old entries to prevent memory leaks - O(n)"""
        cutoff_time = current_time - 3600  # 1 hour
        clients_to_remove = []

        for client_id, bucket in self.buckets.items():
            if bucket.get("last_time", 0) < cutoff_time:
                clients_to_remove.append(client_id)

        for client_id in clients_to_remove:
            del self.buckets[client_id]

        if clients_to_remove:
            logger.info(f"Cleaned up {len(clients_to_remove)} old rate limit entries")


class SecurityManager:
    """Main security manager coordinating all security measures"""

    def __init__(self, config):
        self.validator = InputValidator(max_length=config.security.max_input_length)
        self.rate_limiter = RateLimiter(config.security.max_requests_per_minute)
        self.config = config

        # Request tracking for analytics
        self.request_log: List[Dict] = []
        self.max_log_entries = 1000

    def validate_request(
        self, text: str, client_id: str = "anonymous"
    ) -> Tuple[bool, str]:
        """Validate a complete request - O(n)"""
        # Rate limiting check - O(1)
        if self.config.security.enable_rate_limiting:
            if not self.rate_limiter.is_allowed(client_id):
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                return False, "Rate limit exceeded. Please try again later."

        # Input validation - O(n)
        if self.config.security.enable_input_validation:
            is_valid, message = self.validator.validate_text(text)
            if not is_valid:
                self._log_security_event("invalid_input", client_id, text[:100])
                return False, message

        # Log successful request
        self._log_request(client_id, "valid_request")

        return True, "Request validated"

    def sanitize_input(self, text: str) -> str:
        """Sanitize input text"""
        return self.validator.sanitize_text(text)

    def _log_security_event(
        self, event_type: str, client_id: str, details: str
    ) -> None:
        """Log security events - O(1) amortized"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "client_id": client_id,
            "details": details,
        }

        self.request_log.append(event)

        # Maintain log size
        if len(self.request_log) > self.max_log_entries:
            self.request_log.pop(0)

        logger.warning(f"Security event: {event_type} from {client_id}")

    def _log_request(self, client_id: str, event_type: str) -> None:
        """Log normal requests for analytics - O(1) amortized"""
        if len(self.request_log) >= self.max_log_entries:
            self.request_log.pop(0)

        self.request_log.append(
            {"timestamp": time.time(), "event_type": event_type, "client_id": client_id}
        )

    def get_security_stats(self) -> Dict:
        """Get security statistics - O(n)"""
        total_requests = len(self.request_log)
        if total_requests == 0:
            return {"total_requests": 0}

        # Calculate stats
        event_counts = defaultdict(int)
        recent_events = [
            e for e in self.request_log if time.time() - e["timestamp"] < 3600
        ]  # Last hour

        for event in recent_events:
            event_counts[event["event_type"]] += 1

        return {
            "total_requests": total_requests,
            "recent_requests": len(recent_events),
            "event_counts": dict(event_counts),
            "rate_limit_violations": event_counts.get("rate_limit_exceeded", 0),
            "invalid_inputs": event_counts.get("invalid_input", 0),
        }


def require_security_validation(func):
    """Decorator to add security validation to API endpoints"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract request data (this would be adapted for FastAPI)
        request_data = kwargs.get("request_data", {})

        # Get security manager from global state
        if security_manager is None:
            return {"success": False, "error": "Security manager not initialized"}

        # Validate request
        text = request_data.get("message", "")
        client_id = request_data.get("client_id", "anonymous")

        is_valid, message = security_manager.validate_request(text, client_id)
        if not is_valid:
            return {"success": False, "error": message}

        # Sanitize input
        request_data["message"] = security_manager.sanitize_input(text)

        # Call original function
        return await func(*args, **kwargs)

    return wrapper


# Global security manager instance
security_manager = None


def init_security_manager(config):
    """Initialize global security manager"""
    global security_manager
    security_manager = SecurityManager(config)
    logger.info("Security manager initialized")
