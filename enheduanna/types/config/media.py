from pathlib import Path
from typing import List, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

@dataclass
class MediaSource:
    '''
    Configuration for a single media source folder
    '''
    folder: Path
    operation: Literal["move", "copy"] = "copy"
    subfolder: str = "media"

@dataclass
class MediaConfig:
    '''
    Media organization config options
    '''
    sources: List[MediaSource] = Field(default_factory=list)
    extensions: List[str] = Field(default_factory=lambda: [".png", ".jpg", ".jpeg", ".gif", ".webp"])
    enabled: bool = False
