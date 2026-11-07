"""\
Code Directives
===============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 September 2026
Last updated on: 02 November 2026

The code-explain and code-version directives, the code walkthroughs.
A `code-explain` walks through one snippet and, for Python, runs it to
show the values. A `code-version` shows several attempts at the same
problem with the output their author wrote.
"""

from . import explain
from . import version

__all__: list[str] = ["explain", "version"]
