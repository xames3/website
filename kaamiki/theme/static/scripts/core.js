// NOTE(xames3): The four scripts share one `window.Kaamiki` and load in
// this order: core, animations, explainer, theme. Each takes what it
// needs from the ones before it, and theme starts everything.
(() => {
    'use strict';

    const HASH_SETTLE_MS = 2600;
    const FETCH_TIMEOUT_MS = 8000;
    const FOCUSABLE = 'a[href], button, input, select, textarea, summary, iframe, [tabindex]';
    const REVEAL_WAITING = 'km-page-reveal-item';
    const REVEAL_SHOWN = 'km-page-reveal-item--shown';
    const root = document.documentElement;
    const STRINGS = JSON.parse(root.dataset.kmStrings);

    function say(key, values = {}) {
        return STRINGS[key].replace(/\{(\w+)\}/g, (match, name) => (name in values ? values[name] : match));
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
        const value = raw.endsWith('ms') ? parseFloat(raw) : parseFloat(raw) * 1000;
        durationCache.set(name, value);
        return value;
    }

    function springProgress() {
        const raw = getCssVar('--km-spring-smooth');
        const points = raw.startsWith('linear(') ? raw.slice(7, -1).split(',').map(Number) : null;
        // NOTE(xames3): the last two stops of the spring jump to 1; stop at
        // the rest value so the reels land without a snap or a stuck blur.
        const last = points ? points.length - 3 : 0;
        return (time) => {
            if (!points) return 1 - (1 - time) ** 4;
            const at = time * last;
            const low = Math.min(Math.floor(at), last - 1);
            return (points[low] + (points[low + 1] - points[low]) * (at - low)) / points[last];
        };
    }

    const TIMING = {
        dropdownMin: () => getDurationMs('--km-duration-dropdown-min'),
        dropdownMax: () => getDurationMs('--km-duration-dropdown-max'),
        revealStep: () => getDurationMs('--km-reveal-step'),
        tooltipHold: () => getDurationMs('--km-tooltip-hold'),
        fast: () => getDurationMs('--km-duration-fast'),
        showMoreHold: () => getDurationMs('--km-show-more-hold'),
        tickerDuration: () => getDurationMs('--km-ticker-duration'),
    };

    function headerHeight() {
        const header = document.querySelector('.km-header');
        return header ? Math.ceil(header.getBoundingClientRect().height) : 0;
    }

    function afterReveal(node, fn) {
        const block = node.closest(`.${REVEAL_WAITING}:not(.${REVEAL_SHOWN})`);
        if (block) block.addEventListener('km:reveal', () => fn(node), { once: true });
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
            if (previous.classList.contains('km-pre-title-text')) return previous;
            const last = previous.lastElementChild;
            if (last && last.classList.contains('km-pre-title-text')) return last;
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
        return Math.max(0, top - headerHeight());
    }

    function isModifiedClick(event) {
        return event.button !== 0
            || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
    }

    function settleHash() {
        if (location.hash.length <= 1) return;
        const target = document.getElementById(decodeId(location.hash.slice(1)));
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
        field.style.cssText = 'position: fixed; top: 0; left: 0; opacity: 0; pointer-events: none;';
        document.body.append(field);
        field.select();
        let copied = false;
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
            return navigator.clipboard.writeText(text).then(() => true, () => copyByHand(text));
        }
        return Promise.resolve(copyByHand(text));
    }

    function clamp(value, low, high) {
        return Math.max(low, Math.min(high, value));
    }

    window.Kaamiki = {
        walkthroughs: [],
        FOCUSABLE,
        REVEAL_SHOWN,
        REVEAL_WAITING,
        TIMING,
        anchorTargetY,
        clamp,
        copyText,
        decodeId,
        fetchJson,
        getCssVar,
        getDurationMs,
        headerHeight,
        isModifiedClick,
        layoutTop,
        onScroll,
        onVisible,
        prefersReducedMotion,
        rafThrottle,
        say,
        settleHash,
        springProgress,
    };
})();
