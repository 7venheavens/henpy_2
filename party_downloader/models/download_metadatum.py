@dataclass
class DownloadMetadatum:
    path: str
    target_dir: str
    filetype: str
    key: tuple
    filename: str = None

    def __post_init__(self):
        parsed = urlparse(self.path)
        _, fn = parsed.query.split("=")
        self.filename = fn
