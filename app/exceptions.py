class UserExistsError(Exception):
    """Raised when trying to create a user that already exists."""


class NotFoundError(Exception):
    """Raised when an entity is not found in repository."""
