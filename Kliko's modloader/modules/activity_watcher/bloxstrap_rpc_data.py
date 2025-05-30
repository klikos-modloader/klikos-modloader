from typing import Optional
from dataclasses import dataclass


@dataclass
class BloxstrapRPCImage:
    source: Optional[str] = None
    hover_text: Optional[str] = None
    clear: bool = False
    reset: bool = False


@dataclass
class BloxstrapRPCData:
    start: Optional[int] = None
    end: Optional[int] = None
    details: Optional[str] = None
    state: Optional[str] = None
    large_image: Optional[BloxstrapRPCImage] = None
    small_image: Optional[BloxstrapRPCImage] = None