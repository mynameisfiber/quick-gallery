from collections import abc

from ..media import Media


class BaseGallery:
    def __init__(self, medias: abc.Iterable[Media]):
        self.medias = medias

    def gallery_items(self) -> abc.Sequence[str]:
        raise NotImplementedError()

    def html(self):
        raise NotImplementedError()

    @classmethod
    @property
    def name(cls):
        return cls.__name__
