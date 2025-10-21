# core/endpoints.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoint:
    """
    A blueprint for a location within a Fusebox-based SIS.

    This is a simple data structure that defines a destination for the client.
    Concrete instances of this class should be defined in the application
    (e.g., in a 'grades' app), not in the core framework.
    """
    fuseaction: str