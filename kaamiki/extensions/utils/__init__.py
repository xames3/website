"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 12 October 2026

Kaamiki's shared helpers, now as its own module.
"""

from __future__ import annotations

from kaamiki.extensions.utils import writer
from kaamiki.extensions.utils.build import build_finished
from kaamiki.extensions.utils.build import hidden
from kaamiki.extensions.utils.build import not_found
from kaamiki.extensions.utils.build import root_urls
from kaamiki.extensions.utils.build import sitemap
from kaamiki.extensions.utils.context import context_defaults
from kaamiki.extensions.utils.context import feedback
from kaamiki.extensions.utils.context import page_switches
from kaamiki.extensions.utils.dates import committed
from kaamiki.extensions.utils.dates import dated
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.dates import header
from kaamiki.extensions.utils.dates import provenance
from kaamiki.extensions.utils.dates import updated_on
from kaamiki.extensions.utils.dates import written
from kaamiki.extensions.utils.directives import depart
from kaamiki.extensions.utils.directives import fields
from kaamiki.extensions.utils.directives import listed
from kaamiki.extensions.utils.directives import parse
from kaamiki.extensions.utils.directives import phrase
from kaamiki.extensions.utils.directives import seconds
from kaamiki.extensions.utils.directives import skip
from kaamiki.extensions.utils.directives import toggle
from kaamiki.extensions.utils.directives import trail
from kaamiki.extensions.utils.directives import visitor
from kaamiki.extensions.utils.doctree import badged
from kaamiki.extensions.utils.doctree import buried
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.doctree import offer
from kaamiki.extensions.utils.doctree import standfirst
from kaamiki.extensions.utils.doctree import summarise
from kaamiki.extensions.utils.links import absolute
from kaamiki.extensions.utils.links import elsewhere
from kaamiki.extensions.utils.links import hostnames
from kaamiki.extensions.utils.links import hosts
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.links import youtube_id
from kaamiki.extensions.utils.reading import reading_length
from kaamiki.extensions.utils.reading import reading_speed
from kaamiki.extensions.utils.reading import reading_time
from kaamiki.extensions.utils.reading import wordcount
from kaamiki.extensions.utils.settings import icon
from kaamiki.extensions.utils.settings import language_icon
from kaamiki.extensions.utils.settings import logo_size
from kaamiki.extensions.utils.settings import reread
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.settings import toctree_args
from kaamiki.extensions.utils.social import generated
from kaamiki.extensions.utils.social import social_metadata
from kaamiki.extensions.utils.templates import bridge
from kaamiki.extensions.utils.templates import design_assets
from kaamiki.extensions.utils.templates import designed
from kaamiki.extensions.utils.templates import environment
from kaamiki.extensions.utils.templates import render
from kaamiki.extensions.utils.templates import themed
from kaamiki.extensions.utils.text import clip
from kaamiki.extensions.utils.text import plain
from kaamiki.extensions.utils.text import tidy

__all__: list[str] = [
    "absolute",
    "badged",
    "bridge",
    "build_finished",
    "buried",
    "clip",
    "committed",
    "context_defaults",
    "dated",
    "day",
    "depart",
    "design_assets",
    "designed",
    "elsewhere",
    "environment",
    "feedback",
    "fields",
    "findall",
    "generated",
    "header",
    "hidden",
    "hostnames",
    "hosts",
    "icon",
    "language_icon",
    "listed",
    "logo_size",
    "not_found",
    "offer",
    "opens_new_tab",
    "page_switches",
    "parse",
    "phrase",
    "plain",
    "provenance",
    "reading_length",
    "reading_speed",
    "reading_time",
    "render",
    "reread",
    "root_urls",
    "seconds",
    "setting",
    "sitemap",
    "skip",
    "social_metadata",
    "standfirst",
    "summarise",
    "themed",
    "tidy",
    "toctree_args",
    "toggle",
    "trail",
    "updated_on",
    "visitor",
    "wordcount",
    "writer",
    "written",
    "youtube_id",
]
