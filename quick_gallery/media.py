import mimetypes
from pathlib import Path
from typing import List

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

    def tags(self) -> set:
        tags = set([self.media_type()])
        for tag_file in self.tag_files():
            if tag_file.exists():
                tags.update(tag.lower() for tag in tag_file.read_text().splitlines())
        return tags

    def tag_files(self) -> List[Path]:
        base = self.stem
        pattern = f"{base}-*.tags"
        return list(self.parent.glob(pattern))
