from dataclasses import dataclass
from party_downloader.models.metadata.raw_tag import RawTag


@dataclass
class VideoMetadata:
    id: str
    title: str
    description: str
    producer: str
    publisher: str
    studio: str
    series: str
    actors: list[str]
    tags: list[RawTag]
