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

    function say(key) {
        return STRINGS[key];
    }

    function makeIcon(key, ...classes) {
        if (!MARKS[key]) return null;
        const mark = document.createElement('i');
        mark.className = [MARKS[key], ...classes].join(' ');
        mark.setAttribute('aria-hidden', 'true');
        return mark;
    }

    function attempt(fn) {
        try {
            return fn();
        } catch {
            return undefined;
        }
    }

    function decodeId(value) {
        try {
            return decodeURIComponent(value);
        } catch {
            return value;
        }
    }

    function prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    const scrollSubscribers = new Set();

    function onScroll(fn) {
        if (!scrollSubscribers.size) {
            window.addEventListener('scroll', () => {
                for (const subscriber of scrollSubscribers) subscriber();
            }, { passive: true });
        }
        scrollSubscribers.add(fn);
        fn();
    }

    function rafThrottle(fn) {
        let queued = false;
        return function throttled(...args) {
            if (queued) return;
            queued = true;
            requestAnimationFrame(() => {
                queued = false;
                fn.apply(this, args);
            });
        };
    }

    const durationCache = new Map();

    function getCssVar(name) {
        return getComputedStyle(root).getPropertyValue(name).trim();
    }

    function getDurationMs(name) {
        if (durationCache.has(name)) return durationCache.get(name);
        const raw = getCssVar(name);
        const value = raw.endsWith('ms')
            ? parseFloat(raw)
            : parseFloat(raw) * 1000;
        durationCache.set(name, value);
        return value;
    }

    // https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/cubic-bezier
    const SMOOTH_CURVE = [0.32, 0.72, 0, 1];

    function springProgress() {
        const [x1, y1, x2, y2] = SMOOTH_CURVE;
        const axis = (a, b, t) => (
            3 * a * (1 - t) ** 2 * t + 3 * b * (1 - t) * t ** 2 + t ** 3
        );
        return (time) => {
            if (time <= 0) return 0;
            if (time >= 1) return 1;
            let low = 0;
            let high = 1;
            for (let i = 0; i < 32; i += 1) {
                const middle = (low + high) / 2;
                if (axis(x1, x2, middle) < time) low = middle;
                else high = middle;
            }
            return axis(y1, y2, (low + high) / 2);
        };
    }

    const TIMING = {
        accordionMin: () => getDurationMs('--km-duration-accordion-min'),
        accordionMax: () => getDurationMs('--km-duration-accordion-max'),
        revealStep: () => getDurationMs('--km-reveal-step'),
        revealDuration: () => getDurationMs('--km-reveal-duration'),
        titleStep: () => getDurationMs('--km-title-step'),
        tooltipHold: () => getDurationMs('--km-tooltip-hold'),
        fast: () => getDurationMs('--km-duration-fast'),
        normal: () => getDurationMs('--km-duration-normal'),
        slow: () => getDurationMs('--km-duration-slow'),
        clamp: () => getDurationMs('--km-duration-clamp'),
        showMoreHold: () => getDurationMs('--km-show-more-hold'),
        tickerDuration: () => getDurationMs('--km-ticker-duration'),
        rotateHold: () => getDurationMs('--km-rotate-hold'),
        rotateResize: () => getDurationMs('--km-rotate-resize'),
        codeSwap: () => getDurationMs('--km-code-explain-swap'),
    };

    let glideStop = null;

    function glideTo(targetY) {
        const startY = window.scrollY;
        const endY = clamp(
            targetY,
            0,
            Math.max(0, root.scrollHeight - window.innerHeight),
        );
        if (Math.abs(endY - startY) < 1) return Promise.resolve(true);
        if (prefersReducedMotion()) {
            window.scrollTo(0, endY);
            return Promise.resolve(true);
        }
        glideStop?.();
        const distance = endY - startY;
        const duration = clamp(
            GLIDE_BASE_MS + Math.abs(distance) * GLIDE_PX_FACTOR,
            GLIDE_MIN_MS,
            GLIDE_MAX_MS,
        );
        const spring = springProgress();
        return new Promise((resolve) => {
            let frame = 0;
            const began = performance.now();
            const finish = (arrived) => {
                cancelAnimationFrame(frame);
                GLIDE_STOPS.forEach((type) => (
                    window.removeEventListener(type, stop, true)
                ));
                glideStop = null;
                resolve(arrived);
            };
            const stop = (event) => {
                if (event?.type === 'keydown'
                    && !GLIDE_KEYS.has(event.key)) return;
                if (event?.type === 'wheel'
                    && !event.deltaX && !event.deltaY) return;
                finish(false);
            };
            const step = (now) => {
                const time = clamp((now - began) / duration, 0, 1);
                window.scrollTo({
                    top: startY + distance * spring(time),
                    behavior: 'instant',
                });
                if (time === 1) finish(true);
                else frame = requestAnimationFrame(step);
            };
            glideStop = stop;
            GLIDE_STOPS.forEach((type) => window.addEventListener(
                type,
                stop,
                { capture: true, passive: true },
            ));
            frame = requestAnimationFrame(step);
        });
    }

    function stopGlide() {
        glideStop?.();
    }

    function headerHeight() {
        const header = document.querySelector('.km-header');
        return header ? Math.ceil(header.getBoundingClientRect().height) : 0;
    }

    function afterReveal(node, fn) {
        const block = node.closest(`.${REVEAL_WAITING}:not(.${REVEAL_SHOWN})`);
        if (block) {
            block.addEventListener('km:reveal', () => fn(node), { once: true });
        }
        else fn(node);
    }

    function onVisible(nodes, onEnter, options = { rootMargin: '200px' }) {
        const list = Array.from(nodes);
        if (!list.length) return;
        const observer = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (!entry.isIntersecting) continue;
                observer.unobserve(entry.target);
                afterReveal(entry.target, onEnter);
            }
        }, options);
        list.forEach((node) => observer.observe(node));
    }

    async function fetchJson(url) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
        try {
            const response = await fetch(url, { signal: controller.signal });
            return response.ok ? await response.json() : null;
        } catch {
            return null;
        } finally {
            clearTimeout(timer);
        }
    }

    function anchorHost(element) {
        const previous = element.previousElementSibling;
        if (previous) {
            if (previous.classList.contains('km-text--pre-section')) {
                return previous;
            }
            const last = previous.lastElementChild;
            if (last && last.classList.contains('km-text--pre-section')) {
                return last;
            }
        }
        return element;
    }

    function layoutTop(element) {
        let y = 0;
        for (let node = element; node; node = node.offsetParent) {
            y += node.offsetTop;
        }
        return y;
    }

    function anchorTargetY(element) {
        const host = anchorHost(element);
        const top = host.offsetParent
            ? layoutTop(host)
            : window.scrollY + host.getBoundingClientRect().top;
        const margin = parseFloat(getComputedStyle(host).scrollMarginTop) || 0;
        return Math.max(0, top - Math.max(headerHeight(), margin));
    }

    function isModifiedClick(event) {
        return event.button !== 0
            || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
    }

    function settleHash() {
        if (location.hash.length <= 1) return;
        const target = document.getElementById(
            decodeId(location.hash.slice(1)),
        );
        if (!target) return;

        let cancelled = false;
        const observer = new ResizeObserver(() => requestAnimationFrame(apply));
        const stop = () => {
            cancelled = true;
            observer.disconnect();
        };
        const apply = () => {
            if (cancelled) return;
            const previousBehavior = root.style.scrollBehavior;
            root.style.scrollBehavior = 'auto';
            window.scrollTo(0, anchorTargetY(target));
            root.style.scrollBehavior = previousBehavior || '';
        };

        for (const type of ['wheel', 'touchmove', 'keydown']) {
            window.addEventListener(type, stop, { passive: true, once: true });
        }

        requestAnimationFrame(apply);
        observer.observe(document.documentElement);
        const finish = () => {
            apply();
            document.fonts.ready.then(apply);
            setTimeout(stop, HASH_SETTLE_MS);
        };
        if (document.readyState === 'complete') finish();
        else window.addEventListener('load', finish, { once: true });
    }

    function copyByHand(text) {
        const field = document.createElement('textarea');
        const active = document.activeElement;
        field.value = text;
        field.setAttribute('readonly', '');
        field.style.cssText = 'position: fixed; top: 0; left: 0; opacity: 0; '
            + 'pointer-events: none;';
        document.body.append(field);
        field.select();
        let copied;
        try {
            copied = document.execCommand('copy');
        } catch {
            copied = false;
        }
        field.remove();
        active?.focus?.({ preventScroll: true });
        return copied;
    }

    function copyText(text) {
        if (window.isSecureContext && navigator.clipboard?.writeText) {
            return navigator.clipboard.writeText(text)
                .then(() => true, () => copyByHand(text));
        }
        return Promise.resolve(copyByHand(text));
    }

    const liveRegion = document.createElement('div');
    liveRegion.className = 'sr-only';
    liveRegion.setAttribute('role', 'status');
    document.body.append(liveRegion);
    let announcing = 0;

    function announce(message) {
        window.clearTimeout(announcing);
        liveRegion.textContent = message;
        announcing = window.setTimeout(() => {
            liveRegion.textContent = '';
        }, TIMING.tooltipHold());
    }

    function clamp(value, low, high) {
        return Math.max(low, Math.min(high, value));
    }

    function markMissingIcons() {
        const icons = Array.from(document.querySelectorAll(ICON_ONLY))
            .filter((icon) => icon.getClientRects().length);
        const bare = icons.length > 0 && icons.every((icon) => (
            ['none', 'normal'].includes(
                getComputedStyle(icon, '::before').content,
            )
        ));
        document.fonts.ready.then(() => {
            const failed = Array.from(document.fonts).some((face) => (
                face.status === 'error' && /Font Awesome/.test(face.family)
            ));
            root.classList.toggle('km-document--no-icons', bare || failed);
        });
    }

    window.addEventListener('load', markMissingIcons, { once: true });

    window.Kaamiki = {
        codeExplains: [],
        FOCUSABLE,
        REVEAL_SHOWN,
        REVEAL_WAITING,
        TIMING,
        anchorTargetY,
        announce,
        attempt,
        clamp,
        copyText,
        decodeId,
        fetchJson,
        getCssVar,
        glideTo,
        headerHeight,
        isModifiedClick,
        layoutTop,
        makeIcon,
        onScroll,
        onVisible,
        prefersReducedMotion,
        rafThrottle,
        say,
        settleHash,
        springProgress,
        stopGlide,
    };
})();
