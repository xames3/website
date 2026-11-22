"""\
Banner
======

Author: Akshay Mestry <xa@mes3.dev>
Created on: 22 November 2026
Last updated on: 22 November 2026

The banner of a page: a picture, or a gradient in a shade with the icon
of the page. The byline sets it above the title, and the cards of the
related pages show it.
"""

from __future__ import annotations

import os
import os.path as p
import typing as t

from sphinx.util.osutil import copyfile

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.settings import stored
from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

SHADES: t.Final[tuple[str, ...]] = (
    "blue",
    "indigo",
    "purple",
    "red",
    "orange",
    "yellow",
    "green",
    "teal",
    "graphite",
)
SHADE: t.Final[str] = "blue"
FOLDER: t.Final[str] = "_images/km-banners"


class Banner(t.NamedTuple):
    """The banner of a page, as its byline sets it."""

    shade: str = SHADE
    icon: str = ""
    picture: str = ""
    hidden: bool = False

    @property
    def local(self) -> bool:
        """Whether the picture is a file of the source of the site."""
        return bool(self.picture) and "://" not in self.picture

    def titled(self, glyph: str, style: str | None = None) -> Banner:
        """Use the icon of the title when the byline gives none.

        :param glyph: The classes of the first icon of the title.
        :param style: The style to draw it in, as `light` or
            `duotone regular`, or `None` to keep its own. `duotone`
            alone is `duotone solid`. A brand keeps its own.
        :return: The banner with an icon, or the same banner.
        """
        if self.icon or not glyph:
            return self
        icon = [
            each
            for each in glyph.split()
            if each != "km-glyph" and not checks.MODIFIERS.fullmatch(each)
        ]
        if style and "fa-brands" not in icon:
            families = [_ for _ in icon if _ in checks.FAMILIES]
            rest = [
                _ for _ in icon if _ not in checks.FAMILIES | checks.STYLES
            ]
            family, _, weight = style.rpartition(" ")
            if weight == "duotone":
                family, weight = weight, "solid"
            if family:
                families = [f"fa-{family}"]
            icon = [*families, f"fa-{weight}", *rest]
        return self._replace(icon=" ".join(icon))

    def linked(self, pathto: Callable[..., str]) -> Banner:
        """Write the picture as a page links it.

        :param pathto: The `pathto` of the context of the page.
        :return: The banner, with a path from the page to the picture.
        """
        if not self.local:
            return self
        return self._replace(picture=pathto(f"{FOLDER}/{self.picture}", 1))


def source(env: BuildEnvironment, written: str) -> str:
    """Find the file of a picture in the source of the site.

    :param env: The build environment, on the page that names it.
    :param written: The path, relative to the page, or to the source
        directory when it starts with a `/`.
    :return: The path from the source directory, with `/` between
        folders.
    :raises ValueError: For a file outside the source directory, or a
        file that is not there.
    """
    relative, path = env.relfn2path(written, env.docname)
    root = p.realpath(env.srcdir)
    if p.commonpath([p.realpath(path), root]) != root:
        raise ValueError(
            f"expected a file inside the source directory, got {written!r}"
        )
    if not p.isfile(path):
        raise ValueError(f"expected a file that is there, got {written!r}")
    env.note_dependency(relative)
    return relative.replace(p.sep, "/")


def title_style(config: Config) -> str | None:
    """Find the style of the icons that banners take from titles.

    :param config: The Sphinx configuration.
    :return: `kaamiki.conf.byline.icon_style` with a kit, or `None`
        without one, since Font Awesome Free has no light or thin
        icons and the title keeps its own.
    """
    if not Icons.of(config).kit:
        return None
    return str(values(config).byline.icon_style)


def banners(env: BuildEnvironment) -> dict[str, Banner]:
    """Hold the banner of each page that has a byline.

    :param env: The build environment.
    :return: The banners, by document name.
    """
    return stored(env, "banners", {})


def banner(env: BuildEnvironment, docname: str, glyph: str = "") -> Banner:
    """Find the banner of a page.

    :param env: The build environment.
    :param docname: The page.
    :param glyph: The classes of the first icon of its title.
    :return: The banner of its byline, else a banner in `SHADE`. The
        icon of the title, in `title_style`, fills a banner without an
        icon.
    """
    found = banners(env).get(docname, Banner())
    return found.titled(glyph, title_style(env.config))


@on("build-finished")
def copy_banners(app: Sphinx, exception: Exception | None) -> None:
    """Copy the picture files of the banners into the build.

    :param app: The Sphinx application instance.
    :param exception: The error that stopped the build, or `None`.
    """
    if exception or app.builder.format != "html":
        return
    for found in banners(app.env).values():
        if found.local:
            target = p.join(app.outdir, FOLDER, found.picture)
            os.makedirs(p.dirname(target), exist_ok=True)
            copyfile(p.join(app.srcdir, found.picture), target)


@on("env-purge-doc")
def forget_banner(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Forget the banner of a page when it is read again or removed.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docname: The page that is read again.
    """
    del app
    banners(env).pop(docname, None)


@on("env-merge-info")
def merge_banners(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: set[str],
    other: BuildEnvironment,
) -> None:
    """Take the banners that a parallel reader found.

    :param app: The Sphinx application instance.
    :param env: The build environment.
    :param docnames: The pages that the reader read.
    :param other: The build environment of the reader.
    """
    del app
    banners(env).update(
        {
            name: found
            for name, found in banners(other).items()
            if name in docnames
        }
    )
