"""\
Slopcode Directive
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 03 August, 2026

This module defines the `slopcode` directive for the Kaamiki Sphinx
Theme -- a live, multiplayer "spot the AI-generated text" game.

Unlike every other directive in `kaamiki/extensions/`, this one is
deliberately monolithic: the directive class, the full HTML shell, the
component's CSS, and its client-side JS all live in this single file
as plain strings, rather than the theme's usual split across a
`.html.jinja` template plus entries appended to `theme.css`/`theme.js`.
That's an intentional, explicit deviation from the theme's convention
(every other directive keeps template/static assets in separate
files) -- everything this widget needs to look and behave like part of
the site lives in one place, so there is nothing to keep in sync
across files when it changes.

The `slopcode` directive can be used in reStructuredText documents as
follows::

    .. code-block:: rst

        .. slopcode::
            :expected-headcount-max: 20

GitHub Pages only serves static files -- there's no server-side code
execution here. So while this file renders the entire game's UI, it
cannot itself host a "room" that multiple visitors share live; every
visitor's browser independently runs the JS this directive emits, and
that JS talks over HTTPS/SignalR to a small Azure Functions backend
(see `azure/slopcode/function_app.py`) which is the actual source of
truth for who's in a room, what's been submitted, and how people
voted. This directive is the client, not the server.

The deployed backend's base URL is read from `conf.py`'s
`html_context` as `slopcode_api_base_url` (matching how `author.py`
already pulls project-wide defaults from `html_context` rather than
hardcoding them), with a `:function-base-url:` directive option
available as a manual override on a specific invocation.
"""

from __future__ import annotations

import typing as t

import docutils.nodes as nodes
import docutils.parsers.rst as rst

if t.TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator

name: t.Final[str] = "slopcode"

# Matches SignalR Free_F1's hard 20-concurrent-connection ceiling --
# the UI's own headcount cap can't promise a room size the backend is
# physically unable to support.
DEFAULT_HEADCOUNT_MAX: t.Final[int] = 20

SIGNALR_CLIENT_CDN_URL: t.Final[str] = (
    "https://cdn.jsdelivr.net/npm/@microsoft/signalr@8.0.7/"
    "dist/browser/signalr.min.js"
)


class node(nodes.Element):
    """Class to represent a custom node in the document tree.

    This class extends the `nodes.Element` from `docutils`, serving as
    the container for the parsed information. The node will ultimately
    be transformed into HTML or other output formats by the relevant
    Sphinx translators.
    """


class directive(rst.Directive):
    """Custom `slopcode` directive for reStructuredText.

    This class defines the behaviour of the `slopcode` directive. It
    takes no required arguments -- its only job is to drop the game's
    widget shell at a location in the page.

    The directive supports the following options::

        - `function-base-url`: Override for the deployed Azure
          Functions base URL. Normally this comes from `conf.py`'s
          `html_context["slopcode_api_base_url"]`; this option exists
          only as a per-invocation escape hatch.
        - `expected-headcount-max`: Upper bound the host's
          room-creation form won't let them exceed. Defaults to 20,
          matching SignalR Free_F1's connection cap.
    """

    required_arguments = 0
    option_spec = {  # noqa: RUF012
        "function-base-url": rst.directives.uri,
        "expected-headcount-max": rst.directives.positive_int,
    }

    def run(self) -> list[nodes.Node]:
        """Parse directive options and create a `slopcode` node.

        Reads `conf.py`'s `html_context` for the deployed backend's
        base URL, letting an explicit `:function-base-url:` option on
        this specific invocation take precedence if one is given.

        :return: A list containing a single raw HTML node.
        """
        ctx = self.state.document.settings.env.config.html_context
        api_base_url = self.options.get(
            "function-base-url", ctx.get("slopcode_api_base_url", "")
        )
        headcount_max = self.options.get(
            "expected-headcount-max", DEFAULT_HEADCOUNT_MAX
        )
        if not api_base_url:
            raise self.error(
                "slopcode directive requires either a "
                "':function-base-url:' option or "
                "'slopcode_api_base_url' set in conf.py's html_context."
            )

        uid = f"km-slopcode-{id(self)}"
        html = _render(
            uid=uid, api_base_url=api_base_url, headcount_max=headcount_max
        )
        return [nodes.raw(text=html, format="html")]


def visit(self: HTMLTranslator, node: node) -> None:
    """Handle the entry processing of the `slopcode` node during HTML
    generation.

    The `slopcode` node carries no attributes -- `run()` already
    rendered the final HTML into a `nodes.raw` node, so there's
    nothing left to do here. Present only to match the
    `app.add_node(..., html=(visit, depart))` signature every
    directive in this theme registers.

    :param self: The HTML translator instance.
    :param node: The `slopcode` node being processed.
    """


def depart(self: HTMLTranslator, node: node) -> None:
    """Handle the exit processing of the `slopcode` node during HTML
    generation.

    :param self: The HTML translator instance.
    :param node: The `slopcode` node being processed.
    """


def _render(*, uid: str, api_base_url: str, headcount_max: int) -> str:
    """Render the widget's full HTML+CSS+JS as a single string.

    Every phase of the game (login, lobby, submission, voting,
    results) is present in the DOM from first load; only one is ever
    un-hidden at a time via the shared `.site-slopcode--hidden` class,
    toggled by the JS below. This keeps DOM structure stable across
    phase transitions rather than swapping innerHTML wholesale.
    """
    css = _CSS_TEMPLATE
    html_shell = _HTML_TEMPLATE.format(uid=uid)
    script = _JS_TEMPLATE.format(
        uid=uid, api_base_url=api_base_url, headcount_max=headcount_max
    )
    return (
        f'<div class="site-slopcode" id="{uid}">\n'
        f"<style>{css}</style>\n"
        f"{html_shell}\n"
        f'<script src="{SIGNALR_CLIENT_CDN_URL}" defer></script>\n'
        f"<script>{script}</script>\n"
        f"</div>\n"
    )


# ----------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------
#
# New `.site-slopcode*` BEM blocks, matching the theme's existing
# naming convention (`.site-youtube-card`, `.site-feedback-shell--split`,
# etc.) and reusing the site's existing design tokens (`--km-color-*`,
# `--km-radius-normal`, `--km-ease-smooth`, ...) rather than inventing
# a new visual language. Scoped entirely under `.site-slopcode` so it
# can't leak into or collide with the rest of the theme's CSS.

_CSS_TEMPLATE: t.Final[str] = """
.site-slopcode {
  max-width: var(--km-layout-container, 861px);
  margin: 2rem auto;
  font-family: var(--km-font-sans, inherit);
  color: hsl(var(--km-color-fg));
}

.site-slopcode--hidden {
  display: none !important;
}

.site-slopcode__card {
  background-color: hsl(var(--km-color-surface));
  border: 1px solid hsl(var(--km-color-border));
  border-radius: var(--km-radius-normal, 0.75rem);
  padding: 1.75rem;
  transition-property: opacity, transform;
  transition-timing-function: var(--km-ease-smooth, ease);
  transition-duration: var(--km-duration-normal, 200ms);
}

.site-slopcode__title {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: hsl(var(--km-color-fg-strong));
}

.site-slopcode__subtitle {
  font-size: 0.9rem;
  color: hsl(var(--km-color-fg) / 0.7);
  margin: -0.5rem 0 1rem 0;
}

.site-slopcode__field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.site-slopcode__label {
  font-size: 0.85rem;
  font-weight: 500;
}

.site-slopcode__input,
.site-slopcode__textarea {
  background-color: hsl(var(--km-color-input, var(--km-color-bg)));
  border: 1px solid hsl(var(--km-color-border));
  border-radius: var(--km-radius-normal, 0.75rem);
  padding: 0.6rem 0.75rem;
  color: hsl(var(--km-color-fg));
  font-family: inherit;
  font-size: 0.95rem;
}

.site-slopcode__textarea {
  min-height: 140px;
  resize: vertical;
}

.site-slopcode__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  background-color: hsl(var(--km-color-primary));
  color: hsl(var(--km-color-bg));
  border: none;
  border-radius: var(--km-radius-round, 500px);
  padding: 0.55rem 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition-property: opacity, transform;
  transition-timing-function: var(--km-ease-smooth, ease);
  transition-duration: var(--km-duration-fast, 120ms);
}

.site-slopcode__button:hover {
  opacity: 0.9;
}

.site-slopcode__button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.site-slopcode__button--secondary {
  background-color: transparent;
  color: hsl(var(--km-color-fg));
  border: 1px solid hsl(var(--km-color-border));
}

.site-slopcode__error {
  color: hsl(var(--km-color-red, 0 70% 55%));
  font-size: 0.85rem;
  margin-top: 0.5rem;
  min-height: 1.1rem;
}

.site-slopcode__lobby-share {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  background-color: hsl(var(--km-color-accent-bg));
  color: hsl(var(--km-color-accent-fg));
  border-radius: var(--km-radius-normal, 0.75rem);
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  font-family: var(--km-font-mono, monospace);
  font-size: 1.1rem;
  letter-spacing: 0.08em;
}

.site-slopcode__lobby-count {
  font-size: 0.85rem;
  color: hsl(var(--km-color-fg) / 0.7);
  margin-bottom: 0.75rem;
}

.site-slopcode__participant-list {
  list-style: none;
  margin: 0 0 1.25rem 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.site-slopcode__participant {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--km-radius-normal, 0.75rem);
  background-color: hsl(var(--km-color-muted-bg, var(--km-color-bg)));
  font-size: 0.9rem;
}

.site-slopcode__participant--host::after {
  content: "Host";
  margin-left: auto;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: hsl(var(--km-color-primary));
}

.site-slopcode__participant--you {
  border: 1px solid hsl(var(--km-color-primary));
}

.site-slopcode__participant--you::before {
  content: "You:";
  font-weight: 600;
  color: hsl(var(--km-color-primary));
}

.site-slopcode__host-panel {
  border-top: 1px dashed hsl(var(--km-color-border));
  margin-top: 1.25rem;
  padding-top: 1.25rem;
}

.site-slopcode__host-panel-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: hsl(var(--km-color-fg) / 0.6);
  margin-bottom: 0.5rem;
}

.site-slopcode__voting-content {
  background-color: hsl(var(--km-color-code-bg, var(--km-color-muted-bg)));
  border: 1px solid hsl(var(--km-color-code-border, var(--km-color-border)));
  border-radius: var(--km-radius-normal, 0.75rem);
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  white-space: pre-wrap;
  font-size: 0.95rem;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.site-slopcode__voting-progress {
  font-size: 0.8rem;
  color: hsl(var(--km-color-fg) / 0.6);
  margin-bottom: 1rem;
}

.site-slopcode__voting-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.site-slopcode__voting-verdict-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border-radius: var(--km-radius-normal, 0.75rem);
  border: 2px solid hsl(var(--km-color-border));
  background-color: transparent;
  color: hsl(var(--km-color-fg));
  padding: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition-property: border-color, background-color;
  transition-timing-function: var(--km-ease-smooth, ease);
  transition-duration: var(--km-duration-fast, 120ms);
}

.site-slopcode__voting-verdict-btn--ai.site-slopcode__voting-verdict-btn--selected {
  border-color: hsl(var(--km-color-red, 0 70% 55%));
  background-color: hsl(var(--km-color-red, 0 70% 55%) / 0.12);
}

.site-slopcode__voting-verdict-btn--human.site-slopcode__voting-verdict-btn--selected {
  border-color: hsl(var(--km-color-green, 140 55% 45%));
  background-color: hsl(var(--km-color-green, 140 55% 45%) / 0.12);
}

.site-slopcode__voting-tally {
  font-size: 0.85rem;
  color: hsl(var(--km-color-fg) / 0.7);
  margin: 1rem 0;
}

.site-slopcode__host-vote-feed {
  list-style: none;
  margin: 0.5rem 0 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-height: 220px;
  overflow-y: auto;
}

.site-slopcode__host-vote-feed-item {
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--km-radius-normal, 0.75rem);
  background-color: hsl(var(--km-color-muted-bg, var(--km-color-bg)));
}

.site-slopcode__results-item {
  border: 1px solid hsl(var(--km-color-border));
  border-radius: var(--km-radius-normal, 0.75rem);
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}

.site-slopcode__results-item-content {
  white-space: pre-wrap;
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 0.75rem;
  max-height: 250px;
  overflow-y: auto;
}

.site-slopcode__results-item-tally {
  display: flex;
  gap: 1.25rem;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.site-slopcode__results-item-votes {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.site-slopcode__results-item-vote {
  font-size: 0.8rem;
  color: hsl(var(--km-color-fg) / 0.8);
  padding: 0.4rem 0.6rem;
  border-radius: var(--km-radius-normal, 0.75rem);
  background-color: hsl(var(--km-color-muted-bg, var(--km-color-bg)));
}

.site-slopcode__radio-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.site-slopcode__radio-label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.9rem;
  cursor: pointer;
}
"""


# ----------------------------------------------------------------------
# HTML shell
# ----------------------------------------------------------------------
#
# Five phase containers, all present from first load, toggled by JS
# via `.site-slopcode--hidden`. `{uid}` scopes every element id so two
# invocations of this directive on one page (not the current plan, but
# free to support given the existing theme's per-instance-uid
# precedent in the archived interpreter extension) wouldn't collide.

_HTML_TEMPLATE: t.Final[str] = """
<section id="{uid}-phase-choice" class="site-slopcode__card">
  <h3 class="site-slopcode__title">Slopcode</h3>
  <p class="site-slopcode__subtitle">Got a room code? Join below -- no sign-in needed.</p>
  <div class="site-slopcode__field">
    <label class="site-slopcode__label" for="{uid}-choice-room-code">Room code</label>
    <input class="site-slopcode__input" id="{uid}-choice-room-code" type="text" maxlength="5" style="text-transform: uppercase;">
  </div>
  <div class="site-slopcode__field">
    <label class="site-slopcode__label" for="{uid}-choice-display-name">Display name (optional)</label>
    <input class="site-slopcode__input" id="{uid}-choice-display-name" type="text">
  </div>
  <button class="site-slopcode__button" id="{uid}-choice-join" type="button">Join room</button>
  <p class="site-slopcode__error" id="{uid}-choice-error"></p>

  <div class="site-slopcode__host-panel">
    <p class="site-slopcode__host-panel-label">Hosting? Sign in to create a room</p>
    <div class="site-slopcode__field">
      <label class="site-slopcode__label" for="{uid}-login-username">Username</label>
      <input class="site-slopcode__input" id="{uid}-login-username" type="text" autocomplete="username">
    </div>
    <div class="site-slopcode__field">
      <label class="site-slopcode__label" for="{uid}-login-password">Password</label>
      <input class="site-slopcode__input" id="{uid}-login-password" type="password" autocomplete="current-password">
    </div>
    <button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-login-submit" type="button">Sign in</button>
    <p class="site-slopcode__error" id="{uid}-login-error"></p>

    <div class="site-slopcode__field site-slopcode--hidden" id="{uid}-host-create-fields">
      <label class="site-slopcode__label" for="{uid}-choice-headcount">Expected number of participants</label>
      <input class="site-slopcode__input" id="{uid}-choice-headcount" type="number" min="1" value="4">
      <button class="site-slopcode__button" id="{uid}-choice-create" type="button">Create a room</button>
    </div>
  </div>
</section>

<section id="{uid}-phase-lobby" class="site-slopcode__card site-slopcode--hidden">
  <h3 class="site-slopcode__title">Waiting room</h3>
  <div class="site-slopcode__lobby-share">Room code: <strong id="{uid}-lobby-room-code"></strong></div>
  <p class="site-slopcode__subtitle">You are: <strong id="{uid}-my-display-name"></strong></p>
  <p class="site-slopcode__lobby-count" id="{uid}-lobby-count"></p>
  <ul class="site-slopcode__participant-list" id="{uid}-lobby-participants"></ul>
  <div class="site-slopcode__host-panel site-slopcode--hidden" id="{uid}-lobby-host-panel">
    <p class="site-slopcode__host-panel-label">Host controls</p>
    <button class="site-slopcode__button" id="{uid}-lobby-start-submission" type="button">Start submission phase</button>
  </div>
</section>

<section id="{uid}-phase-submission" class="site-slopcode__card site-slopcode--hidden">
  <h3 class="site-slopcode__title">Paste your text</h3>
  <p class="site-slopcode__subtitle">Nobody else can see this until voting starts.</p>
  <div class="site-slopcode__field">
    <textarea class="site-slopcode__textarea" id="{uid}-submission-textarea" placeholder="Paste content here..."></textarea>
  </div>
  <button class="site-slopcode__button" id="{uid}-submission-submit" type="button">Submit</button>
  <p class="site-slopcode__error" id="{uid}-submission-error"></p>
  <div class="site-slopcode__host-panel site-slopcode--hidden" id="{uid}-submission-host-panel">
    <p class="site-slopcode__host-panel-label">Host controls</p>
    <p class="site-slopcode__lobby-count" id="{uid}-submission-host-count"></p>
    <button class="site-slopcode__button" id="{uid}-submission-start-voting" type="button">Start voting phase</button>
  </div>
</section>

<section id="{uid}-phase-voting" class="site-slopcode__card site-slopcode--hidden">
  <h3 class="site-slopcode__title">Vote: AI or Human?</h3>
  <div id="{uid}-voting-active">
    <p class="site-slopcode__voting-progress" id="{uid}-voting-progress"></p>
    <div class="site-slopcode__voting-content" id="{uid}-voting-content"></div>
    <div class="site-slopcode__voting-actions">
      <button class="site-slopcode__voting-verdict-btn site-slopcode__voting-verdict-btn--ai" id="{uid}-voting-vote-ai" type="button">AI</button>
      <button class="site-slopcode__voting-verdict-btn site-slopcode__voting-verdict-btn--human" id="{uid}-voting-vote-human" type="button">Human</button>
    </div>
    <div class="site-slopcode__field">
      <label class="site-slopcode__label" for="{uid}-voting-reason">Why do you think so?</label>
      <textarea class="site-slopcode__textarea" id="{uid}-voting-reason" style="min-height: 80px;"></textarea>
    </div>
    <button class="site-slopcode__button" id="{uid}-voting-submit" type="button" disabled>Submit vote</button>
    <p class="site-slopcode__error" id="{uid}-voting-error"></p>
  </div>
  <div id="{uid}-voting-waiting" class="site-slopcode--hidden">
    <p class="site-slopcode__subtitle">You're done voting. Waiting for everyone else to finish...</p>
  </div>
  <p class="site-slopcode__voting-tally" id="{uid}-voting-tally"></p>
  <div class="site-slopcode__host-panel site-slopcode--hidden" id="{uid}-voting-host-panel">
    <p class="site-slopcode__host-panel-label">Host view -- votes as they arrive</p>
    <ul class="site-slopcode__host-vote-feed" id="{uid}-voting-host-feed"></ul>
  </div>
</section>

<section id="{uid}-phase-results" class="site-slopcode__card site-slopcode--hidden">
  <h3 class="site-slopcode__title">Results</h3>
  <p class="site-slopcode__voting-progress" id="{uid}-results-progress"></p>
  <div class="site-slopcode__results-item-content" id="{uid}-results-content"></div>
  <div class="site-slopcode__results-item-tally" id="{uid}-results-tally"></div>
  <button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-results-toggle-comments" type="button">Read comments</button>
  <ul class="site-slopcode__results-item-votes site-slopcode--hidden" id="{uid}-results-votes"></ul>
  <div class="site-slopcode__voting-actions" style="margin-top: 1.25rem;">
    <button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-results-prev" type="button">Previous</button>
    <button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-results-next" type="button">Next</button>
  </div>
  <div class="site-slopcode__host-panel site-slopcode--hidden" id="{uid}-results-host-panel">
    <p class="site-slopcode__host-panel-label">Host controls</p>
    <button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-restart-session" type="button">Restart session for everyone</button>
  </div>
</section>

<p class="site-slopcode__error" id="{uid}-connection-status"></p>
<button class="site-slopcode__button site-slopcode__button--secondary" id="{uid}-manual-resync" type="button" style="font-size: 0.75rem; padding: 0.35rem 0.9rem;">Screen stuck? Refresh status</button>
"""


# ----------------------------------------------------------------------
# Client-side JS
# ----------------------------------------------------------------------
#
# Plain vanilla JS, no bundler/build step (this repo has none, and
# Alpine.js' availability elsewhere in the theme isn't reliable enough
# to depend on here) -- state lives in a handful of top-level `let`
# bindings, phases are toggled via one `showPhase()` function, and the
# only "polling" that ever happens is a single one-shot resync call
# right after a dropped SignalR connection reconnects -- never a
# periodic timer, since a forgotten open tab polling for days is
# exactly the kind of abuse the backend's cost guardrails are meant to
# rule out.

_JS_TEMPLATE: t.Final[str] = """
(function() {{
  const UID = "{uid}";
  const API_BASE = "{api_base_url}";
  const HEADCOUNT_MAX = {headcount_max};
  const STORAGE_KEY = "slopcode-session-" + UID;

  const $ = (id) => document.getElementById(UID + "-" + id);

  let hostToken = null;
  let roomCode = null;
  let participantId = null;
  let sessionToken = null;
  let isHost = false;
  let myDisplayName = null;
  let hasSubmitted = false;
  let selectedVerdict = null;
  let connection = null;
  let resultsItems = [];
  let resultsIndex = 0;
  let resultsShowingComments = false;

  function showPhase(phase) {{
    ["choice", "lobby", "submission", "voting", "results"].forEach((p) => {{
      const el = document.getElementById(UID + "-phase-" + p);
      if (el) el.classList.toggle("site-slopcode--hidden", p !== phase);
    }});
  }}

  function setStatus(message) {{
    const el = $("connection-status");
    if (el) el.textContent = message || "";
  }}

  function saveSession() {{
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({{
      roomCode, participantId, sessionToken, isHost, myDisplayName,
    }}));
  }}

  function clearSession() {{
    sessionStorage.removeItem(STORAGE_KEY);
    roomCode = participantId = sessionToken = myDisplayName = null;
    isHost = false;
  }}

  async function api(path, options) {{
    options = options || {{}};
    const headers = Object.assign({{ "Content-Type": "application/json" }}, options.headers || {{}});
    const response = await fetch(API_BASE + path, Object.assign({{}}, options, {{ headers }}));
    let body = null;
    try {{ body = await response.json(); }} catch (e) {{ /* empty body is fine */ }}
    if (!response.ok) {{
      const message = (body && body.error) || ("Request failed (" + response.status + ")");
      throw new Error(message);
    }}
    return body;
  }}

  // ---- Login ----

  $("login-submit").addEventListener("click", async () => {{
    const username = $("login-username").value.trim();
    const password = $("login-password").value;
    $("login-error").textContent = "";
    try {{
      const result = await api("/login", {{
        method: "POST",
        body: JSON.stringify({{ username, password }}),
      }});
      hostToken = result.hostToken;
      $("host-create-fields").classList.remove("site-slopcode--hidden");
      $("login-submit").disabled = true;
      $("login-username").disabled = true;
      $("login-password").disabled = true;
    }} catch (err) {{
      $("login-error").textContent = err.message;
    }}
  }});

  // ---- Create / join room ----

  $("choice-create").addEventListener("click", async () => {{
    $("choice-error").textContent = "";
    const headcount = parseInt($("choice-headcount").value, 10);
    if (!headcount || headcount < 1 || headcount > HEADCOUNT_MAX) {{
      $("choice-error").textContent = "Enter a headcount from 1 to " + HEADCOUNT_MAX + ".";
      return;
    }}
    try {{
      const result = await api("/rooms", {{
        method: "POST",
        body: JSON.stringify({{ hostToken, expectedHeadcount: headcount }}),
      }});
      roomCode = result.roomCode;
      participantId = result.participantId;
      sessionToken = result.sessionToken;
      isHost = true;
      myDisplayName = "Host";
      saveSession();
      await enterLobby();
    }} catch (err) {{
      $("choice-error").textContent = err.message;
    }}
  }});

  $("choice-join").addEventListener("click", async () => {{
    $("choice-error").textContent = "";
    const code = $("choice-room-code").value.trim().toUpperCase();
    const displayName = $("choice-display-name").value.trim();
    if (!code) {{
      $("choice-error").textContent = "Enter a room code.";
      return;
    }}
    try {{
      const result = await api("/rooms/" + code + "/join", {{
        method: "POST",
        body: JSON.stringify({{ displayName: displayName || null }}),
      }});
      roomCode = code;
      participantId = result.participantId;
      sessionToken = result.sessionToken;
      isHost = false;
      myDisplayName = result.displayName;
      saveSession();
      await enterLobby();
    }} catch (err) {{
      $("choice-error").textContent = err.message;
    }}
  }});

  // ---- Lobby ----

  async function enterLobby() {{
    await connectRealtime();
    // resyncState() sets the correct phase itself (lobby, submission,
    // or voting -- e.g. if this join was the last one needed and the
    // room already auto-started by the time this client catches up).
    // Don't force "lobby" afterward; that would silently overwrite it.
    await resyncState();
  }}

  function renderParticipants(participants, expectedHeadcount) {{
    const list = $("lobby-participants");
    list.innerHTML = "";
    participants.forEach((p) => {{
      const li = document.createElement("li");
      let className = "site-slopcode__participant";
      if (p.isHost) className += " site-slopcode__participant--host";
      if (p.participantId === participantId) className += " site-slopcode__participant--you";
      li.className = className;
      li.textContent = p.displayName;
      list.appendChild(li);
    }});
    $("lobby-count").textContent = participants.length + " of " + expectedHeadcount + " joined";
    $("lobby-room-code").textContent = roomCode;
    $("my-display-name").textContent = myDisplayName || "";
    $("lobby-host-panel").classList.toggle("site-slopcode--hidden", !isHost);
  }}

  $("lobby-start-submission").addEventListener("click", async () => {{
    try {{
      await api("/rooms/" + roomCode + "/force-start-submission", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken }}),
      }});
      // Don't wait on the PhaseChanged broadcast to update our own
      // screen -- the action already succeeded server-side, so pull
      // fresh state directly rather than depend on a round-trip
      // message that may be delayed, dropped, or racing a fresh
      // SignalR connection that hasn't finished joining its group yet.
      await resyncState();
    }} catch (err) {{
      setStatus(err.message);
    }}
  }});

  // ---- Submission ----

  $("submission-submit").addEventListener("click", async () => {{
    $("submission-error").textContent = "";
    const content = $("submission-textarea").value.trim();
    if (!content) {{
      $("submission-error").textContent = "Paste something first.";
      return;
    }}
    try {{
      await api("/rooms/" + roomCode + "/submit", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken, content }}),
      }});
      hasSubmitted = true;
      $("submission-submit").disabled = true;
      $("submission-textarea").disabled = true;
    }} catch (err) {{
      $("submission-error").textContent = err.message;
    }}
  }});

  $("submission-start-voting").addEventListener("click", async () => {{
    try {{
      await api("/rooms/" + roomCode + "/force-start-voting", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken }}),
      }});
      await resyncState();
    }} catch (err) {{
      setStatus(err.message);
    }}
  }});

  function enterSubmissionPhase() {{
    showPhase("submission");
    // Mirrors the equivalent toggle in renderVotingItem() for the
    // voting phase's host panel -- without this, the host-only live
    // submission count and "Start voting phase" button stay
    // permanently hidden, since the section starts hidden in the
    // markup and nothing else ever un-hides it.
    $("submission-host-panel").classList.toggle("site-slopcode--hidden", !isHost);
  }}

  // ---- Voting ----

  function selectVerdict(verdict) {{
    selectedVerdict = verdict;
    $("voting-vote-ai").classList.toggle("site-slopcode__voting-verdict-btn--selected", verdict === "ai");
    $("voting-vote-human").classList.toggle("site-slopcode__voting-verdict-btn--selected", verdict === "human");
    $("voting-submit").disabled = false;
  }}

  $("voting-vote-ai").addEventListener("click", () => selectVerdict("ai"));
  $("voting-vote-human").addEventListener("click", () => selectVerdict("human"));

  $("voting-submit").addEventListener("click", async () => {{
    $("voting-error").textContent = "";
    if (!selectedVerdict) return;
    const reason = $("voting-reason").value.trim();
    $("voting-submit").disabled = true;
    $("voting-vote-ai").disabled = true;
    $("voting-vote-human").disabled = true;
    $("voting-reason").disabled = true;
    try {{
      const next = await api("/rooms/" + roomCode + "/vote", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken, verdict: selectedVerdict, reason }}),
      }});
      renderVotingItem(next);
    }} catch (err) {{
      $("voting-error").textContent = err.message;
      $("voting-submit").disabled = false;
      $("voting-vote-ai").disabled = false;
      $("voting-vote-human").disabled = false;
      $("voting-reason").disabled = false;
    }}
  }});

  function renderVotingItem(data) {{
    $("voting-host-panel").classList.toggle("site-slopcode--hidden", !isHost);

    if (data.done) {{
      $("voting-active").classList.add("site-slopcode--hidden");
      $("voting-waiting").classList.remove("site-slopcode--hidden");
      return;
    }}
    $("voting-active").classList.remove("site-slopcode--hidden");
    $("voting-waiting").classList.add("site-slopcode--hidden");

    $("voting-progress").textContent = "Item " + (data.itemIndex + 1) + " of " + data.totalItems;
    $("voting-content").textContent = data.content;
    selectedVerdict = null;
    $("voting-vote-ai").classList.remove("site-slopcode__voting-verdict-btn--selected");
    $("voting-vote-human").classList.remove("site-slopcode__voting-verdict-btn--selected");
    $("voting-vote-ai").disabled = false;
    $("voting-vote-human").disabled = false;
    $("voting-reason").disabled = false;
    $("voting-reason").value = "";
    $("voting-submit").disabled = true;
    $("voting-error").textContent = "";
  }}

  // ---- Results ----

  async function loadResults() {{
    $("results-host-panel").classList.toggle("site-slopcode--hidden", !isHost);
    try {{
      const result = await api("/rooms/" + roomCode + "/results", {{
        headers: {{ "x-session-token": sessionToken }},
      }});
      resultsItems = result.items;
      resultsIndex = 0;
      resultsShowingComments = false;
      renderResultsItem();
    }} catch (err) {{
      setStatus(err.message);
    }}
  }}

  function renderResultsItem() {{
    if (!resultsItems.length) {{
      $("results-progress").textContent = "No submissions.";
      $("results-content").textContent = "";
      $("results-tally").textContent = "";
      $("results-votes").innerHTML = "";
      $("results-prev").disabled = true;
      $("results-next").disabled = true;
      return;
    }}
    const item = resultsItems[resultsIndex];
    $("results-progress").textContent = "Item " + (resultsIndex + 1) + " of " + resultsItems.length;
    $("results-content").textContent = item.content;
    $("results-tally").textContent = "AI: " + item.aiVotes + "   Human: " + item.humanVotes;

    const votesList = $("results-votes");
    votesList.innerHTML = "";
    item.votes.forEach((v) => {{
      const li = document.createElement("li");
      li.className = "site-slopcode__results-item-vote";
      li.textContent = v.voterDisplayName + " voted " + v.verdict + " -- \\"" + v.reason + "\\"";
      votesList.appendChild(li);
    }});
    votesList.classList.toggle("site-slopcode--hidden", !resultsShowingComments);
    $("results-toggle-comments").textContent = resultsShowingComments ? "Hide comments" : "Read comments";

    $("results-prev").disabled = resultsIndex === 0;
    $("results-next").disabled = resultsIndex === resultsItems.length - 1;
  }}

  $("results-toggle-comments").addEventListener("click", () => {{
    resultsShowingComments = !resultsShowingComments;
    renderResultsItem();
  }});

  $("results-prev").addEventListener("click", () => {{
    if (resultsIndex === 0) return;
    resultsIndex -= 1;
    resultsShowingComments = false;
    renderResultsItem();
  }});

  $("results-next").addEventListener("click", () => {{
    if (resultsIndex >= resultsItems.length - 1) return;
    resultsIndex += 1;
    resultsShowingComments = false;
    renderResultsItem();
  }});

  // ---- Realtime (SignalR) ----

  async function connectRealtime() {{
    if (connection) return;
    const negotiateInfo = await api("/negotiate", {{
      method: "POST",
      headers: {{ "x-participant-id": participantId }},
      body: JSON.stringify({{ roomCode, participantId }}),
    }}).catch(() => null);
    if (!negotiateInfo) {{
      setStatus("Couldn't connect to realtime updates. Refresh to retry.");
      return;
    }}
    connection = new signalR.HubConnectionBuilder()
      .withUrl(negotiateInfo.url, {{ accessTokenFactory: () => negotiateInfo.accessToken }})
      .withAutomaticReconnect()
      .build();

    connection.on("PresenceUpdated", (data) => renderParticipants(data.participants, data.expectedHeadcount));
    connection.on("PhaseChanged", async (data) => {{
      if (data.phase === "submission") enterSubmissionPhase();
      if (data.phase === "voting") {{
        showPhase("voting");
        const item = await api("/rooms/" + roomCode + "/voting-item", {{
          headers: {{ "x-session-token": sessionToken }},
        }});
        renderVotingItem(item);
      }}
      if (data.phase === "results") {{ showPhase("results"); loadResults(); }}
    }});
    connection.on("SubmissionArrived", (data) => {{
      if (!isHost) return;
      $("submission-host-count").textContent = data.submittedCount + " of " + data.totalParticipants + " submitted";
    }});
    connection.on("VoteTallyUpdated", (data) => {{
      $("voting-tally").textContent = data.votedCount + " of " + data.totalParticipants + " voted on that item";
    }});
    connection.on("VoteCastHostView", (data) => {{
      if (!isHost) return;
      const li = document.createElement("li");
      li.className = "site-slopcode__host-vote-feed-item";
      li.textContent = data.voterDisplayName + ": " + data.verdict + " -- \\"" + data.reason + "\\"";
      $("voting-host-feed").appendChild(li);
    }});
    connection.on("ResultsReady", () => loadResults());
    connection.on("RoomRestarted", () => {{
      clearSession();
      window.location.reload();
    }});

    async function joinSignalRGroups() {{
      await api("/rooms/" + roomCode + "/join-groups", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken, participantId }}),
      }});
    }}

    connection.onreconnecting(() => setStatus("Reconnecting..."));
    connection.onreconnected(async () => {{
      // A reconnect gets a brand-new underlying connection id -- group
      // membership doesn't carry over, so without rejoining here this
      // client would silently stop receiving any broadcast (phase
      // changes, results, everything) until the page is manually
      // reloaded, even though resyncState() below makes it LOOK caught
      // up at this one instant.
      await joinSignalRGroups();
      setStatus("");
      await resyncState();
    }});
    connection.onclose(() => setStatus("Disconnected. Refresh the page to rejoin."));

    await connection.start();
    await joinSignalRGroups();
  }}

  async function resyncState() {{
    try {{
      const state = await api("/rooms/" + roomCode + "/state", {{
        headers: {{ "x-session-token": sessionToken }},
      }});
      isHost = state.isHost;
      const me = state.participants.find((p) => p.participantId === participantId);
      if (me) {{
        myDisplayName = me.displayName;
        saveSession();
      }}
      renderParticipants(state.participants, state.expectedHeadcount);
      if (state.phase === "lobby") showPhase("lobby");
      if (state.phase === "submission") enterSubmissionPhase();
      if (state.phase === "voting") {{
        showPhase("voting");
        const item = await api("/rooms/" + roomCode + "/voting-item", {{
          headers: {{ "x-session-token": sessionToken }},
        }});
        renderVotingItem(item);
      }}
      if (state.phase === "results") {{ showPhase("results"); loadResults(); }}
    }} catch (err) {{
      setStatus(err.message);
    }}
  }}

  $("manual-resync").addEventListener("click", async () => {{
    if (!roomCode) return;
    setStatus("Refreshing...");
    await resyncState();
    setStatus("");
  }});

  $("restart-session").addEventListener("click", async () => {{
    if (!window.confirm("This ends the session for everyone and returns them to the start. Continue?")) return;
    try {{
      await api("/rooms/" + roomCode + "/restart", {{
        method: "POST",
        body: JSON.stringify({{ sessionToken }}),
      }});
    }} catch (err) {{
      setStatus(err.message);
    }}
  }});

  // ---- Resume a session across page refreshes ----

  (async function resumeIfPossible() {{
    const saved = sessionStorage.getItem(STORAGE_KEY);
    if (!saved) {{ showPhase("choice"); return; }}
    try {{
      const parsed = JSON.parse(saved);
      roomCode = parsed.roomCode;
      participantId = parsed.participantId;
      sessionToken = parsed.sessionToken;
      isHost = parsed.isHost;
      myDisplayName = parsed.myDisplayName || null;
      await connectRealtime();
      // resyncState() sets the correct phase itself -- don't force
      // "lobby" here, that would silently overwrite it (same bug
      // fixed in enterLobby() above).
      await resyncState();
    }} catch (err) {{
      clearSession();
      showPhase("choice");
    }}
  }})();
}})();
"""
