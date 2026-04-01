# -*- coding: utf-8 -*-
# Debug module - centralized debug logging and state management

import os
import logging


class Debug:
    """Centralized debug state and logging management"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Debug state from environment
        self._enabled = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

        # Get logger
        self._logger = logging.getLogger('detector')

    @property
    def enabled(self) -> bool:
        """Check if debug mode is enabled"""
        # Check environment variable each time to allow runtime toggling
        return os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')

    @enabled.setter
    def enabled(self, value: bool):
        """Set debug mode state"""
        self._enabled = value
        os.environ['DEBUG'] = '1' if value else '0'

    def enable(self):
        """Enable debug mode"""
        self.enabled = True

    def disable(self):
        """Disable debug mode"""
        self.enabled = False

    def toggle(self):
        """Toggle debug mode"""
        self.enabled = not self.enabled
        return self.enabled

    # Convenience methods for logging
    def debug(self, msg):
        """Log debug message (only when debug mode is enabled)"""
        if self.enabled:
            self._logger.debug(msg)

    def info(self, msg):
        """Log info message (always logged)"""
        self._logger.info(msg)

    def warning(self, msg):
        """Log warning message"""
        self._logger.warning(msg)

    def error(self, msg):
        """Log error message"""
        self._logger.error(msg)


# Global singleton instance
debug = Debug()


# Module-level convenience functions
def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return debug.enabled


def set_debug_enabled(enabled: bool):
    """Set debug mode state"""
    debug.enabled = enabled


def debug_print(msg):
    """Print debug messages (only in debug mode)"""
    debug.debug(msg)


def info_print(msg):
    """Log info messages (always logged)"""
    debug.info(msg)
