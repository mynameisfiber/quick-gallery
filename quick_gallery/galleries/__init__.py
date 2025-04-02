from .base_gallery import BaseGallery
from .simple_gallery import SimpleGallery
from .tag_gallery import TagGallery


default_gallery = SimpleGallery
galleries = [TagGallery, SimpleGallery]
