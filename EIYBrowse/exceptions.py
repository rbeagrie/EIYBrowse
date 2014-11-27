"""Defines a set of exceptions that can be raised by other
EIYBrowse modules.
"""


class NoFilesError(Exception):
    """Exception to be raised if no files could be found"""
    pass


class TooManyFilesError(Exception):
    """Exception to be raised if more than one file was found
    for a single chromosome.
    """
    pass


class InvalidChromError(Exception):
    """Exception to be raised if interactions are requested
    from a non-existing chromosome."""
    pass


class ImproperlyConfigured(Exception):

    """Exception to be raised when encountering configuration errors"""
    pass
