"""\
Theme Utilities
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 21 February 2025
Last updated on: 07 November 2026

Kaamiki's shared helpers.
"""

from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import writer
from kaamiki.extensions.utils.aliases import spell
from kaamiki.extensions.utils.build import build_finished
from kaamiki.extensions.utils.context import admonition_title
from kaamiki.extensions.utils.context import confdir
from kaamiki.extensions.utils.context import context_defaults
from kaamiki.extensions.utils.context import ensure_articles
from kaamiki.extensions.utils.context import feedback
from kaamiki.extensions.utils.context import field_lists
from kaamiki.extensions.utils.context import follow
from kaamiki.extensions.utils.context import forget_lead
from kaamiki.extensions.utils.context import merge_leads
from kaamiki.extensions.utils.context import neighbours
from kaamiki.extensions.utils.context import note_lead
from kaamiki.extensions.utils.context import page_fields
from kaamiki.extensions.utils.context import page_switches
from kaamiki.extensions.utils.context import page_title
from kaamiki.extensions.utils.context import related
from kaamiki.extensions.utils.context import retitled
from kaamiki.extensions.utils.context import toctrees
from kaamiki.extensions.utils.dates import dated
from kaamiki.extensions.utils.dates import day
from kaamiki.extensions.utils.dates import provenance
from kaamiki.extensions.utils.dates import updated_on
from kaamiki.extensions.utils.dates import warm
from kaamiki.extensions.utils.directives import NATIVE
from kaamiki.extensions.utils.directives import close
from kaamiki.extensions.utils.directives import depart
from kaamiki.extensions.utils.directives import document
from kaamiki.extensions.utils.directives import fields
from kaamiki.extensions.utils.directives import hollow
from kaamiki.extensions.utils.directives import listed
from kaamiki.extensions.utils.directives import located
from kaamiki.extensions.utils.directives import named
from kaamiki.extensions.utils.directives import paragraph
from kaamiki.extensions.utils.directives import parse
from kaamiki.extensions.utils.directives import phrase
from kaamiki.extensions.utils.directives import shipped
from kaamiki.extensions.utils.directives import skip
from kaamiki.extensions.utils.directives import through
from kaamiki.extensions.utils.directives import titled
from kaamiki.extensions.utils.directives import trail
from kaamiki.extensions.utils.directives import unlinked
from kaamiki.extensions.utils.directives import visitor
from kaamiki.extensions.utils.directives import what
from kaamiki.extensions.utils.directives import worded
from kaamiki.extensions.utils.doctree import annotated
from kaamiki.extensions.utils.doctree import caption_icon
from kaamiki.extensions.utils.doctree import findall
from kaamiki.extensions.utils.doctree import glyph
from kaamiki.extensions.utils.doctree import glyph_edges
from kaamiki.extensions.utils.doctree import keycaps
from kaamiki.extensions.utils.doctree import offer
from kaamiki.extensions.utils.links import guarded
from kaamiki.extensions.utils.links import hostnames
from kaamiki.extensions.utils.links import opens_new_tab
from kaamiki.extensions.utils.links import relative_to_page
from kaamiki.extensions.utils.links import youtube_id
from kaamiki.extensions.utils.links import youtube_start
from kaamiki.extensions.utils.reading import reading_time
from kaamiki.extensions.utils.reading import show_more
from kaamiki.extensions.utils.settings import CONF
from kaamiki.extensions.utils.settings import apply
from kaamiki.extensions.utils.settings import kept
from kaamiki.extensions.utils.settings import overrides
from kaamiki.extensions.utils.settings import pair
from kaamiki.extensions.utils.settings import register
from kaamiki.extensions.utils.settings import reread
from kaamiki.extensions.utils.settings import setting
from kaamiki.extensions.utils.settings import stored
from kaamiki.extensions.utils.social import social_metadata
from kaamiki.extensions.utils.templates import TEMPLATES
from kaamiki.extensions.utils.templates import bridge
from kaamiki.extensions.utils.templates import render

__all__: list[str] = [
    "CONF",
    "NATIVE",
    "TEMPLATES",
    "admonition_title",
    "annotated",
    "apply",
    "bridge",
    "build_finished",
    "caption_icon",
    "checks",
    "close",
    "confdir",
    "context_defaults",
    "dated",
    "day",
    "depart",
    "document",
    "ensure_articles",
    "feedback",
    "field_lists",
    "fields",
    "findall",
    "follow",
    "forget_lead",
    "glyph",
    "glyph_edges",
    "guarded",
    "hollow",
    "hostnames",
    "kept",
    "keycaps",
    "listed",
    "located",
    "merge_leads",
    "named",
    "neighbours",
    "note_lead",
    "offer",
    "opens_new_tab",
    "overrides",
    "page_fields",
    "page_switches",
    "page_title",
    "pair",
    "paragraph",
    "parse",
    "phrase",
    "provenance",
    "reading_time",
    "register",
    "related",
    "relative_to_page",
    "render",
    "reread",
    "retitled",
    "setting",
    "shipped",
    "show_more",
    "skip",
    "social_metadata",
    "spell",
    "stored",
    "through",
    "titled",
    "toctrees",
    "trail",
    "unlinked",
    "updated_on",
    "visitor",
    "warm",
    "what",
    "worded",
    "writer",
    "youtube_id",
    "youtube_start",
]
