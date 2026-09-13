"""\
Picture Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 02 September, 2025
Last updated on: 11 September, 2026

A `picture` directive that swaps the image with the colour mode::

    .. picture::
       :light: ../assets/docker-internals/light-docker.jpg
       :dark: ../assets/docker-internals/dark-docker.jpg
       :alt: Docker Internals

Both images are copied into `_images` and written into
`picture.html.jinja`, which shows one or the other in CSS. The
directive extends the standard `figure`, so it takes the same
alignment, caption and class options.

.. versionchanged:: 19.10.2025

    The two images are swapped in CSS by an `img` tag apiece rather
    than by JavaScript.

.. versionadded:: 10.9.2026

    The image's real pixel size is read off the file header by
    `utils.measure` and written out as `width`/`height`, so the browser
    holds the space open before the image lands and the page stops
    shuffling about.

.. versionchanged:: 10.9.2026

    [1] Rendering goes through `utils.render`, which has autoescaping
        on. The per-module templates it replaced had it off, so a
        caption or alt text carrying an `&`, a `<` or a stray quote
        emitted broken markup.
    [2] A bad `:align:` raises a directive error instead of tripping an
        `assert`. The assert vanished under `python -O` and, when it
        did fire, gave a traceback rather than an error pointing at the
        line.

.. deprecated:: 10.9.2026

    [1] The module-level path fiddling has moved to `utils`, along with
        the `jinja2` import. `template` is now just the filename.
    [2] Dropped the empty `depart`. It existed only because `add_node`
        wants a pair; the theme falls back to the shared no-op in
        `utils` when a directive doesn't define one.
"""

from __future__ import annotations

import os
import os.path as p
import shutil
import typing as t

import docutils.nodes as nodes
from docutils.parsers import rst
from docutils.parsers.rst.directives import images

from kaamiki.extensions.utils import measure
from kaamiki.extensions.utils import render

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "picture"
template: t.Final[str] = "picture.html.jinja"


class node(nodes.Element):
    """The parsed directive, waiting for `visit` to write it out."""


class directive(images.Figure):
    """The `picture` directive.

    Options::

        - `light`: Path to the image for light mode, relative to the
          document.
        - `dark`: Path to the image for dark mode.
        - `alt`: Alternative text for both.
        - `align`: `left`, `center`, `right`, `top`, `middle` or
          `bottom`.
        - `figclass`: Class for the figure.
        - `class`: Class for the image.
    """

    required_arguments = 0
    option_spec = {  # noqa: RUF012
        "light": rst.directives.unchanged_required,
        "dark": rst.directives.unchanged_required,
        "alt": rst.directives.unchanged,
        "align": rst.directives.unchanged,
        "figclass": rst.directives.class_option,
        "class": rst.directives.class_option,
    }

    def run(self) -> list[nodes.Node]:
        """Copy both images, measure one and return the node.

        :return: A list holding the one `picture` node.

        .. versionchanged:: 10.9.2026

            [1] Renders through `utils.render`, so the caption and the
                alt text are escaped on their way into the template.
            [2] Measures the chosen image with `utils.measure` and
                passes its `width`/`height` through, so the browser
                holds the space open before the image lands.
            [3] A bad `:align:` raises a directive error rather than
                tripping an `assert`, which vanished under `python -O`
                and gave a traceback instead of a located error.
        """
        env = self.state.document.settings.env
        depth = env.docname.count("/")
        doc_dir = p.dirname(env.doc2path(env.docname))
        images_dir = p.join(env.app.builder.outdir, "_images")
        os.makedirs(images_dir, exist_ok=True)
        allowed = (
            "left",
            "center",
            "right",
            "top",
            "middle",
            "bottom",
            "default",
        )

        def _copy(src: str) -> None:
            """Copy the image into `_images`, unless it is there and
            no older than the source.
            """
            dest = p.join(images_dir, p.basename(src))
            try:
                if (
                    not p.exists(dest)
                    or os.stat(src).st_mtime > os.stat(dest).st_mtime
                ):
                    shutil.copy2(src, dest)
            except OSError as exc:
                raise self.error(
                    f"Failed to copy {src!r} to {dest!r}: {exc}"
                ) from exc

        light = p.normpath(p.join(doc_dir, self.options["light"]))
        dark = p.normpath(p.join(doc_dir, self.options["dark"]))
        for mode in [light, dark]:
            _copy(mode)
        prefix = "../" * depth if depth else ""
        klass = self.options.get("class", "")
        align = self.options.get("align", "default")
        if align not in allowed:
            raise self.error(
                f"Invalid :align: {align!r}. Choose from {', '.join(allowed)}"
            )
        size = measure(light) or measure(dark)
        attributes = {
            "light": f"{prefix}_images/{p.basename(light)}",
            "dark": f"{prefix}_images/{p.basename(dark)}",
            "alt": self.options.get("alt", ""),
            "align": align,
            "figclass": self.options.get("figclass", klass),
            "caption": "\n".join(self.content) if self.content else "",
            "width": size[0] if size else "",
            "height": size[1] if size else "",
        }
        element = node("", **attributes)
        return [element]


def visit(self: HTMLTranslator, node: node) -> None:
    """Write the figure out when the HTML writer reaches the node.

    :param self: The HTML translator, whose body this appends to.
    :param node: The `picture` node and its attributes.
    """
    self.body.append(render(template, **node.attributes))
