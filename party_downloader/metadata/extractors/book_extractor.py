from abc import ABC, abstractmethod, abstractproperty
from typing import Literal
from party_downloader.metadata.raw_tag import RawTag


class BookExtractor(ABC):
    """Base class for book metadata extractors."""

    def __init__(self, webdata: WebData):
        self.webdata = webdata

    @abstractproperty
    def id(self) -> str:
        """The ID of the book."""
        pass

    def title(self) -> str:
        """The title of the book."""
        pass

    def other_titles(self) -> list[str]:
        """Alternative titles of the book."""
        pass

    def type(self) -> Literal["manga", "novel", "light_novel", "web_novel", "other"]:
        """The type of book."""
        pass

    def region(self) -> str:
        """The region of origin"""
        pass
