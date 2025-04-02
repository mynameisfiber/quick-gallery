from collections import abc

from ..media import Media


class BaseGallery:
    def __init__(self, medias: abc.Iterable[Media]):
        self.medias = medias

    def html(self):
        raise NotImplementedError()

    @classmethod
    @property
    def name(cls):
        return cls.__name__
