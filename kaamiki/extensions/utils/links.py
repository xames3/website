"""\
Link Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 08 October 2026
Last updated on: 16 November 2026

The helpers that find where a link goes. `REL` is the `rel` of each
link that opens in a new tab. `noopener` stops the new tab from
reaching back into this tab, and `noreferrer` stops it from seeing the
page that the reader came from.

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel
"""

from __future__ import annotations

import re
import typing as t
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlsplit

from sphinx.util.osutil import relative_uri

from kaamiki.extensions.utils.settings import values

if t.TYPE_CHECKING:
    from collections.abc import Iterable

    from sphinx.config import Config
    from sphinx.writers.html import HTMLTranslator

REL: t.Final[str] = "noopener noreferrer"
SLASHES: t.Final[re.Pattern[str]] = re.compile(r"^/{2,}")
YOUTUBE_ID: t.Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9_-]{11}")
YOUTUBE_START: t.Final[re.Pattern[str]] = re.compile(
    r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?"
)
YOUTUBE_HOSTS: t.Final[frozenset[str]] = frozenset(
    {"youtube.com", "youtube-nocookie.com", "music.youtube.com"}
)
YOUTUBE_PATHS: t.Final[frozenset[str]] = frozenset(
    {"embed", "live", "shorts", "v"}
)


def youtube_id(url: str) -> str | None:
    """Find the video id in a YouTube link.

    :param url: The link, as written: a watch, `youtu.be`, `embed`,
        `shorts`, `live` or `v` link, or only an id. A link must be
        `http` or `https`, and a link that urllib cannot read has no
        id.
    :return: The id of eleven characters, or `None` when there is none.
    """
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return None
    if parts.scheme not in ("", "http", "https"):
        return None
    host = (parts.hostname or "").removeprefix("www.").removeprefix("m.")
    segments = [_ for _ in parts.path.split("/") if _]
    found = ""
    if (not host and len(segments) == 1) or (host == "youtu.be" and segments):
        found = segments[0]
    elif host in YOUTUBE_HOSTS and segments[:1] == ["watch"]:
        found = parse_qs(parts.query).get("v", [""])[0]
    elif host in YOUTUBE_HOSTS and len(segments) > 1:
        found = segments[1] if segments[0] in YOUTUBE_PATHS else ""
    return found if YOUTUBE_ID.fullmatch(found) else None


def youtube_still(vid: str) -> str:
    """Name the address of the picture of a video.

    :param vid: The video id of eleven characters.
    :return: The address of the picture of the video on YouTube.
    """
    return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"


def youtube_start(url: str) -> int | None:
    """Find the second where a YouTube link starts.

    :param url: The link, as written. A link copied at the current time
        has `t=42`, `t=42s` or `t=1h2m3s`, and an embed link has
        `start=42`.
    :return: The seconds, or `None` when the link has none.
    """
    try:
        query = parse_qs(urlsplit(url.strip()).query)
    except ValueError:
        return None
    for key in ("t", "start"):
        found = YOUTUBE_START.fullmatch(query.get(key, [""])[0])
        if found and any(found.groups()):
            hours, minutes, seconds = (int(_ or 0) for _ in found.groups())
            return hours * 3600 + minutes * 60 + seconds
    return None


def hostnames(entries: Iterable[str], *, www: bool = False) -> set[str]:
    """Read the host names out of a list a site wrote.

    :param entries: The entries, each a host or an address.
    :param www: Keep a leading `www.`, which is dropped otherwise.
    :return: The host names, in lowercase.
    """
    found: set[str] = set()
    for entry in entries:
        text = entry.strip()
        try:
            name = urlsplit(text if "//" in text else f"//{text}").hostname
        except ValueError:
            continue
        if name:
            found.add(name if www else name.removeprefix("www."))
    return found


def hosts(config: Config) -> set[str]:
    """Name the hosts that count as the site itself.

    :param config: The Sphinx configuration.
    :return: The host in `html_baseurl` and the ones in
        `kaamiki.conf.links.internal_hosts`, lowercase and without
        `www.`.
    """
    return hostnames([config.html_baseurl]) | hostnames(
        values(config).links.internal_hosts
    )


def elsewhere(url: str, own: t.Collection[str]) -> bool:
    """Say whether a link goes to a different site.

    :param url: The link, as written.
    :param own: The hosts of the site, as `hosts` gives them.
    :return: `True` for a host that is not of the site, without `www.`.
        A browser reads a backslash as a slash, so a link with two
        backslashes at the start goes to a different site, as with
        `//`. A link that urllib cannot read stays on the site.
    """
    text = SLASHES.sub("//", url.strip().replace("\\", "/"))
    try:
        host = urlsplit(text).hostname
    except ValueError:
        return False
    if not host:
        return False
    return host.removeprefix("www.") not in own


def guarded(rel: str | None) -> str:
    """Add the words a link that opens in a new tab needs to its `rel`.

    :param rel: What the link says in `rel`, as written.
    :return: Those words and `REL`'s, each once.
    """
    return " ".join(dict.fromkeys([*(rel or "").split(), *REL.split()]))


def opens_new_tab(url: str, config: Config) -> bool:
    """Say whether a link opens in a new tab.

    :param url: The link, as written.
    :param config: The Sphinx configuration.
    :return: `True` for a link that gets `target="_blank"`: it goes to
        a different site, not in `kaamiki.conf.links.internal_hosts`,
        and `kaamiki.conf.links.new_tab` is not off.
    """
    if not values(config).links.new_tab:
        return False
    return elsewhere(url, hosts(config))


def relative_to_page(translator: HTMLTranslator, url: str) -> str:
    """Make the path of an option work from its page.

    :param translator: The HTML translator that writes the page.
    :param url: The path or the address, as written.
    :return: The address, relative to the page when it was a path.
    """
    if not url or urlsplit(url).scheme or url.startswith(("//", "#", "?")):
        return url
    builder = translator.builder
    page = builder.get_target_uri(builder.current_docname)
    return relative_uri(page, url.lstrip("/"))


def absolute(url: str, home: str) -> str:
    """Make an address absolute for the site.

    :param url: The address, as written. A path starts at the root of
        the site, so `_static/cover.png` is the same picture on each
        page.
    :param home: The `html_baseurl` of the site. Without it, the
        address does not change.
    :return: The address, absolute where possible.
    """
    if not url or not home or urlsplit(url).scheme:
        return url
    return home.rstrip("/") + "/" + quote(url.lstrip("/"), safe="/%?=&#:")
