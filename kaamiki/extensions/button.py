"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April 2026
Last updated on: 15 November 2026

A `button` directive that renders a link as a button::

    .. button:: https://example.com/demo.mp4
       :fa-icon: video
       :scheme: dark

       Watch it here!

A page of the site is named with `:doc:` or `:ref:` in place of the
address, so the link works under every builder::

    .. button::
       :doc: index

       Back to the start
"""

from __future__ import annotations

import colorsys
import functools
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.block import address
from kaamiki.extensions.roles import steady
from kaamiki.extensions.utils import KaamikiDirective
from kaamiki.extensions.utils import Option
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import html
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import paragraph
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import values
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import guarded
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES
from kaamiki.extensions.utils.settings import SCHEMES

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

template: t.Final[str] = "directives/button.html.jinja"
# NOTE(xames3): Inspired by Sphinx Design's button directive.
# https://sphinx-design.readthedocs.io/en/latest/badges_buttons.html
RELS: t.Final[frozenset[str]] = frozenset(
    {
        "author",
        "external",
        "help",
        "license",
        "nofollow",
        "noopener",
        "noreferrer",
        "sponsored",
        "ugc",
    }
)
DOWNLOAD: t.Final[re.Pattern[str]] = re.compile(r"[\w][\w.+-]{0,119}")
ZERO_WIDTH: t.Final[re.Pattern[str]] = re.compile(
    r"[\u200b-\u200d\u2060\ufeff]"
)
ESCAPED_SPACE: t.Final[re.Pattern[str]] = re.compile(r"\\(?:\s|$)")
ICON_POSITIONS: t.Final[tuple[str, ...]] = CHOICES["button_icon_position"]


def blank(text: str) -> bool:
    """Say whether a label would draw nothing.

    :param text: The label as written.
    :return: `True` for spaces, zero-width characters and escaped
        spaces and nothing else.
    """
    return not ESCAPED_SPACE.sub("", ZERO_WIDTH.sub("", text)).strip()


def hsl(value: str) -> str:
    """Turn a colour into the three numbers `hsl()` takes.

    :param value: A hex colour like `#7c3aed` or the numbers
        themselves, as `262 83% 58%`.
    :return: The numbers.
    """
    value = value.strip()
    if not value.startswith("#"):
        return " ".join(value.split())
    digits = value.removeprefix("#")
    if len(digits) == 3:
        digits = "".join(_ * 2 for _ in digits)
    red, green, blue = (int(digits[_ : _ + 2], 16) / 255 for _ in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(red, green, blue)
    return f"{hue * 360:.0f} {sat * 100:.0f}% {light * 100:.0f}%"


def rel(argument: str | None) -> str:
    """Check what a link's `rel` says.

    :param argument: The words as written.
    :return: The words.
    :raises ValueError: For one that isn't a link type.
    """
    found = (argument or "").split()
    if not found or any(_ not in RELS for _ in found):
        raise ValueError(
            f"expected some of {', '.join(sorted(RELS))}, got {argument!r}"
        )
    return " ".join(found)


def download(argument: str | None) -> str:
    """Check the file name a download is saved under.

    :param argument: The name as written, or `None` for the link's own.
    :return: The name, empty for none.
    :raises ValueError: For a path or a name with odd characters.
    """
    if argument is None:
        return ""
    if not DOWNLOAD.fullmatch(argument.strip()):
        raise ValueError(
            f"expected a file name like report.pdf, got {argument!r}"
        )
    return argument.strip()


class Button(KaamikiDirective):
    """The `button` directive.

    The argument is the address: a full address, a path on the site or
    a fragment. `doc` and `ref` can replace it. A button has only one of
    the three.

    Options::

        - `doc`: A document of the site, named as `:doc:` names it. The
          button links to it. The link works with all builders.
        - `ref`: A label, named as `:ref:` names it. Capitals and spaces
          do not change the label. The button links to it.
        - `fa-icon`: A Font Awesome icon, as `video`, `fa-video` or
          `fa-regular fa-video`. An icon without a style uses the site's
          `kaamiki.conf.icons.style`, which is `regular` by default.
          When Font Awesome Free has no icon of that name in that style,
          it uses `solid`.
        - `icon-position`: The side of the label for the icon, `before`
          or `after`. The default is `before`. It needs `fa-icon`.
        - `align`: Where the button is, `left`, `center` or `right`. The
          default is `left`.
        - `scheme`: `light`, `dark`, `chevron`, `red`, `yellow`, `blue`
          or `green`. A colour in `kaamiki.conf.button.colours` is also
          correct. `chevron` is `light` with a chevron on the right. On
          hover, the chevron changes to an arrow.
        - `new-tab`: Open the link in a new tab, also on this site. The
          build stops when the link opens in a new tab already.
        - `same-tab`: Open the link in this tab, also for a different
          site. Without it, a link to a different site opens in a new
          tab, unless `kaamiki.conf.links.new_tab` of the site is off.
          The build stops when the link stays in this tab already.
        - `rel`: The `rel` of the link. It adds to `noopener
          noreferrer`, which a link that opens in a new tab always has.
        - `tooltip`: The text that shows when a reader hovers on the
          button, with a maximum of 120 characters.
        - `download`: Save the link, not open it, with the file name if
          you give one.
        - `name`: A name for links.
        - `class`: More classes for the link.

    When a button does not set the scheme or the side of its icon,
    `kaamiki.conf.button.scheme` and `kaamiki.conf.button.icon_position`
    set them. The `chevron` scheme cannot have `fa-icon` or
    `icon-position`. Thus, when the site uses `chevron`, a button with
    an icon is `light`.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    doc = Option(checks.text)
    ref = Option(checks.text)
    fa_icon = Option(checks.icon)
    icon_position = Option(checks.word(*ICON_POSITIONS), needs="fa-icon")
    align = Option(checks.word(*ALIGNMENTS))
    scheme = Option(checks.text)
    new_tab = Option(rst.directives.flag)
    same_tab = Option(rst.directives.flag)
    rel = Option(rel)
    tooltip = Option(functools.partial(checks.text, maximum=120))
    download = Option(download)

    class Node(nodes.Element):
        """The button and its parsed label, which `visit` writes."""

    def build(self) -> list[nodes.Node]:
        """Parse the label and return the button's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the label reported.
        """
        config = self.config
        options = self.options
        if "new-tab" in options and "same-tab" in options:
            self.fail(":new-tab: not allowed with :same-tab:")
        argument = self.arguments.pop() if self.arguments else ""
        kind = next((_ for _ in ("doc", "ref") if _ in options), "")
        names = [
            *(["the address"] if argument else []),
            *(f":{_}:" for _ in ("doc", "ref") if _ in options),
        ]
        if not names:
            self.fail("expected an address, :doc: or :ref:, got none")
        if len(names) > 1:
            self.fail(f"{names[0]} not allowed with {names[1]}")
        url, link = "", ""
        if kind == "doc":
            link = document(self, options.pop("doc"), "doc")
        elif kind == "ref":
            link = options.pop("ref")
        else:
            try:
                url = checks.link(argument)
            except ValueError as error:
                self.fail(f"{error}")
        new_tab = bool(url) and opens_new_tab(url, config)
        if "new-tab" in options or "same-tab" in options:
            if ("new-tab" in options) == new_tab:
                self.fail(
                    f":{'new-tab' if new_tab else 'same-tab'}: does"
                    " nothing, the link does that already"
                )
            new_tab = "new-tab" in options
        if "download" in options and (new_tab or "new-tab" in options):
            self.fail(":download: not allowed with a new tab")
        look, style = self.look(
            options.pop("scheme", None), iconic="fa-icon" in options
        )
        chevron = look == "km-button--scheme-chevron"
        if chevron and ("fa-icon" in options or "icon-position" in options):
            self.fail(
                "the chevron scheme isn't allowed with :fa-icon: or "
                ":icon-position:"
            )
        side = options.pop("icon-position", None)
        if side is None:
            side = values(config).button.icon_position
        source, line = self.state_machine.get_source_and_line(self.lineno)
        attributes: dict[str, t.Any] = {}
        attributes["url"] = url
        attributes["kind"] = kind
        attributes["link"] = link
        attributes["where"] = f"{source}:{line}"
        try:
            attributes["faicon"] = Icons.of(config).custom(
                options.pop("fa-icon", None)
            )
        except ValueError as error:
            self.fail(f":fa-icon: {error}")
        attributes["faicon_after"] = side == "after"
        attributes["chevron"] = chevron
        attributes["align"] = options.pop("align", "left")
        attributes["look"] = look
        attributes["extra"] = " ".join(
            ALIASES.get(_, _) for _ in options.pop("class", [])
        )
        said = options.pop("rel", None)
        attributes["anchor"] = {
            "rel": guarded(said) if new_tab else said,
            "target": "_blank" if new_tab else None,
            "title": options.pop("tooltip", None),
            "download": options.pop("download", None),
            "style": style or None,
        }
        text = "\n".join(self.content).strip()
        if blank(text):
            self.fail("expected a label, got none")
        label, messages = paragraph(self, text, "text")
        unlinked(self, label, "a label")
        worded(self, label, "a label")
        steady(
            self,
            label,
            "a label",
            "which the script doesn't run inside a link",
        )
        element = self.Node("", label, **attributes)
        self.add_name(element)
        return [element, *trail(self, attributes, ("url",)), *messages]

    def look(self, scheme: str | None, *, iconic: bool) -> tuple[str, str]:
        """Work out the classes and the colour a scheme stands for.

        :param scheme: The scheme as written or `None` for the site's.
        :param iconic: Whether the button has an icon, which a site's
            `chevron` doesn't suit, so it's `light` there.
        :return: The classes and the inline style holding the colour,
            if the scheme is one the site named. The `dark` scheme is
            how a button looks without one and has no class.
        """
        config = self.config
        colours = values(config).button.colours
        where = ""
        if scheme is None:
            scheme = values(config).button.scheme
            where = " (set by kaamiki.conf.button.scheme)"
            if scheme == "chevron" and iconic:
                scheme = "light"
        if scheme in colours:
            slug = nodes.make_id(scheme)
            return (
                f"km-button--scheme-custom km-button--scheme-{slug}",
                f"--km-colour-button-scheme: {hsl(str(colours[scheme]))}",
            )
        if scheme not in SCHEMES:
            options = ", ".join(map(repr, [*SCHEMES, *sorted(colours)]))
            self.fail(
                f":scheme: expected one of {options}, got {scheme!r}{where}"
            )
        return ("" if scheme == "dark" else f"km-button--scheme-{scheme}"), ""

    @staticmethod
    def plain(node: Button.Node) -> list[nodes.Node]:
        """Write a button as words, for a builder that writes no HTML.

        :param node: The button's node.
        :return: A paragraph with its label and its address, written as a
            link to itself, which a text writer would otherwise drop. A
            button that names a page of the site has no address to show.
        """
        label = next(each for each in node.children if isinstance(each, phrase))
        words = nodes.paragraph("", "", *label.children)
        if node["url"]:
            link = nodes.reference("", node["url"], refuri=node["url"])
            words += [nodes.Text(" "), link]
        return [words]


def prepare(
    self: HTMLTranslator, attributes: dict[str, t.Any]
) -> dict[str, t.Any]:
    """Work out where a button that names a page of the site goes.

    :param self: The HTML translator writing the page.
    :param attributes: The node's attributes.
    :return: A copy of them, with the address a `doc` or a `ref` comes
        to from this page under this builder.
    """
    found = dict(attributes)
    if found["kind"]:
        found["url"], _ = address(
            self, "button", found["kind"], found["link"], found["where"]
        )
    return found


html.draws(Button.Node, template, prepare)
