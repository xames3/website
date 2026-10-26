"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April 2026
Last updated on: 25 October 2026

A `button` directive that renders a link as a button::

    .. button:: https://www.w3schools.com/tags/movie.mp4
       :fa-icon: video
       :scheme: dark

       Watch it here!
"""

import colorsys
import re
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import NATIVE
from kaamiki.extensions.utils import checks
from kaamiki.extensions.utils import icon
from kaamiki.extensions.utils import named
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.settings import ALIGNMENTS
from kaamiki.extensions.utils.settings import CHOICES
from kaamiki.extensions.utils.settings import SCHEMES

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
POSITIONS: t.Final[tuple[str, ...]] = CHOICES["button_icon_position"]


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


class node(nodes.Element):
    """The button and its parsed label, waiting for `visit`."""


class directive(rst.Directive):
    """The `button` directive.

    Options::

        - `fa-icon`: A Font Awesome icon, as `video`, `fa-video` or
          `far fa-video`. One without a style is drawn solid.
        - `fa-icon-position`: `before` the label, the default or
          `after` it.
        - `align`: Where the button sits, `left`, `center` or `right`.
          Defaults to `left`.
        - `scheme`: `light`, `dark`, `chevron`, `red`, `yellow`, `blue`
          or `green`, or a colour named in `button_colours`. `chevron`
          is `light` with a chevron on the right that turns into an
          arrow on hover.
        - `new-tab`: Open the link in a new tab, even on this site.
        - `no-new-tab`: Open the link in this tab, even off this site.
          A link off this site opens in a new tab without it, unless
          the site's `open_links_in_new_tab` is off.
        - `rel`: What the link's `rel` says. Defaults to
          `noopener noreferrer` for a new tab.
        - `title`: The tooltip.
        - `download`: Save the link instead of opening it, under the
          file name given if there's one.
        - `name`: A name to link to.
        - `class`: More classes for the link.

    The site's `button_scheme` and `button_icon_position` settle the
    scheme and the icon's side for a button that doesn't say. The
    `chevron` scheme takes neither `fa-icon` nor `fa-icon-position`.

    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        **NATIVE,
        "fa-icon": checks.icon,
        "fa-icon-position": checks.word(*POSITIONS),
        "align": checks.word(*ALIGNMENTS),
        "scheme": checks.text,
        "new-tab": rst.directives.flag,
        "no-new-tab": rst.directives.flag,
        "rel": rel,
        "title": lambda _: checks.text(_, 120),
        "download": download,
    }

    def run(self) -> list[nodes.Node]:
        """Parse the label and return the button's node.

        :return: The node, followed by the `raw` node `trail` returns
            for the link checker and anything the label reported.
        """
        self.assert_has_content()
        config = self.state.document.settings.env.config
        options = self.options
        if "new-tab" in options and "no-new-tab" in options:
            raise self.error("button: :new-tab: not allowed with :no-new-tab:")
        try:
            url = checks.link(self.arguments.pop())
        except ValueError as error:
            raise self.error(f"button: {error}") from error
        new_tab = opens_new_tab(url, config)
        if "new-tab" in options or "no-new-tab" in options:
            if ("new-tab" in options) == new_tab:
                raise self.error(
                    f"button: :{'new-tab' if new_tab else 'no-new-tab'}: does"
                    " nothing, the link does that already"
                )
            new_tab = "new-tab" in options
        if "download" in options and (new_tab or "new-tab" in options):
            raise self.error("button: :download: not allowed with a new tab")
        if "fa-icon-position" in options and "fa-icon" not in options:
            raise self.error("button: :fa-icon-position: requires :fa-icon:")
        look, style = self.look(options.pop("scheme", None))
        chevron = look == "km-button--chevron"
        if chevron and ("fa-icon" in options or "fa-icon-position" in options):
            raise self.error(
                "button: the chevron scheme not allowed with :fa-icon: or "
                ":fa-icon-position:"
            )
        side = options.pop("fa-icon-position", None)
        if side is None:
            side = setting(config, "button_icon_position")
        attributes: dict[str, t.Any] = {}
        attributes["url"] = url
        attributes["faicon"] = icon(
            options.pop("fa-icon", None), kit=bool(setting(config, "fa_kit"))
        )
        attributes["faicon_after"] = side == "after"
        attributes["chevron"] = chevron
        attributes["align"] = options.pop("align", "left")
        attributes["look"] = look
        attributes["extra"] = " ".join(options.pop("class", []))
        attributes["anchor"] = {
            "rel": options.pop("rel", None) or (REL if new_tab else None),
            "target": "_blank" if new_tab else None,
            "title": options.pop("title", None),
            "download": options.pop("download", None),
            "style": style or None,
        }
        text = "\n".join(self.content).strip()
        if not text:
            raise self.error("button: expected a label, got none")
        label, messages = parse(self, text, "text")
        element = node("", label, **attributes)
        named(self, element)
        return [element, *trail(attributes, ("url",)), *messages]

    def look(self, scheme: str | None) -> tuple[str, str]:
        """Work out the classes and the colour a scheme stands for.

        :param scheme: The scheme as written or `None` for the site's.
        :return: The classes and the inline style holding the colour, if
            the scheme is one the site named.
        """
        config = self.state.document.settings.env.config
        named = setting(config, "button_colours")
        where = ""
        if scheme is None:
            scheme = str(setting(config, "button_scheme"))
            where = " (set by button_scheme)"
        if scheme in named:
            return (
                f"km-button--custom km-button--{nodes.make_id(scheme)}",
                f"--km-colour-button-scheme: {hsl(str(named[scheme]))}",
            )
        if scheme not in SCHEMES:
            options = ", ".join([*SCHEMES, *sorted(named)])
            raise self.error(
                f"button: scheme {scheme!r}{where} expected one of {options}"
            )
        return f"km-button--{scheme}", ""


visit = visitor(template)
