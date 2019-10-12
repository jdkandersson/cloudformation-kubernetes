"""Custom exceptions that can be raised."""


class ParentError(Exception):
    """Parent of all custom exceptions."""


class ApiVersionMissingError(ParentError):
    """The apiVersion is missing."""

    def __init__(self):
        """Construct."""
        super().__init__("apiVersion is required.")


class KindMissingError(ParentError):
    """The kind is missing."""

    def __init__(self):
        """Construct."""
        super().__init__("kind is required.")
