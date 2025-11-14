from pathlib import Path
from typing import List, Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

@dataclass
class MediaConfig:
    '''
    Media organization config options
    '''
    source_directory: Path | None = None
    date_regex: str | None = None
    subfolder: str = "media"
    operation: Literal["move", "copy"] = "copy"
    extensions: List[str] = Field(default_factory=lambda: [".png", ".jpg", ".jpeg", ".gif", ".webp"])
    enabled: bool = False
