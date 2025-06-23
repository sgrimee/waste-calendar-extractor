"""Type stubs for ics module."""

from typing import Any, Optional, Union
from datetime import date, datetime
from .event import Event as Event

class Calendar:
    """iCal Calendar class."""
    
    def __init__(self, content: Optional[str] = None) -> None: ...
    
    @property
    def events(self) -> "EventSet": ...
    
    def serialize(self) -> str: ...
    
    @classmethod
    def parse_multiple(cls, content: str) -> list["Calendar"]: ...
    
    def clone(self) -> "Calendar": ...

class EventSet:
    """Container for calendar events."""
    
    def add(self, event: Event) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...

class Attendee:
    """iCal Attendee class."""
    pass

class AudioAlarm:
    """iCal AudioAlarm class."""
    pass

class DisplayAlarm:
    """iCal DisplayAlarm class."""
    pass

class Geo:
    """iCal Geo class."""
    pass

class Organizer:
    """iCal Organizer class."""
    pass

class Todo:
    """iCal Todo class."""
    pass

# Module exports
__all__ = [
    "Calendar",
    "Event", 
    "Attendee",
    "AudioAlarm",
    "DisplayAlarm",
    "Geo",
    "Organizer",
    "Todo",
]