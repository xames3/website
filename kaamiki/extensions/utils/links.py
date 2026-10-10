"""\
Link Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 09 October 2026

The helpers that work out where a link goes.
"""

from __future__ import annotations

import re
import typing as t
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlsplit

from kaamiki.extensions.utils.settings import setting

if t.TYPE_CHECKING:
    from sphinx.config import Config

YOUTUBE_ID: re.Pattern[str] = re.compile(r"^[\w-]{11}$")
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
    return found if YOUTUBE_ID.match(found) else None


def hostnames(entries: object, *, www: bool = False) -> set[str]:
    """Read the host names out of a list a site wrote.

    :param entries: A list of entries or one entry as a string.
    :param www: Keep a leading `www.`, which is dropped otherwise.
    :return: The host names, in lowercase.
    """
    if isinstance(entries, str):
        entries = [entries]
    found: set[str] = set()
    for entry in t.cast("t.Iterable[object]", entries or ()):
        text = str(entry).strip()
        if not text:
            continue
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
    return hostnames(config.html_baseurl) | hostnames(
        setting(config, "internal_hosts")
    )


def elsewhere(url: str, own: t.Collection[str]) -> bool:
    """Say whether a link leaves the site.

    Only a host other than the site's own counts, `www.` aside.

    :param url: The link, as written.
    :param own: The site's own hosts, as `hosts` returns them.
    :return: Whether the link goes to another site.
    """
    try:
        host = urlsplit(url).hostname
    except ValueError:
        return True
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
    if not config.html_context.get("km_open_links_in_new_tab", True):
        return False
    return elsewhere(url, hosts(config))


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
