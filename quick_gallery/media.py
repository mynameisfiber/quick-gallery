import mimetypes
from pathlib import Path

mimetypes.add_type("image/jfif", ".jfif", strict=False)


class Media(Path):
    def __init__(self, host_file, public_file=None):
        self.public_file = Path(public_file or host_file)
        super().__init__(host_file)

    def mimetype(self) -> str | None:
        if not mimetypes.inited:
            mimetypes.init()
        mimetype, _ = mimetypes.guess_type(self, strict=False)
        return mimetype

    def media_type(self) -> str | None:
        if mimetype := self.mimetype():
            return mimetype.split("/", 1)[0]
        return None
