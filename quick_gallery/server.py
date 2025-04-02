from collections import abc
import logging

from aiohttp import web

from .media import Media
from .galleries import BaseGallery


logger = logging.getLogger(__name__)


class AioHttpServer:
    def __init__(
        self, host: str, port: int, gallery: BaseGallery, medias: abc.Iterable[Media]
    ):
        self.host = host
        self.port = port
        self.gallery = gallery
        self.gallery_html = gallery.html()
        self.media_lookup: dict[str, Media] = {
            self.media_path(media): media for media in medias
        }
        self.app = web.Application()
        self.app.router.add_get("/", self.handle_root)

        for path in self.media_lookup.keys():
            self.app.router.add_get(path, self.handle_static)

    @classmethod
    def media_path(cls, media: Media):
        return str("/" / media.public_file)

    async def handle_root(self, request):
        return web.Response(text=self.gallery_html, content_type="text/html")

    async def handle_static(self, request):
        media = self.media_lookup.get(request.path)
        if media and media.is_file():
            print(f"Request for media {request.path}")
            return web.FileResponse(media)
        return web.Response(status=404, text="404: Not Found")

    def start(self):
        web.run_app(self.app, host=self.host, port=self.port)
