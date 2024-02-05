from dataclasses import dataclass
from urllib.parse import urlparse, unquote


@dataclass
class DownloadMetadatum:
    """Dataclass that contains the full set of information necessary to perform a download"""

    path: str
    filetype: str
    key: tuple
    filename: str = None
    raw_filename: str = None

    def __post_init__(self):
        parsed = urlparse(self.path)
        _, fn = parsed.query.split("=")
        self.raw_filename = fn
        # Convert from %C3 to proper characters
        self.filename = unquote(fn)
