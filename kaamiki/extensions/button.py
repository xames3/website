"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April 2026
Last updated on: 07 November 2026

A `button` directive that renders a link as a button::

    .. button:: https://www.w3schools.com/tags/movie.mp4
       :fa-icon: video
       :scheme: dark

       Watch it here!

A page of the site is named with `:doc:` or `:ref:` in place of the
address, so the link works under every builder::

    .. button::
       :doc: install

       Install it
"""

from __future__ import annotations

import colorsys
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.block import address
from kaamiki.extensions.roles import steady
from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import document
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import paragraph
from kaamiki.extensions.utils import phrase
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import unlinked
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils import worded
from kaamiki.extensions.utils.aliases import ALIASES
from kaamiki.extensions.utils.icons import Icons
from kaamiki.extensions.utils.links import guarded
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES
from kaamiki.extensions.utils.settings import SCHEMES

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "button"
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


class Button(nodes.Element):
    """The button and its parsed label, waiting for `visit`."""


class directive(rst.Directive):
    """The `button` directive.

    The argument is the address, a full one, a path on the site or a
    fragment. `doc` and `ref` stand in for it, and a button takes one
    of the three.

    Options::

        - `doc`: A document of the site the button links to, as `:doc:`
          names it. The link works under every builder.
        - `ref`: A label the button links to, as `:ref:` names it,
          capitals and spaces aside.
        - `fa-icon`: A Font Awesome icon, as `video`, `fa-video` or
          `far fa-video`. One without a style is drawn in the site's
          `kaamiki.conf.icons.style`, `regular` unless it says
          otherwise and `solid` where Font Awesome Free has no icon of
          that name in that style.
        - `icon-position`: `before` the label, the default or
          `after` it.
        - `align`: Where the button sits, `left`, `center` or `right`.
          Defaults to `left`.
        - `scheme`: `light`, `dark`, `chevron`, `red`, `yellow`, `blue`
          or `green`, or a colour named in
          `kaamiki.conf.button.colours`. `chevron` is `light` with a
          chevron on the right that turns into an arrow on hover.
        - `new-tab`: Open the link in a new tab, even on this site. It
          stops the build for a link that opens in one already.
        - `same-tab`: Open the link in this tab, even off this site.
          A link off this site opens in a new tab without it, unless
          the site's `kaamiki.conf.links.new_tab` is off. It stops the
          build for a link that stays in this tab already.
        - `rel`: What the link's `rel` says. It adds to `noopener
          noreferrer`, which a link that opens in a new tab always has.
        - `tooltip`: The text a reader sees when they hover over it, up
          to 120 characters.
        - `download`: Save the link instead of opening it, under the
          file name given if there's one.
        - `name`: A name to link to.
        - `class`: More classes for the link.

    The site's `kaamiki.conf.button.scheme` and
    `kaamiki.conf.button.icon_position` settle the scheme and the
    icon's side for a button that doesn't say. The `chevron` scheme
    takes neither `fa-icon` nor `icon-position`, so a button with an
    icon is `light` under a site-wide `chevron`.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "doc": checks.text,
        "ref": checks.text,
        "fa-icon": checks.icon,
        "icon-position": checks.word(*ICON_POSITIONS),
        "align": checks.word(*ALIGNMENTS),
        "scheme": checks.text,
        "new-tab": rst.directives.flag,
        "same-tab": rst.directives.flag,
        "rel": rel,
        "tooltip": lambda _: checks.text(_, 120),
        "download": download,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the label and return the button's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the label reported.
        """
        config = self.state.document.settings.env.config
        options = self.options
        if "new-tab" in options and "same-tab" in options:
            raise self.error("button: :new-tab: not allowed with :same-tab:")
        argument = self.arguments.pop() if self.arguments else ""
        kind = next((_ for _ in ("doc", "ref") if _ in options), "")
        names = [
            *(["the address"] if argument else []),
            *(f":{_}:" for _ in ("doc", "ref") if _ in options),
        ]
        if not names:
            raise self.error(
                "button: expected an address, :doc: or :ref:, got none"
            )
        if len(names) > 1:
            raise self.error(f"button: {names[0]} not allowed with {names[1]}")
        url, link = "", ""
        if kind == "doc":
            link = document(self, options.pop("doc"), "doc")
        elif kind == "ref":
            link = options.pop("ref")
        else:
            try:
                url = checks.link(argument)
            except ValueError as error:
                raise self.error(f"button: {error}") from error
        new_tab = bool(url) and opens_new_tab(url, config)
        if "new-tab" in options or "same-tab" in options:
            if ("new-tab" in options) == new_tab:
                raise self.error(
                    f"button: :{'new-tab' if new_tab else 'same-tab'}: does"
                    " nothing, the link does that already"
                )
            new_tab = "new-tab" in options
        if "download" in options and (new_tab or "new-tab" in options):
            raise self.error("button: :download: not allowed with a new tab")
        if "icon-position" in options and "fa-icon" not in options:
            raise self.error("button: :icon-position: needs :fa-icon:")
        look, style = self.look(
            options.pop("scheme", None), iconic="fa-icon" in options
        )
        chevron = look == "km-button--scheme-chevron"
        if chevron and ("fa-icon" in options or "icon-position" in options):
            raise self.error(
                "button: the chevron scheme is not allowed with :fa-icon: or "
                ":icon-position:"
            )
        side = options.pop("icon-position", None)
        if side is None:
            side = setting(config, "button_icon_position")
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
            raise self.error(f"button: :fa-icon: {error}") from error
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
            raise self.error("button: expected a label, got none")
        label, messages = paragraph(self, text, "text")
        unlinked(self, label, "a label")
        worded(self, label, "a label")
        steady(
            self,
            label,
            "a label",
            "which the script does not run inside a link",
        )
        element = Button("", label, **attributes)
        named(self, element)
        return [element, *trail(attributes, ("url",)), *messages]

    def look(self, scheme: str | None, *, iconic: bool) -> tuple[str, str]:
        """Work out the classes and the colour a scheme stands for.

        :param scheme: The scheme as written or `None` for the site's.
        :param iconic: Whether the button has an icon, which a site's
            `chevron` doesn't suit, so it is `light` there.
        :return: The classes and the inline style holding the colour,
            if the scheme is one the site named. The `dark` scheme is
            how a button looks without one and has no class.
        """
        config = self.state.document.settings.env.config
        colours = setting(config, "button_colours")
        where = ""
        if scheme is None:
            scheme = str(setting(config, "button_scheme"))
            where = " (set by kaamiki.conf.button.scheme)"
            if scheme == "chevron" and iconic:
                scheme = "light"
        if scheme in colours:
            named = nodes.make_id(scheme)
            return (
                f"km-button--scheme-custom km-button--scheme-{named}",
                f"--km-colour-button-scheme: {hsl(str(colours[scheme]))}",
            )
        if scheme not in SCHEMES:
            options = ", ".join(map(repr, [*SCHEMES, *sorted(colours)]))
            raise self.error(
                f"button: :scheme: expected one of {options}, got"
                f" {scheme!r}{where}"
            )
        return ("" if scheme == "dark" else f"km-button--scheme-{scheme}"), ""


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


def plain(node: Button) -> list[nodes.Node]:
    """Write a button as words, for a builder that draws no HTML.

    :param node: The button's node.
    :return: A paragraph with its label and its address, written as a
        link to itself, which a text writer would otherwise drop. A
        button that names a page of the site has no address to show.
    """
    label = next(_ for _ in node.children if isinstance(_, phrase))
    words = nodes.paragraph("", "", *label.children)
    if node["url"]:
        link = nodes.reference("", node["url"], refuri=node["url"])
        words += [nodes.Text(" "), link]
    return [words]


visit = visitor(template, prepare)


node = Button
