import sys
import os
import hashlib
from pathlib import Path
from collections import abc

import click

from . import galleries
from .server import AioHttpServer
from .media import Media


GALLERY_LOOKUP = {g.name: g for g in galleries.galleries}


def resolve_files(
    paths, recursive=False, public_path_fxn=lambda x: None
) -> abc.Iterable[Media]:
    for path in paths:
        if recursive and path.is_dir():
            yield from resolve_files(
                path.iterdir(), recursive=recursive, public_path_fxn=public_path_fxn
            )
        elif path == Path("-"):
            paths_stdin = (Path(line.strip()) for line in sys.stdin)
            yield from resolve_files(
                paths_stdin, recursive=recursive, public_path_fxn=public_path_fxn
            )
        else:
            yield Media(path, public_file=public_path_fxn(path))


@click.group()
def cli():
    pass


@cli.command()
@click.option("--recursive", is_flag=True, default=False)
@click.option("--output", type=click.File(mode="wt+"), default="-")
@click.option("--debug", is_flag=True, default=False)
@click.option(
    "--gallery",
    "gallery_name",
    type=click.Choice(list(GALLERY_LOOKUP.keys()), case_sensitive=False),
    default=galleries.default_gallery.name,
)
@click.argument("media", type=click.Path(path_type=Path, allow_dash=True), nargs=-1)
def static(recursive, gallery_name, output, media, debug):
    if debug:
        logfile = sys.stderr
    else:
        logfile = open(os.devnull, "w")
    medias = resolve_files(media, recursive=recursive)
    GalleryType = GALLERY_LOOKUP[gallery_name]
    gallery = GalleryType(medias)
    output.write(gallery.html())


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", type=int, default=8000)
@click.option("--recursive", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.option(
    "--gallery",
    "gallery_name",
    type=click.Choice(list(GALLERY_LOOKUP.keys()), case_sensitive=False),
    default=galleries.default_gallery.name,
)
@click.argument("media", type=click.Path(path_type=Path, allow_dash=True), nargs=-1)
def serve(host, port, gallery_name, recursive, media, debug):
    if debug:
        logfile = sys.stderr
    else:
        logfile = open(os.devnull, "w")
    medias = list(
        resolve_files(
            media,
            recursive=recursive,
            public_path_fxn=lambda p: "media/"
            + hashlib.md5(str(p).encode("utf8")).hexdigest(),
        )
    )
    GalleryType = GALLERY_LOOKUP[gallery_name]
    gallery = GalleryType(medias)
    server = AioHttpServer(host, port, gallery, medias)
    server.start()


def main():
    cli(auto_envvar_prefix="QUICK_GALLERY_")


if __name__ == "__main__":
    main()
