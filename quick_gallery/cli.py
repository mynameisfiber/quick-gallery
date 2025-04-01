import sys
import os
import asyncio
import hashlib
from pathlib import Path
from collections import abc

import click

from .create_gallery import generate_gallery
from .server import AioHttpServer
from .media import Media


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
@click.argument("media", type=click.Path(path_type=Path, allow_dash=True), nargs=-1)
def static(recursive, output, media, debug):
    if debug:
        logfile = sys.stderr
    else:
        logfile = open(os.devnull, "w")
    medias = resolve_files(media, recursive=recursive)
    gallery = generate_gallery(medias, log=logfile)
    output.write(gallery)


@cli.command()
@click.option("--host", default="0.0.0.0")
@click.option("--port", type=int, default=8000)
@click.option("--recursive", is_flag=True, default=False)
@click.option("--debug", is_flag=True, default=False)
@click.argument("media", type=click.Path(path_type=Path, allow_dash=True), nargs=-1)
def serve(host, port, recursive, media, debug):
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
    gallery = generate_gallery(medias, log=logfile)
    server = AioHttpServer(host, port, gallery, medias)
    server.start()


def main():
    cli(auto_envvar_prefix="QUICK_GALLERY_")


if __name__ == "__main__":
    main()
