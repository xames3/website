"""\
Picture Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 02 September, 2025
Last updated on: 11 September, 2026

This module defines a custom `picture` directive for the Kaamiki Sphinx
Theme. The directive allows embedding and rendering images specific to
the document's current colour mode.

The `picture` directive is designed to extend reStructuredText (rST)
capabilities by injecting structured metadata about the content, which
can be styled or processed further using Jinja2 templates.

The `picture` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. picture::
            :light: ../assets/docker-internals/light-docker.jpg
            :dark: ../assets/docker-internals/dark-docker.jpg
            :alt: Docker Internals

The above snippet will be processed and rendered according to the
theme's Jinja2 template, producing a final HTML output.

.. versionchanged:: 19.10.2025

    Simplified the directive to render images according to the theme's
    colour scheme using the `img` tag instead of fancy Javascript.

.. versionadded:: 10.9.2026

    [1] The image's real pixel size is read off the file header by
        `utils.measure` and emitted as `width`/`height`. The browser can
        hold the space open before the image lands, which is what stops
        the page shuffling about as you scroll.

.. versionchanged:: 10.9.2026

    [1] Rendering goes through `utils.render`, one shared Jinja
        environment for the whole theme with autoescaping switched on.
        The old per-module templates had escaping off, so a caption or
        an alt text carrying an `&`, a `<` or a stray quote quietly
        emitted broken markup.
    [2] A bad `:align:` raises a proper directive error instead of
        tripping an `assert`. The assert vanished entirely under `python
        -O` and, when it did fire, gave you a traceback rather than a
        build error pointing at the offending line.

.. deprecated:: 10.9.2026

    [1] The module-level `here`, `templates` and `html` path fiddling
        has moved out to `utils`, along with the `jinja2` import. Every
        directive was opening its own template at import time and
        building a bare `jinja2.Template` off it, which is a daft thing
        to do seven times over. `template` is now just the filename.
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
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


class directive(images.Figure):
    """Custom `picture` directive for reStructuredText.

    This class extends the standard `Figure` directive to provide
    theming-aware images that switch based on the current colour scheme.
    It inherits all the standard figure functionality while adding
    theme-specific image handling.

    The directive supports the following options::

        - `light`: Relative path of the image to render in light mode.
        - `dark`: Relative path of the image to render in dark mode.
        - `alt`: Alternate text for the image.
        - `align`: Alignment options for the image, available options
          are `left`, `center`, `right`, `top`, `middle`, `bottom`.
        - `figclass`: CSS class name.
        - `class`: CSS class name.

    .. versionchanged:: 19.10.2025

        Simplified the directive to render images according to the
        theme's colour scheme using the `img` tag instead of fancy
        Javascript.
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
        """Parse directive options and create an `picture` node.

        This method processes the image path prefix provided as an
        argument and combines it with the directive options to create
        a theming-aware picture element.

        The directive expects a path prefix that will be combined with
        'light' and 'dark' suffixes to create the final image paths.

        :return: A list containing a single `node` element.

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
            """Copy the source image to the destination if it doesn't
            already exist or is outdated.
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
    """Handle the entry processing of the `picture` node during HTML
    generation.

    This method is called when the HTML translator encounters the
    `picture` node in the document tree. It retrieves the relevant
    attributes from the node and uses Jinja2 templating to produce the
    final HTML output.

    :param self: The HTML translator instance responsible for rendering
        nodes into HTML.
    :param node: The `picture` node containing parsed attributes.
    """
    self.body.append(render(template, **node.attributes))
