"""\
Link Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 15 October 2026

The helpers that work out where a link goes.
"""

import re
import typing as t
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlsplit

from sphinx.util.osutil import relative_uri

from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from sphinx.config import Config
    from sphinx.writers.html import HTMLTranslator

# NOTE(xames3): What every link that opens in a new tab says in `rel`.
# `noopener` keeps the new tab from reaching back into this one and
# `noreferrer` keeps it from seeing which page the reader came from.
REL: t.Final[str] = "noopener noreferrer"
YOUTUBE_ID: re.Pattern[str] = re.compile(r"[A-Za-z0-9_-]{11}")
# HACK(xames3): Surprisingly, got this idea while installing an
# AdBlocker and these domains were already configured in them.
YOUTUBE_HOSTS: t.Final[frozenset[str]] = frozenset(
    {"youtube.com", "youtube-nocookie.com", "music.youtube.com"}
)
YOUTUBE_PATHS: t.Final[frozenset[str]] = frozenset(
    {"embed", "live", "shorts", "v"}
)


def youtube_id(url: str) -> str | None:
    """Find the video id in a YouTube link.

    Watch, `youtu.be`, `embed`, `shorts`, `live` and `v` links work, as
    does a bare id.

    :param url: The link, as written.
    :return: The eleven character id or `None` when there isn't one.
    """
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.").removeprefix("m.")
    segments = [_ for _ in parts.path.split("/") if _]
    found = ""
    if (not host and len(segments) == 1) or (host == "youtu.be" and segments):
        found = segments[0]
    elif host in YOUTUBE_HOSTS and segments[:1] == ["watch"]:
        found = parse_qs(parts.query).get("v", [""])[0]
    elif host in YOUTUBE_HOSTS and len(segments) > 1:
        found = segments[1] if segments[0] in YOUTUBE_PATHS else ""
    return found if YOUTUBE_ID.fullmatch(found) else None


def hostnames(entries: Iterable[str], *, www: bool = False) -> set[str]:
    """Read the host names out of a list a site wrote.

    :param entries: The entries, each a host or an address.
    :param www: Keep a leading `www.`, which is dropped otherwise.
    :return: The host names, in lowercase.
    """
    found: set[str] = set()
    for entry in entries:
        text = entry.strip()
        name = urlsplit(text if "//" in text else f"//{text}").hostname
        if name:
            found.add(name if www else name.removeprefix("www."))
    return found


def hosts(config: Config) -> set[str]:
    """Name the hosts that count as the site itself.

    :param config: The Sphinx configuration.
    :return: The host in `html_baseurl` and the ones in
        `internal_hosts`, lowercase and without `www.`.
    """
    return hostnames([config.html_baseurl]) | hostnames(
        setting(config, "internal_hosts")
    )


def elsewhere(url: str, own: t.Collection[str]) -> bool:
    """Say whether a link leaves the site.

    Only a host other than the site's own counts, `www.` aside.

    :param url: The link, as written.
    :param own: The site's own hosts, as `hosts` returns them.
    :return: Whether the link goes to another site.
    """
    host = urlsplit(url).hostname
    if not host:
        return False
    return host.removeprefix("www.") not in own


def opens_new_tab(url: str, config: Config) -> bool:
    """Say whether a link should open in a new tab.

    It has to leave the site, `internal_hosts` aside, and
    `open_links_in_new_tab` mustn't be off.

    :param url: The link, as written.
    :param config: The Sphinx configuration.
    :return: Whether the link gets `target="_blank"`.
    """
    if not setting(config, "open_links_in_new_tab"):
        return False
    return elsewhere(url, hosts(config))


def rooted(translator: HTMLTranslator, url: str) -> str:
    """Make a path written in an option an address that works from the
    page it is on.

    A path counts from the top of the site, with or without a leading
    `/`, so `_static/cover.png` is the same picture from every page and
    from a site under a sub-path. A full address, a `//` one and a
    `data:` one are left as written.

    :param translator: The HTML translator writing the page.
    :param url: The path or address, as written.
    :return: The address, relative to the page where it was a path.
    """
    if not url or urlsplit(url).scheme or url.startswith(("//", "#", "?")):
        return url
    builder = translator.builder
    page = builder.get_target_uri(builder.current_docname)
    return relative_uri(page, url.lstrip("/"))


def absolute(url: str, home: str) -> str:
    """Make an address absolute against the site's own.

    A path counts from the site root, so `_static/cover.png` is the
    same picture on every page. Without `html_baseurl` it's left as
    written.

    :param url: The address, as written.
    :param home: The site's `html_baseurl`.
    :return: The address, absolute where it can be.
    """
    if not url or not home or urlsplit(url).scheme:
        return url
    if url.startswith("//"):
        return f"{urlsplit(home).scheme}:{url}"
    return home.rstrip("/") + "/" + quote(url.lstrip("/"), safe="/%?=&#:")
