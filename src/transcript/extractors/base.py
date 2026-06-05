# src/transcript/extractors/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Segment:
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    segments: list[Segment]
    language: str  # "zh" | "en" | "auto"
    source_type: str  # "youtube" | "bilibili" | "local"

    @property
    def full_text(self) -> str:
        return "\n".join(s.text for s in self.segments)

    def to_dict(self) -> dict:
        return {
            "segments": [
                {"start": s.start, "end": s.end, "text": s.text}
                for s in self.segments
            ],
            "language": self.language,
            "source_type": self.source_type,
        }


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, input_path: str, **kwargs) -> Transcript:
        """Extract transcript from the given input."""

    @abstractmethod
    def supports(self, input_path: str) -> bool:
        """Return True if this extractor can handle the input."""
