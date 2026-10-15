"""\
Button Directive
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 29 April 2026
Last updated on: 13 October 2026

A `button` directive that renders a link as a button::

    .. button:: https://www.w3schools.com/tags/movie.mp4
       :fa-icon: video
       :scheme: dark

       Watch it here!
"""

import colorsys
import functools
import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

from kaamiki.extensions.utils import icon
from kaamiki.extensions.utils import opens_new_tab
from kaamiki.extensions.utils import parse
from kaamiki.extensions.utils import setting
from kaamiki.extensions.utils import trail
from kaamiki.extensions.utils import visitor
from kaamiki.extensions.utils.links import REL
from kaamiki.extensions.utils.settings import CHOICES
from kaamiki.extensions.utils.settings import TONES

name: t.Final[str] = "button"
template: t.Final[str] = "directives/button.html.jinja"
# NOTE(xames3): Inspired by Sphinx Design's button directive.
# https://sphinx-design.readthedocs.io/en/latest/badges_buttons.html
SCHEMES: t.Final[tuple[str, ...]] = ("dark", "light", *TONES)
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


class node(nodes.Element):
    """The button and its parsed label, waiting for `visit`."""


class directive(rst.Directive):
    """The `button` directive.

    Options::

        - `fa-icon`: A Font Awesome icon, as `video`, `fa-video` or
          `far fa-video`. One without a style is drawn solid.
        - `fa-icon-position`: `before` the label, the default or
          `after` it.
        - `scheme`: `dark`, `light`, `red`, `yellow`, `blue` or
          `green`, or a colour named in `button_colours`.
        - `new-tab`: Open the link in a new tab, even on this site.
        - `no-new-tab`: Open the link in this tab, even off this site.
          A link off this site opens in a new tab without it, unless
          the site's `open_links_in_new_tab` is off.
        - `rel`: What the link's `rel` says. Defaults to
          `noopener noreferrer` for a new tab.
        - `title`: The tooltip.
        - `download`: Save the link instead of opening it, under the
          file name given if there's one.
        - `class`: More classes for the link.

    The site's `button_scheme` and `button_icon_position` settle the
    scheme and the icon's side for a button that doesn't say.
    """

    has_content = True
    required_arguments = 1
    final_argument_whitespace = False
    option_spec = {  # noqa: RUF012
        "fa-icon": rst.directives.unchanged,
        "fa-icon-position": functools.partial(
            rst.directives.choice, values=POSITIONS
        ),
        "scheme": rst.directives.unchanged_required,
        "new-tab": rst.directives.flag,
        "no-new-tab": rst.directives.flag,
        "rel": rst.directives.unchanged_required,
        "title": rst.directives.unchanged_required,
        "download": rst.directives.unchanged,
        "class": rst.directives.class_option,
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
            raise self.error("button takes :new-tab: or :no-new-tab:, not both")
        url = rst.directives.uri(self.arguments.pop().strip())
        new_tab = opens_new_tab(url, config)
        if "new-tab" in options or "no-new-tab" in options:
            new_tab = "new-tab" in options
        side = options.pop("fa-icon-position", None)
        if side is None:
            side = setting(config, "button_icon_position")
        look, style = self.look(options.pop("scheme", None))
        attributes: dict[str, t.Any] = {}
        attributes["url"] = url
        attributes["faicon"] = icon(options.pop("fa-icon", None))
        attributes["faicon_after"] = side == "after"
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
        label, messages = parse(self, text, "text")
        element = node("", label, **attributes)
        return [element, *trail(attributes, ("url",)), *messages]

    def look(self, scheme: str | None) -> tuple[str, str]:
        """Work out the classes and the colour a scheme stands for.

        :param scheme: The scheme as written or `None` for the site's.
        :return: The classes and the inline style holding the colour, if
            the scheme is one the site named.
        """
        config = self.state.document.settings.env.config
        named = {
            str(_).strip().lower(): value
            for _, value in setting(config, "button_colours").items()
        }
        if scheme is None:
            scheme = str(setting(config, "button_scheme"))
            where = " (set by button_scheme)"
        else:
            where = ""
        key = scheme.strip().lower()
        if key in named:
            return (
                f"km-button--custom km-button--{nodes.make_id(key)}",
                f"--km-button-colour: {hsl(str(named[key]))}",
            )
        if key not in SCHEMES:
            options = ", ".join([*SCHEMES, *sorted(named)])
            raise self.error(
                f"button scheme {scheme!r}{where} is not one of {options}"
            )
        return (
            f"km-button--{key}" if key in TONES else f"sd-btn-{key}",
            "",
        )


visit = visitor(template)
