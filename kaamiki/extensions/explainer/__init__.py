"""\
Explainer Extensions
====================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September, 2026
Last updated on: 29 September, 2026

The directives that explain a piece of code by showing it run, rather
than by pasting it and narrating underneath which I was doing before.
It wasn't the smartest move on my part initially, but it led me to
write this explainer module to better explain and walkthrough my
stories.
"""

from __future__ import annotations

from . import walkthrough

__all__: list[str] = ["walkthrough"]
