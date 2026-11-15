"""\
Hook Utilities
==============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 15 November 2026
Last updated on: 15 November 2026

The record of the Sphinx events that Kaamiki listens to.
"""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx


class Hooks:
    """The record of the Sphinx events that Kaamiki listens to."""

    def __init__(self) -> None:
        """Make an empty record."""
        self.handlers: list[tuple[str, Callable[..., t.Any], int]] = []

    def __call__[F: Callable[..., t.Any]](
        self, event: str, *, priority: int = 500
    ) -> Callable[[F], F]:
        """Record the function below as a handler of an event.

        :param event: The Sphinx event, as `doctree-read`.
        :param priority: The priority of the handler. A lower priority
            runs first.
        :return: The decorator, which gives back the same function.
        """

        def record(function: F) -> F:
            self.handlers.append((event, function, priority))
            return function

        return record

    def connect(self, app: Sphinx) -> None:
        """Connect each handler to its event, in the recorded sequence.

        :param app: The Sphinx application instance.
        """
        for event, function, priority in self.handlers:
            app.connect(event, function, priority=priority)


on: t.Final[Hooks] = Hooks()
