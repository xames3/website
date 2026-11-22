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

import typing as t

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils.hooks import on
from kaamiki.extensions.utils.settings import stored

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
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


class Banner(t.NamedTuple):
    """The banner of a page, as its byline sets it."""

    shade: str = SHADE
    icon: str = ""
    picture: str = ""
    hidden: bool = False

    def titled(self, glyph: str) -> Banner:
        """Use the icon of the title when the byline gives none.

        :param glyph: The classes of the first icon of the title.
        :return: The banner with an icon, or the same banner.
        """
        if self.icon or not glyph:
            return self
        icon = [
            each
            for each in glyph.split()
            if each != "km-glyph" and not checks.MODIFIERS.fullmatch(each)
        ]
        return self._replace(icon=" ".join(icon))

    def linked(self, pathto: Callable[..., str]) -> Banner:
        """Write the picture as a page links it.

        :param pathto: The `pathto` of the context of the page.
        :return: The banner, with a path from the page to the picture.
        """
        if not self.picture:
            return self
        return self._replace(picture=pathto(self.picture.lstrip("/"), 1))


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
        icon of the title fills a banner without an icon.
    """
    return banners(env).get(docname, Banner()).titled(glyph)


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
