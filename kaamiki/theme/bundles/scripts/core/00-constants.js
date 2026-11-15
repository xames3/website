/*
Core Script
===========

Author: Akshay Mestry <xa@mes3.dev>
Created on: 17 October 2026
Last updated on: 11 November 2026
*/

// NOTE(xames3): The four scripts share one `window.Kaamiki` and load in
// this order: core, animations, theme, explainer. Each takes what it
// needs from the ones before it, and theme starts everything. Explainer
// is only on pages with a code-explain or code-version and starts its own.
// The order is set in the scripts tuple of
// https://github.com/xames3/website/blob/main/kaamiki/__init__.py
(() => {
    'use strict';

    const HASH_SETTLE_MS = 2600;
    const FETCH_TIMEOUT_MS = 8000;
    const GLIDE_STOPS = ['wheel', 'touchstart', 'pointerdown', 'keydown'];
    const GLIDE_KEYS = new Set([
        'ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' ',
    ]);
    const GLIDE_BASE_MS = 380;
    const GLIDE_PX_FACTOR = 0.12;
    const GLIDE_MIN_MS = 520;
    const GLIDE_MAX_MS = 1100;
    const FOCUSABLE = 'a[href], button, input, select, textarea, summary, '
        + 'iframe, [tabindex]';
    const ICON_ONLY = '.km-header__menu-toggle > i, .km-search__submit > i, '
        + '.km-scrolltop > i';
    const REVEAL_WAITING = 'km-page-reveal-item';
    const REVEAL_SHOWN = 'km-page-reveal-item--shown';
    const root = document.documentElement;
    const STRINGS = JSON.parse(root.dataset.kmStrings);
    const MARKS = JSON.parse(root.dataset.kmIcons);

