"""\
Picture Directive
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 02 September, 2025
Last updated on: 02 November, 2025

This module defines a custom `picture` directive for this sphinx theme.
The directive allows embedding and rendering images specific to the
document's current colour mode.

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
"""

from __future__ import annotations

import os
import os.path as p
import shutil
import typing as t

import docutils.nodes as nodes
import jinja2
from docutils.parsers import rst
from docutils.parsers.rst.directives import images

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "picture"
here: str = p.dirname(__file__)
templates: str = "../base/templates"
html = p.join(p.abspath(p.join(here, templates)), "picture.html.jinja")

with open(html) as f:
    template = jinja2.Template(f.read())


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
        assert align in allowed, (
            f"Available align options are {', '.join(allowed)}"
        )
        attributes = {
            "light": f"{prefix}_images/{p.basename(light)}",
            "dark": f"{prefix}_images/{p.basename(dark)}",
            "alt": self.options.get("alt", ""),
            "align": align,
            "figclass": self.options.get("figclass", klass),
            "caption": "\n".join(self.content) if self.content else "",
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
    self.body.append(template.render(**node.attributes))


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `picture` node during HTML
    generation.

    This method is invoked after the node's HTML representation has been
    fully processed and added to the output. Since the `picture` node
    does not require any closing actions, the method currently acts as a
    placeholder.

    :param self: The HTML translator instance.
    :param node: The `picture` node being processed.
    """
