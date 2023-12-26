import logging
import os

log = logging.getLogger(__name__)


class EnvVar:
    """Environment variable definition."""

    def __init__(self, default_value: str, desc: str, name: str = "NOT_SET"):
        self.name = name  # gets set later
        self.default_value = default_value
        self.desc = desc

    def log_debug(self) -> None:
        """Log the name=value of this environment variable."""
        log.debug(f"{self.name}={self.value}")

    @property
    def value(self) -> str:
        """Return the value of the environment variable."""
        return os.getenv(self.name, self.default_value)
