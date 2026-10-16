"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 15 October 2026

Kaamiki's shared helpers, now as its own module.
"""

from kaamiki.extensions.utils import writer
from kaamiki.extensions.utils.build import build_finished
from kaamiki.extensions.utils.context import articles
from kaamiki.extensions.utils.context import context_defaults
from kaamiki.extensions.utils.context import feedback
from kaamiki.extensions.utils.context import follow
from kaamiki.extensions.utils.context import forget_lead
from kaamiki.extensions.utils.context import header_leads
from kaamiki.extensions.utils.context import merge_leads
from kaamiki.extensions.utils.context import neighbours
from kaamiki.extensions.utils.context import note_lead
from kaamiki.extensions.utils.context import page_switches
from kaamiki.extensions.utils.dates import dated
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.dates import provenance
from kaamiki.extensions.utils.dates import updated_on
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
from kaamiki.extensions.utils.doctree import annotated
from kaamiki.extensions.utils.doctree import badged
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.doctree import offer
from kaamiki.extensions.utils.links import hostnames
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.links import rooted
from kaamiki.extensions.utils.links import youtube_id
from kaamiki.extensions.utils.reading import reading_length
from kaamiki.extensions.utils.reading import reading_time
from kaamiki.extensions.utils.settings import icon
from kaamiki.extensions.utils.settings import reread
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.social import social_metadata
from kaamiki.extensions.utils.templates import bridge
from kaamiki.extensions.utils.templates import design_assets
from kaamiki.extensions.utils.templates import render
from kaamiki.extensions.utils.templates import themed

__all__: list[str] = [
    "annotated",
    "articles",
    "badged",
    "bridge",
    "build_finished",
    "context_defaults",
    "dated",
    "day",
    "depart",
    "design_assets",
    "feedback",
    "fields",
    "findall",
    "follow",
    "forget_lead",
    "header_leads",
    "hostnames",
    "icon",
    "listed",
    "merge_leads",
    "neighbours",
    "note_lead",
    "offer",
    "opens_new_tab",
    "page_switches",
    "parse",
    "phrase",
    "provenance",
    "reading_length",
    "reading_time",
    "render",
    "reread",
    "rooted",
    "seconds",
    "setting",
    "skip",
    "social_metadata",
    "themed",
    "toggle",
    "trail",
    "updated_on",
    "visitor",
    "writer",
    "youtube_id",
]
