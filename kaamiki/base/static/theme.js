const SCROLL_DURATION_MIN_MS = 300;
const SCROLL_DURATION_MAX_MS = 1800;
const ANCHOR_SCROLL_PX_FACTOR = 0.6;
const ANCHOR_SCROLL_DIST_CAP_MS = 400;
const HEADER_OFFSET_DEFAULT_PX = 40;
const ANCHOR_EXTRA_OFFSET_DEFAULT_PX = 12;
const HEADER_BORDER_SCROLL_THRESHOLD = 250;
const HASH_SETTLE_MS = 2600;
const CLAMP_SLACK_PX = 48;
const CLAMP_SETTLE_MS = 60;
const CLAMP_GAP_PX = 32;
const CLAMP_MIN_PX = 320;
const DROPDOWN_OPEN_DELAY_MS = 40;
const DROPDOWN_CLOSE_DELAY_MS = 140;
const DROPDOWN_PX_FACTOR = 0.9;
const FETCH_TIMEOUT_MS = 8000;
const ARTICLE_BG_FADE_MS = 600;
const ARTICLE_BG_INTERVAL_MS = 7000;
const CAL_ORIGIN = 'https://app.cal.com';
const TICKER_RADIX = 10;
const TICKER_MAX_LAPS = 4;
const TICKER_EASING = 'cubic-bezier(0.25, 1, 0.5, 1)';
const TICKER_BLUR = 'blur(1.5px)';
const TICKER_BLUR_AT = 0.4;
const FOCUSABLE = 'a[href], button, input, select, textarea, summary, iframe, [tabindex]';
const SIDEBAR_WIDE_PX = 1024;
const SCROLLTOP_AFTER_PX = 200;
const REVEAL_STEPS = 6;

const root = document.documentElement;

function ready(fn) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
        fn();
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

function getDurationMs(cssVar = '--km-duration-normal', fallback = 500) {
    if (durationCache.has(cssVar)) return durationCache.get(cssVar);
    let value = fallback;
    try {
        const raw = getComputedStyle(root).getPropertyValue(cssVar).trim();
        if (raw.endsWith('ms')) value = Math.max(0, parseFloat(raw));
        else if (raw.endsWith('s')) value = Math.max(0, parseFloat(raw) * 1000);
        else if (raw && !Number.isNaN(Number(raw))) value = Number(raw);
    } catch { /* keep fallback */ }
    durationCache.set(cssVar, value);
    return value;
}

const TIMING = {
    dropdownMin: () => getDurationMs('--km-duration-dropdown-min', 340),
    dropdownMax: () => getDurationMs('--km-duration-dropdown-max', 760),
    revealStep: () => getDurationMs('--km-reveal-step', 90),
    scrollMin: () => getDurationMs('--km-scroll-min', 450),
    scrollMax: () => getDurationMs('--km-scroll-max', 900),
    tooltipHold: () => getDurationMs('--km-tooltip-hold', 1800),
    showMoreHold: () => getDurationMs('--km-show-more-hold', 3000),
    walkthroughSwap: () => getDurationMs('--km-walkthrough-swap', 420),
    tickerBase: () => getDurationMs('--km-ticker-base', 1900),
    tickerStep: () => getDurationMs('--km-ticker-step', 280),
};

function easingToken(name, fallback) {
    return getComputedStyle(root).getPropertyValue(name).trim() || fallback;
}

function toPx(value, fallback) {
    if (!value) return fallback;
    const number = parseFloat(value);
    if (Number.isNaN(number)) return fallback;
    if (value.endsWith('rem')) {
        return number * (parseFloat(getComputedStyle(root).fontSize) || 16);
    }
    if (value.endsWith('em')) {
        return number * (parseFloat(getComputedStyle(document.body).fontSize) || 16);
    }
    return number;
}

function getCssVar(name) {
    try { return getComputedStyle(root).getPropertyValue(name).trim(); }
    catch { return ''; }
}

function getHeaderOffsetPx() {
    const fromTokens = toPx(getCssVar('--km-layout-header-offset'), HEADER_OFFSET_DEFAULT_PX)
        + toPx(getCssVar('--km-layout-anchor-offset'), ANCHOR_EXTRA_OFFSET_DEFAULT_PX);
    const header = document.querySelector('.site-header');
    const headerHeight = header ? Math.ceil(header.getBoundingClientRect().height) : 0;
    return Math.max(0, fromTokens, headerHeight);
}

function onVisible(nodes, onEnter, options = { rootMargin: '200px' }) {
    const list = Array.from(nodes);
    if (!list.length) return;
    if (!('IntersectionObserver' in window)) {
        list.forEach(onEnter);
        return;
    }
    const observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            observer.unobserve(entry.target);
            onEnter(entry.target);
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

function resolveTheme(mode) {
    if (mode === 'system') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return mode || 'light';
}

function syncThemeColor() {
    const meta = document.querySelector('meta[name="theme-color"]');
    const background = document.body && getComputedStyle(document.body).backgroundColor;
    if (meta && background) meta.setAttribute('content', background);
}

function applyTheme(mode) {
    const resolved = resolveTheme(mode);
    const commit = () => {
        root.setAttribute('data-theme', resolved);
        root.classList.toggle('dark', resolved === 'dark');
        syncThemeColor();
    };

    if (prefersReducedMotion() || typeof document.startViewTransition !== 'function') {
        commit();
        return;
    }

    root.classList.add('theme-switching');
    const transition = document.startViewTransition(commit);
    transition.finished
        .catch(() => { /* superseded by a newer switch */ })
        .finally(() => root.classList.remove('theme-switching'));
}

function initPrintColours() {
    let before = null;
    window.addEventListener('beforeprint', () => {
        before = root.getAttribute('data-theme');
        root.classList.add('no-transitions');
        root.setAttribute('data-theme', 'light');
        root.classList.remove('dark');
    });
    window.addEventListener('afterprint', () => {
        if (before === null) return;
        root.setAttribute('data-theme', before);
        root.classList.toggle('dark', before === 'dark');
        root.classList.remove('no-transitions');
        before = null;
    });
}

function initSystemColours() {
    if (root.dataset.colourMode !== 'system') return;
    let chosen = null;
    if (root.hasAttribute('data-colour-toggle')) {
        try { chosen = localStorage.getItem('darkMode'); } catch { /* storage unavailable */ }
    }
    if (chosen) return;
    window.matchMedia('(prefers-color-scheme: light)').addEventListener?.('change', (event) => {
        applyTheme(event.matches ? 'light' : 'dark');
    });
}

function initThemeToggle() {
    let mode = root.dataset.theme || 'dark';
    document.querySelectorAll('.site-footer__theme-toggle').forEach((button) => {
        button.addEventListener('click', () => {
            mode = mode === 'light' ? 'dark' : 'light';
            try { localStorage.setItem('darkMode', mode); } catch { /* storage unavailable */ }
            applyTheme(mode);
        });
    });
}

function initKeyboardModality() {
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Tab' || event.key.startsWith('Arrow')) root.setAttribute('data-keyboard', '');
    }, true);
    document.addEventListener('pointerdown', () => root.removeAttribute('data-keyboard'), true);
}

function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.site-header__menu-toggle');
    const backdrop = document.querySelector('.site-sidebar__backdrop');
    if (!sidebar || !toggle) return;
    let open = false;
    const stops = () => Array.from(sidebar.querySelectorAll(FOCUSABLE))
        .filter((element) => element.tabIndex >= 0 && element.getClientRects().length);
    const enter = (frames = 0) => {
        if (!open) return;
        if (getComputedStyle(sidebar).visibility !== 'visible' && frames < 30) {
            requestAnimationFrame(() => enter(frames + 1));
            return;
        }
        stops()[0]?.focus({ preventScroll: true });
    };
    const show = (next, restore = true, keyed = false) => {
        const inside = sidebar.contains(document.activeElement);
        open = next;
        document.body.classList.toggle('site-body--locked', next);
        sidebar.classList.toggle('site-sidebar--visible', next);
        toggle.setAttribute('aria-expanded', String(next));
        if (backdrop) backdrop.hidden = !next;
        if (next && keyed) requestAnimationFrame(() => enter());
        else if (!next && restore && inside) toggle.focus({ preventScroll: true });
    };
    toggle.addEventListener('click', (event) => show(!open, true, event.detail === 0));
    backdrop?.addEventListener('click', () => show(false));
    window.addEventListener('keydown', (event) => {
        if (!open) return;
        if (event.key === 'Escape') {
            show(false);
            return;
        }
        if (event.key !== 'Tab') return;
        const items = stops();
        if (!items.length) return;
        const at = items.indexOf(document.activeElement);
        const next = at < 0 ? 0 : at + (event.shiftKey ? -1 : 1);
        event.preventDefault();
        items[(next + items.length) % items.length].focus();
    });
    window.addEventListener('resize', () => {
        if (open && window.innerWidth >= SIDEBAR_WIDE_PX) show(false, false);
    }, { passive: true });
}

function initScrollTop() {
    const button = document.getElementById('scrolltop');
    if (!button) return;
    let last = 0;
    button.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    window.addEventListener('scroll', () => {
        const y = window.scrollY;
        const bottom = y + window.innerHeight >= root.scrollHeight - SCROLLTOP_AFTER_PX;
        button.classList.toggle(
            'site-scrolltop--hidden',
            !(y > last && (y > SCROLLTOP_AFTER_PX || bottom)),
        );
        last = Math.max(0, y);
    }, { passive: true });
}

function initShowMore() {
    const page = document.querySelector('.site-page--clamped');
    if (!page) return;
    const content = page.querySelector('.site-page__content');
    const shell = page.querySelector('[data-show-more]');
    const button = shell?.querySelector('.site-page__more-button');
    const label = button?.querySelector('.site-page__more-label');
    if (!content || !shell || !button) return;
    if (getComputedStyle(shell).display === 'none') {
        page.classList.remove('site-page--clamped');
        return;
    }

    let expanded = false;
    let timer = 0;
    let idleTimer = 0;
    let stirred = 0;

    const dock = () => toPx(getCssVar('--km-show-more-dock'), CLAMP_GAP_PX);
    const tail = () => button.getBoundingClientRect().height + dock();

    const fit = () => {
        const top = window.scrollY + content.getBoundingClientRect().top;
        const viewport = window.visualViewport?.height || window.innerHeight;
        const room = Math.max(CLAMP_MIN_PX, viewport - top - tail());
        page.style.setProperty('--km-show-more-clamp', `${Math.round(room)}px`);
    };

    let folded = true;
    const fold = (next) => {
        page.classList.toggle('site-page--clamped', next);
        if (next === folded) return;
        folded = next;
        document.dispatchEvent(new Event('km:fold'));
    };

    const settle = (next) => {
        window.clearTimeout(timer);
        page.classList.remove('site-page--clamping');
        fold(!next);
        content.style.maxHeight = '';
    };

    const measure = () => {
        content.style.maxHeight = '';
        page.classList.add('site-page--clamped');
        const collapsed = content.getBoundingClientRect().height;
        page.classList.remove('site-page--clamped');
        const full = content.getBoundingClientRect().height;
        return { collapsed, full };
    };

    fit();
    const { collapsed: first, full: whole } = measure();
    settle(false);
    if (whole - first < CLAMP_SLACK_PX) {
        page.classList.remove('site-page--clamped');
        shell.remove();
        return;
    }

    const keepInView = (collapsed) => {
        const top = window.scrollY + content.getBoundingClientRect().top;
        const viewport = window.visualViewport?.height || window.innerHeight;
        const targetY = Math.max(0, top + collapsed + tail() - viewport);
        const distance = window.scrollY - targetY;
        if (distance <= 0) return Promise.resolve();
        return smoothScrollTo(targetY, scrollDuration(distance));
    };

    let turn = 0;

    const clamp = (next, from, to) => {
        page.classList.toggle('site-page--clamped', !next);
        page.classList.add('site-page--clamping');
        content.style.maxHeight = `${from}px`;
        void content.offsetHeight;
        content.style.maxHeight = `${to}px`;
        window.clearTimeout(timer);
        timer = window.setTimeout(
            () => settle(next),
            getDurationMs('--km-duration-clamp', 420) + CLAMP_SETTLE_MS,
        );
    };

    const IDLE = 'site-page__more--idle';

    const riding = () => {
        const viewport = window.visualViewport?.height || window.innerHeight;
        return shell.getBoundingClientRect().bottom > viewport - dock() - 1;
    };

    const rest = () => {
        window.clearTimeout(idleTimer);
        idleTimer = 0;
        shell.classList.remove(IDLE);
    };

    const idle = () => {
        idleTimer = 0;
        if (!expanded) return;
        const hold = TIMING.showMoreHold();
        const quiet = performance.now() - stirred;
        if (quiet < hold) {
            idleTimer = window.setTimeout(idle, hold - quiet);
            return;
        }
        if (button.matches(':hover, :focus-visible')) {
            idleTimer = window.setTimeout(idle, hold);
            return;
        }
        if (riding()) shell.classList.add(IDLE);
    };

    const stir = () => {
        if (!expanded) return;
        stirred = performance.now();
        shell.classList.remove(IDLE);
        if (!idleTimer) idleTimer = window.setTimeout(idle, TIMING.showMoreHold());
    };

    const toggle = (next, animate = true) => {
        if (next === expanded) return;
        expanded = next;
        try { history.replaceState({ ...history.state, kmExpanded: next }, ''); } catch { /* noop */ }
        button.setAttribute('aria-expanded', next ? 'true' : 'false');
        if (label) {
            label.textContent = next
                ? button.dataset.labelLess
                : button.dataset.labelMore;
        }
        if (next) stir();
        else rest();

        const start = content.getBoundingClientRect().height;
        const current = ++turn;
        window.clearTimeout(timer);
        if (next) {
            const { full } = measure();
            if (!animate || prefersReducedMotion()) settle(true);
            else clamp(true, start, full);
            return;
        }
        const room = page.style.getPropertyValue('--km-show-more-clamp');
        const collapsed = Math.min(start, toPx(room, start));
        if (!animate || prefersReducedMotion()) {
            keepInView(collapsed);
            settle(false);
            return;
        }
        keepInView(collapsed).then(() => {
            if (current !== turn) return;
            const viewport = window.visualViewport?.height || window.innerHeight;
            const shown = viewport - content.getBoundingClientRect().top;
            clamp(false, Math.min(start, Math.max(collapsed, shown)), collapsed);
        });
    };

    const holds = (href) => {
        if (!href.startsWith('#') || href.length < 2) return false;
        const target = document.getElementById(decodeId(href.slice(1)));
        return !!target && target !== content && content.contains(target);
    };

    button.addEventListener('click', () => toggle(!expanded));

    document.addEventListener('click', (event) => {
        if (expanded) return;
        const link = event.target.closest?.('a[href]');
        if (!link || !holds(link.getAttribute('href') || '')) return;
        toggle(true, false);
    }, true);

    window.addEventListener('hashchange', () => {
        if (expanded || !holds(location.hash)) return;
        toggle(true, false);
        settleHash();
    });

    const buried = (node) => {
        const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
        if (expanded || !element || !content.contains(element)) return false;
        return element.getBoundingClientRect().bottom > shell.getBoundingClientRect().top;
    };

    document.addEventListener('focusin', (event) => {
        if (buried(event.target)) toggle(true, false);
    });

    document.addEventListener('selectionchange', () => {
        const selection = document.getSelection();
        if (selection && !selection.isCollapsed && buried(selection.focusNode)) {
            toggle(true, false);
        }
    });

    for (const type of [
        'pointermove', 'pointerdown', 'keydown', 'touchstart', 'focusin',
    ]) {
        window.addEventListener(type, stir, { passive: true });
    }
    onScroll(stir);

    window.addEventListener('resize', rafThrottle(fit), { passive: true });
    if ('ResizeObserver' in window) new ResizeObserver(rafThrottle(fit)).observe(document.body);
    if (document.fonts?.ready) document.fonts.ready.then(fit);

    if (holds(location.hash) || history.state?.kmExpanded) toggle(true, false);
}

function initHeaderSearch() {
    const search = document.querySelector('.site-header__search .site-search');
    if (!search) return;
    const input = search.querySelector('.site-search__input');
    const submit = search.querySelector('.site-search__submit');

    const open = () => {
        search.classList.add('is-open');
        if (!input) return;
        input.focus({ preventScroll: true });
    };
    const close = () => {
        if (input && input.value.trim()) return;
        search.classList.remove('is-open');
    };

    submit?.addEventListener('click', (event) => {
        if (search.classList.contains('is-open')) return;
        event.preventDefault();
        open();
    });

    input?.addEventListener('focus', () => search.classList.add('is-open'));
    input?.addEventListener('blur', () => setTimeout(close, 0));
    input?.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        close();
        input.blur();
    });

    const apple = /Mac|iPhone|iPad|iPod/.test(navigator.userAgentData?.platform || navigator.platform || '');
    window.addEventListener('keydown', (event) => {
        if (!input || String(event.key).toLowerCase() !== 'k') return;
        if (!(apple ? event.metaKey : event.ctrlKey) || event.altKey || event.shiftKey) return;
        event.preventDefault();
        input.focus();
    });

    document.addEventListener('click', (event) => {
        if (!search.contains(event.target)) close();
    });
}

function easeOutCubic(t) {
    return 1 - (1 - t) ** 3;
}

function smoothScrollTo(targetY, duration) {
    const startY = window.scrollY;
    const maxY = Math.max(0, root.scrollHeight - window.innerHeight);
    const endY = Math.min(maxY, Math.max(0, targetY));
    const distance = endY - startY;

    if (Math.abs(distance) < 1 || prefersReducedMotion()) {
        window.scrollTo(0, endY);
        return Promise.resolve();
    }

    const start = performance.now();
    const total = Math.max(SCROLL_DURATION_MIN_MS, Math.min(duration, SCROLL_DURATION_MAX_MS));
    const previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = 'auto';

    return new Promise((resolve) => {
        function step(now) {
            const t = Math.min(1, (now - start) / total);
            window.scrollTo(0, startY + distance * easeOutCubic(t));
            if (t < 1) {
                requestAnimationFrame(step);
                return;
            }
            root.style.scrollBehavior = previousBehavior || '';
            resolve();
        }
        requestAnimationFrame(step);
    });
}

function anchorHost(element) {
    const previous = element.previousElementSibling;
    if (previous) {
        if (previous.classList.contains('pre-title-text')) return previous;
        const last = previous.lastElementChild;
        if (last && last.classList.contains('pre-title-text')) return last;
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
    return Math.max(0, top - getHeaderOffsetPx());
}

function scrollDuration(distance) {
    return Math.max(TIMING.scrollMin(), Math.min(
        TIMING.scrollMax(),
        TIMING.scrollMin() + Math.min(ANCHOR_SCROLL_DIST_CAP_MS, Math.abs(distance) * ANCHOR_SCROLL_PX_FACTOR),
    ));
}

function scrollToElement(element) {
    const targetY = anchorTargetY(element);
    return smoothScrollTo(targetY, scrollDuration(window.scrollY - targetY));
}

function isModifiedClick(event) {
    return event.button !== 0
        || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
}

function initAnchorScrolling() {
    document.addEventListener('click', (event) => {
        const link = event.target.closest('a[href^="#"]');
        if (!link || isModifiedClick(event)) return;
        const href = link.getAttribute('href') || '';
        if (href === '#') return;
        const id = decodeId(href.slice(1));
        const target = document.getElementById(id);
        if (!target) return;

        event.preventDefault();
        scrollToElement(target).then(() => {
            try { history.pushState(history.state, '', `#${id}`); } catch { /* noop */ }
            if (!target.contains(link)) focusTarget(target);
        });
    });

    if (!revisited()) settleHash();
}

function revisited() {
    const [entry] = performance.getEntriesByType?.('navigation') ?? [];
    return entry?.type === 'reload' || entry?.type === 'back_forward';
}

function focusTarget(element) {
    if (!element.matches(FOCUSABLE)) element.setAttribute('tabindex', '-1');
    element.focus({ preventScroll: true });
}

function settleHash() {
    if (location.hash.length <= 1) return;
    const target = document.getElementById(decodeId(location.hash.slice(1)));
    if (!target) return;

    let cancelled = false;
    let observer = null;
    const stop = () => {
        cancelled = true;
        observer?.disconnect();
        observer = null;
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
    if ('ResizeObserver' in window) {
        observer = new ResizeObserver(() => requestAnimationFrame(apply));
        observer.observe(document.documentElement);
    }
    const finish = () => {
        apply();
        document.fonts?.ready.then(apply);
        setTimeout(stop, HASH_SETTLE_MS);
    };
    if (document.readyState === 'complete') finish();
    else window.addEventListener('load', finish, { once: true });
}

const tooltipTimers = new WeakMap();

function flashTooltip(link, message, transient = false) {
    window.clearTimeout(tooltipTimers.get(link));
    link.setAttribute('data-tooltip', message);
    void link.offsetWidth;
    link.classList.add('show-tooltip');
    tooltipTimers.set(link, window.setTimeout(() => {
        link.classList.remove('show-tooltip');
        if (!transient) return;
        tooltipTimers.set(link, window.setTimeout(
            () => link.removeAttribute('data-tooltip'),
            getDurationMs('--km-duration-fast', 250),
        ));
    }, TIMING.tooltipHold()));
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

function canonicalUrl(href) {
    const base = document.querySelector('link[rel="canonical"]')?.href || window.location.href;
    return href === undefined ? base : new URL(href, base).href;
}

function initCopyUrl() {
    document.querySelectorAll('.copy-url').forEach((link) => {
        link.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();
            const copied = await copyText(canonicalUrl());
            flashTooltip(link, copied ? 'Copied!' : 'Copy failed');
        });
    });
}

function initHeaderLinks() {
    if (!root.hasAttribute('data-copy-links')) return;
    document.addEventListener('click', (event) => {
        const link = event.target.closest?.('a.headerlink');
        if (!link || isModifiedClick(event)) return;
        copyText(canonicalUrl(link.getAttribute('href') || '')).then((copied) => {
            flashTooltip(link, copied ? 'Copied!' : 'Copy failed', true);
        });
    });
}

function initHeaderBorder() {
    const header = document.querySelector('.site-header');
    if (!header) return;
    const update = rafThrottle(() => {
        header.classList.toggle(
            'site-header--with-border',
            window.scrollY > HEADER_BORDER_SCROLL_THRESHOLD,
        );
    });
    onScroll(update);
}

function initCopyButtonNames() {
    const cells = document.querySelectorAll('div.highlight > pre').length;
    if (!cells) return;
    const name = () => {
        const buttons = document.querySelectorAll('button.copybtn');
        buttons.forEach((button) => {
            if (button.hasAttribute('aria-label')) return;
            const title = button.querySelector('svg title')?.textContent.trim();
            button.setAttribute('aria-label', title || button.dataset.tooltip || 'Copy');
        });
        return buttons.length >= cells;
    };
    if (name() || !('MutationObserver' in window)) return;
    const watch = new MutationObserver(() => {
        if (name()) watch.disconnect();
    });
    watch.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('load', () => setTimeout(() => watch.disconnect(), 5000), { once: true });
}

function initHighlightedLines() {
    const blocks = [...document.querySelectorAll('.highlight pre')]
        .filter((pre) => pre.querySelector('.hll'));
    if (!blocks.length) return;
    const measure = () => {
        blocks.forEach((pre) => pre.style.removeProperty('--km-code-width'));
        const widths = blocks.map((pre) => {
            const { paddingLeft, paddingRight } = getComputedStyle(pre);
            return Math.max(0, pre.scrollWidth - parseFloat(paddingLeft) - parseFloat(paddingRight));
        });
        blocks.forEach((pre, at) => pre.style.setProperty('--km-code-width', `${widths[at]}px`));
    };
    const soon = rafThrottle(measure);
    measure();
    document.fonts?.ready.then(measure);
    window.addEventListener('resize', soon, { passive: true });
    if ('ResizeObserver' in window) {
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }
}

function initScrollable() {
    const blocks = Array.from(document.querySelectorAll('.highlight pre, #content table'));
    if (!blocks.length) return;
    const mark = () => {
        blocks.forEach((pre) => {
            const scrolls = pre.scrollWidth > pre.clientWidth + 1
                || pre.scrollHeight > pre.clientHeight + 1;
            if (scrolls) pre.setAttribute('tabindex', '0');
            else pre.removeAttribute('tabindex');
        });
    };
    const soon = rafThrottle(mark);
    mark();
    document.fonts?.ready.then(mark);
    window.addEventListener('resize', soon, { passive: true });
    if ('ResizeObserver' in window) {
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }
}

function initImageZoom() {
    if (prefersReducedMotion()) return;

    const wrap = (element, container, standalone) => {
        if (element.classList.contains('no-zoom')) return;
        const inner = document.createElement('div');
        inner.className = standalone ? 'zoom-inner zoom-inner--standalone' : 'zoom-inner';
        const scale = document.createElement('div');
        scale.className = 'zoom-scale';
        (container || element.parentElement).insertBefore(inner, element);
        inner.appendChild(scale);
        scale.appendChild(element);
    };

    document.querySelectorAll('#content figure.zoom:not([data-zoom-ready]) > img')
        .forEach((image) => {
            const figure = image.parentElement;
            if (!figure || figure.dataset.zoomReady === 'true') return;
            wrap(image, figure, false);
            figure.dataset.zoomReady = 'true';
        });

    document.querySelectorAll('#content img.zoom:not(figure img):not(.no-zoom):not([data-zoom-ready])')
        .forEach((image) => {
            wrap(image, null, true);
            image.dataset.zoomReady = 'true';
        });
}

function initTouchReveal() {
    if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    const selector = '#content figure.zoom, #content figure.fuzzy-blur';
    const figures = document.querySelectorAll(selector);
    if (!figures.length) return;

    document.addEventListener('click', (event) => {
        const figure = event.target.closest(selector);
        if (figure && event.target.closest('a')) return;
        const shouldReveal = figure && !figure.classList.contains('is-revealed');
        figures.forEach((node) => node.classList.remove('is-revealed'));
        if (shouldReveal) figure.classList.add('is-revealed');
    });
}

function initHeaderNavDropdowns() {
    const nav = document.querySelector('.site-header__nav-tree');
    if (!nav) return;

    let uid = 0;
    Array.from(nav.querySelectorAll('p.caption')).forEach((caption) => {
        const list = caption.nextElementSibling;
        if (list?.tagName !== 'UL') return;

        const group = document.createElement('div');
        group.className = 'site-header__nav-group';
        caption.parentNode.insertBefore(group, caption);
        group.append(caption, list);

        list.id = list.id || `nav-group-${++uid}`;
        caption.setAttribute('tabindex', '0');
        caption.setAttribute('role', 'button');
        caption.setAttribute('aria-haspopup', 'true');
        caption.setAttribute('aria-controls', list.id);
        caption.setAttribute('aria-expanded', 'false');

        let openTimer;
        let closeTimer;
        const set = (next) => {
            clearTimeout(openTimer);
            clearTimeout(closeTimer);
            group.classList.toggle('is-open', next);
            caption.setAttribute('aria-expanded', String(next));
        };
        const open = () => {
            clearTimeout(closeTimer);
            openTimer = setTimeout(() => set(true), DROPDOWN_OPEN_DELAY_MS);
        };
        const close = () => {
            clearTimeout(openTimer);
            closeTimer = setTimeout(() => set(false), DROPDOWN_CLOSE_DELAY_MS);
        };

        caption.addEventListener('mouseenter', open, { passive: true });
        group.addEventListener('mouseenter', open, { passive: true });
        group.addEventListener('mouseleave', () => {
            if (!group.contains(document.activeElement)) close();
        }, { passive: true });
        group.addEventListener('focusout', (event) => {
            if (!group.contains(event.relatedTarget)) set(false);
        });
        caption.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                set(!group.classList.contains('is-open'));
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                set(true);
                list.querySelector('a[href]')?.focus();
            }
        });
        group.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape' || !group.classList.contains('is-open')) return;
            set(false);
            caption.focus();
        });
    });
}

function initDropdowns() {
    const easing = easingToken('--km-ease-smooth', 'cubic-bezier(0.32, 0.72, 0, 1)');

    document.querySelectorAll('details.sd-dropdown').forEach((details) => {
        const summary = details.querySelector(':scope > summary');
        const content = details.querySelector(':scope > .sd-summary-content');
        if (!summary || !content) return;

        let animation = null;
        summary.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            event.preventDefault();

            if (prefersReducedMotion() || typeof content.animate !== 'function') {
                details.open = !details.open;
                return;
            }

            const opening = !details.open;
            animation?.cancel();
            if (opening) details.open = true;
            details.classList.add('is-animating');

            const height = content.scrollHeight;
            const duration = Math.min(TIMING.dropdownMax(),
                Math.max(TIMING.dropdownMin(), height * DROPDOWN_PX_FACTOR));
            animation = content.animate({
                height: opening ? ['0px', `${height}px`] : [`${height}px`, '0px'],
                opacity: opening ? [0, 1] : [1, 0],
            }, { duration, easing, fill: 'both' });

            animation.finished.then(() => {
                animation?.cancel();
                animation = null;
                details.classList.remove('is-animating');
                if (!opening) details.open = false;
            }).catch(() => { /* superseded by a newer toggle */ });
        });
    });
}

function enrichYouTubeCard(card) {
    const id = card.getAttribute('data-youtube-id');
    if (!id || card.dataset.youtubeEnriched === '1') return;
    card.dataset.youtubeEnriched = '1';
    const title = card.hasAttribute('data-youtube-title')
        ? null
        : card.querySelector('.site-youtube-card__title');
    const channel = card.hasAttribute('data-youtube-channel')
        ? null
        : card.querySelector('.site-youtube-card__channel');
    if (!title && !channel) return;

    const watch = encodeURIComponent(`https://www.youtube.com/watch?v=${id}`);
    fetchJson(`https://www.youtube.com/oembed?url=${watch}&format=json`).then((data) => {
        if (!data) return;
        if (title && data.title) title.textContent = data.title;
        if (channel && data.author_name) channel.textContent = data.author_name;
    });
}

function initYouTubeCards() {
    onVisible(
        document.querySelectorAll('.site-youtube-card[data-youtube-id]'),
        enrichYouTubeCard,
    );
}

function formatCount(value) {
    return value >= 1000
        ? `${(value / 1000).toFixed(1).replace(/\.0$/, '')}k`
        : String(value);
}

function buildTickerColumn(digit, index) {
    const laps = Math.min(1 + index, TICKER_MAX_LAPS);
    const stops = laps * TICKER_RADIX + digit;
    const column = document.createElement('span');
    column.className = 'site-github-repository__digit';
    const reel = document.createElement('span');
    reel.className = 'site-github-repository__reel';
    for (let i = 0; i <= stops; i += 1) {
        const cell = document.createElement('span');
        cell.className = 'site-github-repository__cell';
        cell.textContent = String(i % TICKER_RADIX);
        reel.appendChild(cell);
    }
    column.appendChild(reel);
    return {
        column,
        reel,
        shift: `translateY(-${(stops / (stops + 1)) * 100}%)`,
        duration: TIMING.tickerBase() + index * TIMING.tickerStep(),
    };
}

function renderTicker(field, value) {
    const ticker = document.createElement('span');
    ticker.className = 'site-github-repository__ticker';
    const columns = [];

    for (const character of value) {
        if (character < '0' || character > '9') {
            const symbol = document.createElement('span');
            symbol.className = 'site-github-repository__symbol';
            symbol.textContent = character;
            ticker.appendChild(symbol);
            continue;
        }
        const built = buildTickerColumn(Number(character), columns.length);
        ticker.appendChild(built.column);
        columns.push(built);
    }

    field.replaceChildren(ticker);
    const reduced = prefersReducedMotion();
    for (const { reel, shift, duration } of columns) {
        if (reduced || typeof reel.animate !== 'function') {
            reel.style.transform = shift;
            continue;
        }
        reel.animate([
            { transform: 'translateY(0%)', filter: 'blur(0)' },
            { filter: TICKER_BLUR, offset: TICKER_BLUR_AT },
            { transform: shift, filter: 'blur(0)' },
        ], {
            duration, easing: TICKER_EASING, fill: 'forwards',
        });
    }
}

async function loadRepository(widget) {
    if (widget.dataset.repositoryLoaded === '1') return;
    widget.dataset.repositoryLoaded = '1';

    const project = widget.getAttribute('data-repository');
    const fields = widget.querySelectorAll('[data-repository-count]');
    if (!project || !fields.length) return;

    const data = await fetchJson(`https://api.github.com/repos/${project}`) || {};
    fields.forEach((field) => {
        const raw = Number(data[field.getAttribute('data-repository-count')]);
        const count = Number.isFinite(raw) ? Math.max(0, Math.trunc(raw)) : 0;
        renderTicker(field, formatCount(count));
    });
}

function initRepositoryWidgets() {
    // The reel should roll once per page load, the moment the widget is first
    // scrolled into view - not while it is still off-screen.
    onVisible(
        document.querySelectorAll('.site-github-repository[data-repository]'),
        loadRepository,
        { rootMargin: '0px 0px -10% 0px' },
    );
}

function initInkReveal() {
    onVisible(
        document.querySelectorAll('.sharpie, .pencil'),
        (element) => element.classList.add('is-visible'),
        { threshold: 0.1 },
    );
}

function initPageReveal() {
    const assigned = new Set();
    let delay = 0;
    const assign = (element) => {
        if (!element || assigned.has(element)) return;
        assigned.add(element);
        if (element.getBoundingClientRect().top > window.innerHeight) return;
        element.classList.add('page-reveal-item');
        element.style.setProperty('--km-reveal-delay', `${delay}ms`);
        delay = Math.min(delay + TIMING.revealStep(), TIMING.revealStep() * REVEAL_STEPS);
    };

    assign(document.querySelector('.site-header'));
    assign(document.querySelector('.site-breadcrumbs'));

    const content = document.getElementById('content');
    const topSection = content?.querySelector(':scope > section');
    if (topSection) {
        assign(topSection.querySelector(':scope > h1'));
        assign(topSection.querySelector(':scope > .lead'));
        assign(topSection.querySelector(':scope > .site-article'));
        for (const child of topSection.children) {
            if (child.tagName !== 'SECTION') assign(child);
        }
        topSection.querySelectorAll(':scope > section').forEach(assign);
    } else {
        assign(content);
    }

    assign(document.querySelector('.site-feedback-shell'));
    assign(document.querySelector('.site-layout__meta'));
    assign(document.querySelector('.site-pagination'));
    assign(document.querySelector('.site-footer'));
}

function initArticleBackground() {
    const article = document.querySelector('.site-article[data-background]');
    const main = document.querySelector('.site-layout__content');
    if (!article || !main) return;

    const urls = article.getAttribute('data-background').trim().split(/\s+/).filter(Boolean);
    if (!urls.length) return;

    for (let i = urls.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        [urls[i], urls[j]] = [urls[j], urls[i]];
    }

    main.style.isolation = 'isolate';
    const overlay = document.createElement('div');
    overlay.className = 'site-article__bg';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.style.top = '0';
    overlay.style.backgroundImage = `url("${urls[0]}")`;
    overlay.style.opacity = '0';
    if (urls.length === 1) {
        overlay.style.animationIterationCount = '1';
        overlay.style.animationFillMode = 'forwards';
    }
    main.appendChild(overlay);

    const measure = () => {
        const anchor = article.querySelector('.site-article__meta') || article;
        const fontSize = parseFloat(getComputedStyle(root).fontSize) || 16;
        const height = anchor.getBoundingClientRect().bottom - fontSize * 2
            - main.getBoundingClientRect().top;
        overlay.style.height = `${Math.max(0, height)}px`;
    };

    measure();
    requestAnimationFrame(() => requestAnimationFrame(() => {
        overlay.style.opacity = '';
    }));

    window.addEventListener('resize', rafThrottle(measure), { passive: true });
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(main);
    if (document.fonts?.ready) document.fonts.ready.then(measure);

    if (urls.length === 1 || prefersReducedMotion()) return;
    let index = 0;
    setInterval(() => {
        overlay.style.opacity = '0';
        setTimeout(() => {
            index = (index + 1) % urls.length;
            overlay.style.backgroundImage = `url("${urls[index]}")`;
            overlay.style.animationName = 'none';
            void overlay.offsetWidth;
            overlay.style.animationName = '';
            requestAnimationFrame(() => requestAnimationFrame(() => {
                overlay.style.opacity = '';
            }));
        }, ARTICLE_BG_FADE_MS + 50);
    }, ARTICLE_BG_INTERVAL_MS);
}

(function initCalEmbed(window_, source, action) {
    const push = (target, args) => target.q.push(args);
    window_.Cal = window_.Cal || function Cal(...args) {
        const cal = window_.Cal;
        if (!cal.loaded) {
            cal.ns = {};
            cal.q = cal.q || [];
            document.head.appendChild(document.createElement('script')).src = source;
            cal.loaded = true;
        }
        if (args[0] !== action) {
            push(cal, args);
            return;
        }
        const api = function api(...inner) { push(api, inner); };
        const namespace = args[1];
        api.q = api.q || [];
        if (typeof namespace === 'string') {
            cal.ns[namespace] = cal.ns[namespace] || api;
            push(cal.ns[namespace], args);
            push(cal, ['initNamespace', namespace]);
        } else {
            push(cal, args);
        }
    };
}(window, 'https://app.cal.com/embed/embed.js', 'init'));

function initCalNamespaces() {
    document.addEventListener('click', (event) => {
        const link = event.target.closest?.('a[href="#"]');
        if (link?.hasAttribute('data-cal-link') || link?.querySelector('[data-cal-link]')) event.preventDefault();
    });
    const seen = new Set();
    document.querySelectorAll('[data-cal-namespace]').forEach((el) => {
        const ns = el.getAttribute('data-cal-namespace');
        if (!ns || seen.has(ns)) return;
        seen.add(ns);
        Cal('init', ns, { origin: CAL_ORIGIN });
        Cal.ns[ns]('ui', { hideEventTypeDetails: false, layout: 'month_view' });
    });
}

const WALKTHROUGH_NARROW = 641;
const WALKTHROUGH_LINES = 15;
const WALKTHROUGH_MIN_LINES = 6;
const WALKTHROUGH_SHARE = 0.55;
const WALKTHROUGH_LEAD = 0.24;
const WALKTHROUGH_LEAD_NARROW = 0.14;
const WALKTHROUGH_ROOM = 120;
const WALKTHROUGH_OUT_LINES = 4;
const WALKTHROUGH_JITTER = 120;
const WALKTHROUGH_SETTLE = 120;
const WALKTHROUGH_RISE = 6;
const WALKTHROUGH_QUIET = 3;
const WALKTHROUGH_PATIENCE = 60;
const WALKTHROUGH_KEYS = { ArrowLeft: -1, ArrowRight: 1 };
const ATTEMPTS_OUT_LINES = 8;
const ATTEMPTS_HOLD = 0.8;
const ATTEMPTS_KEEP = 0.5;
const walkthroughs = [];
const walkthroughDrawn = new Map();
let walkthroughPieces = new Map();
let walkthroughLift = 0;

function clamp(value, low, high) {
    return Math.max(low, Math.min(high, value));
}

function readWalkthroughPayload(host) {
    try {
        return JSON.parse(host.querySelector('[data-payload]')?.textContent || 'null');
    } catch {
        return null;
    }
}

function walkthroughHeader() {
    const header = document.querySelector('.site-header');
    return header ? Math.ceil(header.getBoundingClientRect().height) : 0;
}

function walkthroughSource(payload) {
    const code = payload.code || '';
    if (!payload.setup) return code;
    const { open = '#', close = '' } = payload.comment || {};
    return `${open} Setup${close ? ` ${close}` : ''}\n${payload.setup}\n\n${code}`;
}

function walkthroughValue(item, opened) {
    const value = document.createElement('span');
    value.className = 'km-walkthrough__value';
    if (!item.short) {
        value.textContent = item.full;
        return value;
    }
    const short = document.createElement('span');
    short.className = 'km-walkthrough__short';
    short.textContent = item.short;
    const full = document.createElement('span');
    full.className = 'km-walkthrough__full';
    full.textContent = item.full;
    value.dataset.key = item.key;
    value.setAttribute('data-long', '');
    value.setAttribute('role', 'button');
    value.tabIndex = 0;
    const open = opened.has(item.key);
    if (open) value.setAttribute('data-open', '');
    value.setAttribute('aria-expanded', String(open));
    value.append(short, full);
    return value;
}

function walkthroughEntry(item, opened) {
    const entry = document.createElement('span');
    entry.className = 'km-walkthrough__var';
    if (item.fresh) entry.setAttribute('data-fresh', '');
    if (item.kind) entry.dataset.kind = item.kind;
    entry.append(
        item.name ? `${item.name}: ` : `${item.mark} `,
        walkthroughValue(item, opened),
    );
    return entry;
}

function attemptsDiff(before, after) {
    const table = Array.from({ length: before.length + 1 }, () => new Uint32Array(after.length + 1));
    for (let i = before.length - 1; i >= 0; i -= 1) {
        for (let j = after.length - 1; j >= 0; j -= 1) {
            table[i][j] = before[i] === after[j]
                ? table[i + 1][j + 1] + 1
                : Math.max(table[i + 1][j], table[i][j + 1]);
        }
    }
    const script = [];
    let i = 0;
    let j = 0;
    while (i < before.length || j < after.length) {
        if (i < before.length && j < after.length && before[i] === after[j]) {
            script.push(['=', i, j]);
            i += 1;
            j += 1;
        } else if (j === after.length || (i < before.length && table[i + 1][j] >= table[i][j + 1])) {
            script.push(['-', i, -1]);
            i += 1;
        } else {
            script.push(['+', -1, j]);
            j += 1;
        }
    }
    return script;
}

function attemptsSign(line, change) {
    const sign = document.createElement('span');
    sign.className = 'km-attempts__sign';
    sign.setAttribute('aria-hidden', 'true');
    sign.textContent = change === 'added' ? '+' : '-';
    line.dataset.diff = change;
    line.prepend(sign);
}

function walkthroughMovable(element) {
    const { display, position } = getComputedStyle(element);
    return display !== 'none' && (position === 'static' || position === 'relative');
}

function walkthroughHeight(element) {
    return element.getBoundingClientRect().height;
}

function walkthroughShifted(element) {
    const { translate, transform } = getComputedStyle(element);
    let shifted = translate && translate !== 'none' ? parseFloat(translate.split(' ')[1]) || 0 : 0;
    const matrix = /^matrix(3d)?\((.+)\)$/.exec(transform || '');
    if (matrix) shifted += Number(matrix[2].split(',')[matrix[1] ? 13 : 5]) || 0;
    return shifted;
}

function walkthroughTop(element) {
    let top = element.getBoundingClientRect().top + window.scrollY;
    for (let node = element; node && node !== root; node = node.parentElement) {
        top -= walkthroughShifted(node);
    }
    return top;
}

function walkthroughScreen() {
    const probe = document.createElement('div');
    probe.style.cssText = 'position: absolute; top: 0; width: 0; height: 100lvh; visibility: hidden;';
    document.body.append(probe);
    const height = probe.getBoundingClientRect().height;
    probe.remove();
    return height || window.innerHeight;
}

function walkthroughSnap(value) {
    const ratio = window.devicePixelRatio || 1;
    return Math.round(value * ratio) / ratio;
}

function walkthroughTail(host) {
    const found = [];
    for (let node = host; node && node !== document.body; node = node.parentElement) {
        for (let next = node.nextElementSibling; next; next = next.nextElementSibling) {
            if (walkthroughMovable(next)) found.push(next);
        }
    }
    return found;
}

function walkthroughLayout() {
    const pieces = new Map();
    walkthroughs.forEach((walk) => {
        if (!walk.span) return;
        const start = walkthroughTop(walk.host) - walk.stick;
        walk.start = start;
        walk.piece = [start, start + walk.span, -walk.span, 0];
        walk.tail.forEach((element) => {
            if (!pieces.has(element)) pieces.set(element, []);
            pieces.get(element).push(walk.piece);
        });
    });
    walkthroughPieces = pieces;
}

function walkthroughDraw() {
    const shifts = new Map();
    let lift = 0;
    walkthroughs.forEach((walk) => {
        if (!walk.span) return;
        const shift = walk.pane.getBoundingClientRect().bottom
            - walk.host.getBoundingClientRect().bottom;
        shifts.set(walk, shift);
        lift += shift;
    });
    const totals = new Map();
    shifts.forEach((shift, walk) => {
        walk.tail.forEach((element) => {
            totals.set(element, (totals.get(element) || 0) + shift);
        });
    });
    lift = walkthroughSnap(lift);
    if (lift !== walkthroughLift) {
        walkthroughLift = lift;
        document.querySelector('.site-layout__content')
            ?.style.setProperty('--km-walkthrough-lift', `${lift}px`);
    }
    walkthroughDrawn.forEach((_, element) => {
        if (!totals.has(element)) totals.set(element, 0);
    });
    totals.forEach((value, element) => {
        const offset = walkthroughSnap(value);
        if ((walkthroughDrawn.get(element) || 0) === offset) return;
        if (offset) {
            element.style.translate = `0 ${offset}px`;
            element.setAttribute('data-km-drawn', '');
            walkthroughDrawn.set(element, offset);
        } else {
            element.style.removeProperty('translate');
            element.removeAttribute('data-km-drawn');
            walkthroughDrawn.delete(element);
        }
    });
}

function walkthroughFrame(animate = true) {
    walkthroughs.forEach((walk) => walk.update(animate));
    walkthroughDraw();
}

const walkthroughTick = rafThrottle(() => walkthroughFrame());

function walkthroughMeasure() {
    walkthroughs.forEach((walk) => walk.measure());
    walkthroughLayout();
    walkthroughFrame(false);
}

function walkthroughRefit() {
    let changed = false;
    walkthroughs.forEach((walk) => {
        if (walk.shape() === walk.shaped) return;
        walk.measure();
        changed = true;
    });
    walkthroughLayout();
    walkthroughFrame(!changed);
}

let walkthroughSettling = 0;

function walkthroughSoon() {
    window.clearTimeout(walkthroughSettling);
    walkthroughSettling = window.setTimeout(walkthroughRefit, WALKTHROUGH_SETTLE);
}

function walkthroughMoved(element) {
    for (let node = element; node && node !== document.body; node = node.parentElement) {
        if (walkthroughPieces.has(node)) return true;
    }
    return false;
}

function walkthroughReach(target) {
    let last = window.scrollY;
    let place = target.getBoundingClientRect().top;
    let quiet = 0;
    let frames = 0;
    let again = false;
    const look = () => {
        if (document.activeElement !== target) return;
        frames += 1;
        const now = target.getBoundingClientRect().top;
        const still = !again
            || (now === place && !walkthroughs.some((walk) => walk.moving()));
        quiet = window.scrollY === last && still ? quiet + 1 : 0;
        last = window.scrollY;
        place = now;
        if (quiet < WALKTHROUGH_QUIET && frames < WALKTHROUGH_PATIENCE) {
            requestAnimationFrame(look);
            return;
        }
        const top = walkthroughHeader();
        const rect = target.getBoundingClientRect();
        const fits = rect.height <= window.innerHeight - top;
        const seen = fits
            ? rect.top >= top - 1 && rect.bottom <= window.innerHeight + 1
            : rect.top < window.innerHeight && rect.bottom > top;
        if (!seen) {
            const previousBehavior = root.style.scrollBehavior;
            root.style.scrollBehavior = 'auto';
            window.scrollTo(0, Math.max(0, layoutTop(target) - getHeaderOffsetPx()));
            root.style.scrollBehavior = previousBehavior || '';
        }
        if (again) return;
        again = true;
        quiet = 0;
        frames = 0;
        requestAnimationFrame(look);
    };
    requestAnimationFrame(look);
}

function createWalkthrough(host) {
    const payload = readWalkthroughPayload(host);
    const steps = payload?.steps;
    const pane = host.querySelector('[data-pane]');
    const frame = host.querySelector('[data-frame]');
    const stage = host.querySelector('[data-stage]');
    const code = stage?.querySelector('pre');
    const box = host.querySelector('[data-notes]');
    if (!steps?.length || !pane || !frame || !code || !box) return null;

    const lead = host.querySelector('[data-lead]');
    const foot = host.querySelector('.km-walkthrough__tail') || box;
    const counter = host.querySelector('[data-counter]');
    const out = host.querySelector('[data-out]');
    const status = host.querySelector('[data-status]');
    const copy = host.querySelector('[data-copy]');
    const buttons = Array.from(host.querySelectorAll('[data-step]'));
    const codes = Array.isArray(payload.codes) ? payload.codes : null;
    const texts = codes ? codes.map((source) => source.split('\n')) : [];
    const drafts = Array.from(
        host.querySelectorAll('[data-draft]'),
        (draft) => Array.from(draft.querySelectorAll('[data-line]')),
    );
    const lines = new Map();
    code.querySelectorAll('[data-line]').forEach((line) => {
        lines.set(Number(line.dataset.line), line);
    });
    const notes = new Map();
    box.querySelectorAll('[data-note]').forEach((note) => {
        notes.set(Number(note.dataset.note), note);
    });
    const runs = steps.map((step, at) => {
        let first = at;
        let last = at;
        while (first > 0 && steps[first - 1].note === step.note) first -= 1;
        while (last < steps.length - 1 && steps[last + 1].note === step.note) last += 1;
        return [first, last];
    });
    const paces = steps.map((step) => step.pace ?? payload.pace);
    const starts = [];
    let length = 0;
    paces.forEach((pace) => {
        starts.push(length);
        length += pace;
    });
    const printed = [];
    let text = '';
    steps.forEach((step) => {
        text += step.out || '';
        printed.push(text.length);
    });
    const written = codes ? steps.map((step) => step.out || '').filter(Boolean) : [text].filter(Boolean);
    const sayings = (codes || []).map((_, at) => (
        steps.find((step) => (step.version ?? 0) === at && step.out)?.out || ''
    ));

    const opened = new Set();
    const walk = {
        host, pane, tail: [], stick: 0, span: 0, start: 0, resting: 0, shaped: '', update, measure, shape, moving,
    };
    let index = -1;
    let mode = '';
    let current = null;
    let marked = [];
    let filled = [];
    let shown = null;
    let grow = null;
    let settling = 0;
    let shift = 0;
    let most = 0;
    let fitted = new Map();
    let loose = false;
    let touched = false;
    let steady = false;
    let version = 0;
    let morphing = null;
    let told = null;
    let telling = 0;
    let settled = 0;
    let row = 0;
    let inset = 0;
    let wholes = [];
    let boxes = [];

    function shape() {
        return [
            host.getClientRects().length > 0,
            host.closest('.site-page--clamped') !== null,
            pane.clientWidth,
            codes ? getComputedStyle(code).lineHeight : code.offsetHeight,
            lead?.offsetHeight ?? 0,
            walkthroughHeader(),
        ].join(' ');
    }

    function moving() {
        return Boolean(morphing && !morphing.done);
    }

    function whole() {
        return codes ? wholes[version] ?? code.offsetHeight : code.offsetHeight;
    }

    function stepAt(into) {
        if (into < 0) return -1;
        let at = 0;
        while (at < steps.length - 1 && starts[at + 1] <= into) at += 1;
        return at;
    }

    function renumber(staying, to) {
        staying.forEach(([line, at]) => {
            line.dataset.line = String(at + 1);
            line.dataset.number = drafts[to][at].dataset.number;
        });
    }

    function land() {
        if (!morphing) return;
        const run = morphing;
        morphing = null;
        run.timers.forEach((timer) => window.clearTimeout(timer));
        run.animations.forEach((animation) => animation.cancel());
        run.going.forEach((line) => line.remove());
        run.coming.forEach((line) => {
            line.removeAttribute('data-coming');
            line.removeAttribute('data-diff');
            line.removeAttribute('data-settling');
            line.querySelector('.km-attempts__sign')?.remove();
        });
        renumber(run.staying, run.to);
        host.style.removeProperty('--km-attempts-delay');
    }

    function resize(at) {
        if (boxes.length) host.style.setProperty('--km-attempts-out', `${boxes[at]}px`);
    }

    function outline() {
        const kept = Array.from(out.childNodes);
        host.style.setProperty('--km-attempts-out', `calc(${ATTEMPTS_OUT_LINES} * 1.5em + 1rem)`);
        const cap = out.getBoundingClientRect().height;
        host.style.setProperty('--km-attempts-out', 'auto');
        const found = sayings.map((said) => {
            out.textContent = said;
            return Math.min(cap, out.getBoundingClientRect().height);
        });
        out.replaceChildren(...kept);
        return found;
    }

    function morph(to, animate) {
        settled = 0;
        if (to === version || !drafts[to]) return null;
        land();
        const from = version;
        const forward = to > from;
        version = to;
        const before = Array.from(code.children);
        const tall = before[0]?.getBoundingClientRect().height || row;
        const rows = [];
        const run = {
            to, going: [], coming: [], staying: [], animations: [], timers: [],
        };
        attemptsDiff(texts[from], texts[to]).forEach(([change, was, now]) => {
            if (change === '=') {
                rows.push(before[was]);
                run.staying.push([before[was], now]);
            } else if (change === '-') {
                rows.push(before[was]);
                run.going.push(before[was]);
            } else {
                const line = drafts[to][now].cloneNode(true);
                rows.push(line);
                run.coming.push(line);
            }
        });
        code.replaceChildren(...rows);
        lines.clear();
        run.staying.forEach(([line, now]) => lines.set(now + 1, line));
        run.coming.forEach((line) => lines.set(Number(line.dataset.line), line));
        const first = run.coming[0] ? Number(run.coming[0].dataset.line) : null;
        if (!animate) {
            run.going.forEach((line) => line.remove());
            renumber(run.staying, to);
            resize(to);
            return first;
        }
        morphing = run;
        const swap = TIMING.walkthroughSwap();
        const easing = easingToken('--km-ease-smooth', 'ease-out');
        const hold = forward ? swap * ATTEMPTS_HOLD : 0;
        settled = hold + swap;
        host.style.setProperty('--km-attempts-delay', `${hold}ms`);
        resize(to);
        run.going.forEach((line) => {
            line.setAttribute('aria-hidden', 'true');
            line.setAttribute('data-going', '');
            if (forward) attemptsSign(line, 'removed');
            run.animations.push(line.animate(
                [{ height: `${tall}px`, opacity: 1 }, { height: '0px', opacity: 0 }],
                { duration: swap, delay: hold, easing, fill: 'forwards' },
            ));
        });
        run.coming.forEach((line) => {
            line.setAttribute('data-coming', '');
            if (forward) attemptsSign(line, 'added');
            run.animations.push(line.animate(
                [{ height: '0px', opacity: 0 }, { height: `${tall}px`, opacity: 1 }],
                { duration: swap, delay: hold, easing, fill: 'backwards' },
            ));
        });
        const later = (delay, then) => run.timers.push(window.setTimeout(then, delay));
        later(hold, () => renumber(run.staying, to));
        later(hold + swap, () => {
            run.done = true;
            run.going.forEach((line) => line.remove());
            run.going = [];
            run.coming.forEach((line) => line.removeAttribute('data-coming'));
            host.style.removeProperty('--km-attempts-delay');
            if (!forward) morphing = null;
        });
        if (!forward) return first;
        later(hold + swap * (1 + ATTEMPTS_KEEP), () => {
            run.coming.forEach((line) => {
                line.setAttribute('data-settling', '');
                line.removeAttribute('data-diff');
            });
        });
        later(hold + swap * (2 + ATTEMPTS_KEEP), () => {
            run.coming.forEach((line) => {
                line.removeAttribute('data-settling');
                line.querySelector('.km-attempts__sign')?.remove();
            });
            morphing = null;
        });
        return first;
    }

    function tell(at, animate, wait) {
        if (!out || !written.length || told === at) return;
        told = at;
        const step = steps[at];
        window.clearTimeout(telling);
        out.replaceChildren();
        out.removeAttribute('data-verdict');
        if (!step.out) return;
        const swap = TIMING.walkthroughSwap();
        const words = document.createElement('span');
        words.textContent = step.out;
        const show = () => {
            out.replaceChildren(words);
            if (step.verdict) out.dataset.verdict = step.verdict;
            out.scrollTop = 0;
        };
        if (!animate) {
            show();
            return;
        }
        telling = window.setTimeout(() => {
            show();
            words.animate(
                [{ opacity: 0 }, { opacity: 1 }],
                { duration: swap * 0.8, easing: easingToken('--km-ease-smooth', 'ease-out') },
            );
        }, wait || swap * 0.2);
    }

    function annotate(step) {
        const focused = stage.contains(document.activeElement)
            ? document.activeElement.closest('[data-long]')?.dataset.key
            : undefined;
        filled.forEach((slot) => slot.replaceChildren());
        filled = [];
        const groups = new Map();
        const add = (at, item) => {
            if (!lines.has(at)) return;
            if (!groups.has(at)) groups.set(at, []);
            groups.get(at).push(item);
        };
        (step.vars || []).forEach(([name, at, full, short, fresh]) => {
            add(at, { name, full, short, fresh, key: name });
        });
        if (step.ret) {
            add(step.line, {
                mark: 'returns:', full: step.ret[0], short: step.ret[1],
                key: 'returns:', kind: 'return', fresh: 1,
            });
        }
        if (step.error) {
            add(step.line, {
                mark: 'error:', full: step.error[0], short: step.error[1],
                key: 'error:', kind: 'error', fresh: 1,
            });
        }
        const { open = '#', close = '' } = payload.comment || {};
        groups.forEach((items, at) => {
            const slot = lines.get(at).querySelector('[data-ann]');
            slot.append(`${open} `);
            items.forEach((item, n) => {
                if (n) slot.append(', ');
                slot.append(walkthroughEntry(item, opened));
            });
            if (close) slot.append(` ${close}`);
            filled.push(slot);
        });
        if (focused === undefined) return;
        const again = Array.from(stage.querySelectorAll('[data-long]'))
            .find((value) => value.dataset.key === focused);
        steady = true;
        (again || stage).focus({ preventScroll: true });
        steady = false;
    }

    function room() {
        return Math.floor(fitted.get(codes ? index : shown ?? -1) ?? most);
    }

    function follow(line) {
        const rect = line.getBoundingClientRect();
        aim(rect.top - code.getBoundingClientRect().top, rect.height);
    }

    function aim(top, tall) {
        const height = room();
        const pad = Math.min(height / 3, tall * 2);
        let target = shift;
        if (top < target + pad) target = top - pad;
        else if (top + tall > target + height - pad) {
            target = top + tall - height + pad;
        }
        shift = clamp(Math.round(target), 0, Math.max(0, whole() - height));
        host.style.setProperty('--km-walkthrough-shift', `${shift}px`);
    }

    function edge() {
        const right = stage.scrollWidth - stage.clientWidth - stage.scrollLeft;
        const top = loose ? stage.scrollTop : shift;
        const below = loose
            ? stage.scrollHeight - stage.clientHeight - top
            : whole() - room() - shift;
        stage.toggleAttribute('data-more', right > 2);
        stage.toggleAttribute('data-above', top > 2);
        stage.toggleAttribute('data-below', below > 2);
        if (box.hasAttribute('data-moving')) return;
        const rest = Math.max(0, box.scrollHeight - box.clientHeight - box.scrollTop);
        box.style.setProperty('--km-walkthrough-notes-above', `${Math.round(box.scrollTop)}px`);
        box.style.setProperty('--km-walkthrough-notes-below', `${Math.round(rest)}px`);
    }

    function print(at) {
        if (!out || !text) return;
        const end = printed[at];
        const start = end - (steps[at].out || '').length;
        out.replaceChildren();
        if (start > 0) out.append(text.slice(0, start));
        if (end > start) {
            const fresh = document.createElement('span');
            fresh.setAttribute('data-fresh', '');
            fresh.textContent = text.slice(start, end);
            out.append(fresh);
        }
        out.scrollTop = out.scrollHeight;
    }

    function fit() {
        host.style.setProperty('--km-walkthrough-stage', `${room()}px`);
    }

    function loosen() {
        if (loose || !mode || steady || touched) return;
        loose = true;
        stage.setAttribute('data-loose', '');
        host.style.setProperty('--km-walkthrough-shift', '0px');
        stage.scrollTop = shift;
        edge();
    }

    function rejoin() {
        if (!loose) return;
        loose = false;
        shift = Math.round(stage.scrollTop);
        host.style.setProperty('--km-walkthrough-shift', `${shift}px`);
        stage.scrollTop = 0;
        stage.removeAttribute('data-loose');
        void code.offsetHeight;
    }

    function trailing() {
        const probe = document.createElement('div');
        probe.style.cssText = 'display: block; height: 0; margin: 0; padding: 0; border: 0';
        pane.append(probe);
        const gap = probe.getBoundingClientRect().top - foot.getBoundingClientRect().bottom;
        probe.remove();
        return Math.max(0, gap);
    }

    function still() {
        grow?.cancel();
        grow = null;
        window.clearTimeout(settling);
        box.removeAttribute('data-moving');
        notes.forEach((note) => {
            note.getAnimations().forEach((animation) => animation.cancel());
            note.removeAttribute('data-leaving');
        });
    }

    function reveal(next, animate) {
        if (next === shown) return;
        const from = box.getBoundingClientRect().height;
        const leaving = notes.get(shown);
        const arriving = notes.get(next);
        shown = next;
        leaving?.removeAttribute('aria-current');
        arriving?.setAttribute('aria-current', 'step');
        if (!animate) {
            still();
            notes.forEach((note) => note.toggleAttribute('data-shown', note === arriving));
            fit();
            return;
        }
        const swap = TIMING.walkthroughSwap();
        const easing = easingToken('--km-ease-smooth', 'ease-out');
        if (leaving) {
            const { opacity, translate } = getComputedStyle(leaving);
            leaving.getAnimations().forEach((animation) => animation.cancel());
            leaving.removeAttribute('data-shown');
            leaving.setAttribute('data-leaving', '');
            const fade = leaving.animate(
                [{ opacity, translate }, { opacity: 0, translate }],
                { duration: swap * 0.4, easing, fill: 'forwards' },
            );
            fade.onfinish = () => {
                leaving.removeAttribute('data-leaving');
                fade.cancel();
            };
        }
        if (arriving) {
            const { opacity, translate } = arriving.hasAttribute('data-leaving')
                ? getComputedStyle(arriving)
                : { opacity: 0, translate: `0 ${WALKTHROUGH_RISE}px` };
            arriving.getAnimations().forEach((animation) => animation.cancel());
            arriving.removeAttribute('data-leaving');
            arriving.setAttribute('data-shown', '');
            arriving.animate(
                [{ opacity, translate }, { opacity: 1, translate: '0 0' }],
                { duration: swap * 0.8, delay: swap * 0.2, easing, fill: 'backwards' },
            );
        }
        fit();
        grow?.cancel();
        box.scrollTop = 0;
        box.style.setProperty('--km-walkthrough-notes-above', '0px');
        box.style.setProperty('--km-walkthrough-notes-below', '0px');
        const to = box.getBoundingClientRect().height;
        grow = Math.abs(to - from) > 0.5
            ? box.animate(
                [{ height: `${from}px` }, { height: `${to}px` }],
                { duration: swap, easing },
            )
            : null;
        box.setAttribute('data-moving', '');
        window.clearTimeout(settling);
        settling = window.setTimeout(() => {
            box.removeAttribute('data-moving');
            read();
            edge();
        }, swap);
    }

    function paint(at, animate = true) {
        const next = clamp(at, 0, steps.length - 1);
        if (next === index && animate) return;
        index = next;
        rejoin();
        const step = steps[index];
        const smooth = animate && !prefersReducedMotion();
        marked.forEach((line) => line.removeAttribute('data-current'));
        marked = [];
        const arrived = codes ? morph(step.version ?? 0, smooth) : null;
        for (let at = step.line; at <= (step.end ?? step.line); at += 1) {
            const line = lines.get(at);
            if (!line) continue;
            line.setAttribute('data-current', '');
            marked.push(line);
        }
        current = marked[0] || null;
        if (codes) {
            host.toggleAttribute('data-banded', marked.length > 0);
            tell(index, smooth, settled);
        } else {
            annotate(step);
            print(index);
        }
        reveal(step.note ?? -1, smooth);
        if (codes) {
            fit();
            if (current) aim(inset + row * (step.line - 1), row * marked.length);
            else if (arrived) aim(inset + row * (arrived - 1), row);
            else aim(shift, 0);
        } else if (current) {
            follow(current);
        }
        edge();
        if (counter) {
            counter.textContent = codes
                ? `${version + 1} / ${codes.length}`
                : `${index + 1} / ${steps.length}`;
        }
        buttons.forEach((button) => {
            const back = Number(button.dataset.step) < 0;
            const stuck = back ? index === 0 : index === steps.length - 1;
            button.setAttribute('aria-disabled', String(stuck));
        });
        if (status && mode === 'pager') {
            const first = marked[0]?.dataset.number || step.line;
            const last = marked[marked.length - 1]?.dataset.number || first;
            const where = first === last ? `line ${first}` : `lines ${first}–${last}`;
            status.textContent = codes
                ? `Attempt ${version + 1} of ${codes.length}${marked.length ? `, ${where}` : ''}`
                : `Step ${index + 1} of ${steps.length}, ${where}`;
        }
    }

    function update(animate) {
        if (mode !== 'scroll') return;
        paint(stepAt(window.scrollY - walk.start), animate);
        read();
    }

    function read() {
        if (mode !== 'scroll' || box.hasAttribute('data-moving')) return;
        const spare = box.scrollHeight - box.clientHeight;
        if (spare < 1) return;
        const [first, last] = runs[index] || [index, index];
        const into = window.scrollY - walk.start - starts[first];
        const through = clamp(into / (starts[last] + paces[last] - starts[first]), 0, 1);
        box.scrollTop = Math.round(through * spare);
    }

    function switchTo(next) {
        if (next === mode) return;
        mode = next;
        host.dataset.mode = next;
        if (status) status.textContent = '';
    }

    function measure() {
        const top = walkthroughHeader();
        const width = window.innerWidth;
        const height = window.innerHeight;
        const narrow = width < WALKTHROUGH_NARROW;
        rejoin();
        still();
        land();
        host.setAttribute('data-measuring', '');
        pane.style.removeProperty('min-height');
        if (out) {
            out.hidden = !written.length;
            const rows = text.replace(/\n$/, '').split('\n').length;
            host.style.setProperty(
                '--km-walkthrough-out-rows',
                String(Math.min(WALKTHROUGH_OUT_LINES, rows)),
            );
        }
        const tucked = !host.getClientRects().length
            || host.closest('.site-page--clamped') !== null;
        switchTo(prefersReducedMotion() || tucked ? 'pager' : 'scroll');
        host.style.removeProperty('--km-walkthrough-stage');
        const size = code.offsetHeight;
        const line = lines.get(1)?.getBoundingClientRect().height || 20;
        const pad = Math.max(0, size - line * lines.size);
        row = line;
        inset = pad / 2;
        wholes = codes ? texts.map((rows) => pad + line * rows.length) : [size];
        const printing = out && !out.hidden ? out.getBoundingClientRect().height : 0;
        const rest = box.offsetTop - frame.offsetTop - stage.offsetHeight - printing;
        boxes = codes && printing ? outline() : [];
        const outs = wholes.map((_, at) => boxes[at] ?? printing);
        resize(version);
        const above = lead
            ? frame.getBoundingClientRect().top - pane.getBoundingClientRect().top
            : 0;
        const share = narrow ? WALKTHROUGH_LEAD_NARROW : WALKTHROUGH_LEAD;
        const keep = clamp(Math.round(height * share), 0, above);
        const leasts = wholes.map((tall) => Math.min(tall, pad + line * WALKTHROUGH_MIN_LINES));
        const frees = outs.map((tall) => height - top - keep - rest - tall);
        const mosts = wholes.map((tall, at) => Math.min(tall, Math.max(leasts[at], narrow
            ? pad + line * WALKTHROUGH_LINES
            : (height - top) * WALKTHROUGH_SHARE - rest - outs[at])));
        most = mosts[codes ? version : 0];
        const spare = Math.min(...frees.map((free, at) => free - leasts[at]));
        if (mode === 'scroll' && spare < WALKTHROUGH_ROOM) switchTo('pager');
        host.style.setProperty('--km-walkthrough-notes', `${Math.floor(spare)}px`);
        const heights = new Map();
        notes.forEach((note) => note.removeAttribute('data-shown'));
        heights.set(-1, walkthroughHeight(box));
        notes.forEach((note, key) => {
            note.setAttribute('data-shown', '');
            heights.set(key, walkthroughHeight(box));
            note.removeAttribute('data-shown');
        });
        notes.get(shown)?.setAttribute('data-shown', '');
        const lined = (note, at) => {
            const fits = clamp(frees[at] - note, leasts[at], mosts[at]);
            const rows = fits < wholes[at] ? pad + line * Math.floor((fits - pad) / line) : fits;
            return Math.max(leasts[at], rows);
        };
        fitted = new Map();
        if (codes) {
            steps.forEach((step, at) => {
                fitted.set(at, lined(heights.get(step.note ?? -1) ?? 0, step.version ?? 0));
            });
        } else {
            heights.forEach((note, key) => fitted.set(key, lined(note, 0)));
        }
        fit();
        const note = steps[steps.length - 1].note ?? -1;
        const last = codes ? steps.length - 1 : note;
        const ending = outs[codes ? steps[steps.length - 1].version ?? 0 : 0] - outs[codes ? version : 0];
        const base = walkthroughHeight(pane) - walkthroughHeight(stage) - walkthroughHeight(box);
        walk.stick = top - (above - keep);
        walk.span = mode === 'scroll' ? length : 0;
        const floor = narrow && walk.span ? Math.ceil(walkthroughScreen() - walk.stick) : 0;
        walk.resting = Math.max(
            floor,
            base + ending + Math.floor(fitted.get(last) ?? most) + (heights.get(note) ?? 0),
        );
        pane.style.minHeight = floor ? `${floor}px` : '';
        walk.tail = walk.span ? walkthroughTail(host) : [];
        host.style.marginBottom = walk.span ? `${trailing()}px` : '';
        host.style.height = walk.span ? `${walk.span + walk.resting}px` : '';
        host.style.setProperty('--km-walkthrough-stick', `${walk.stick}px`);
        if (mode === 'pager') paint(Math.max(0, index), false);
        void host.offsetHeight;
        host.removeAttribute('data-measuring');
        walk.shaped = shape();
    }

    function go(at) {
        if (mode === 'pager') {
            paint(at);
            return;
        }
        smoothScrollTo(walk.start + starts[at] + paces[at] / 2, TIMING.scrollMin());
    }

    function release() {
        if (!loose) return;
        rejoin();
        if (current) follow(current);
        edge();
    }

    function unfold(value) {
        const open = value.toggleAttribute('data-open');
        value.setAttribute('aria-expanded', String(open));
        if (open) opened.add(value.dataset.key);
        else opened.delete(value.dataset.key);
        edge();
    }

    stage.addEventListener('scroll', rafThrottle(edge), { passive: true });
    box.addEventListener('scroll', rafThrottle(edge), { passive: true });

    stage.addEventListener('click', (event) => {
        const value = event.target.closest?.('[data-long]');
        if (value) unfold(value);
    });

    stage.addEventListener('keydown', (event) => {
        if (event.key !== 'Enter' && event.key !== ' ') return;
        if (!event.target.matches?.('[data-long]')) return;
        event.preventDefault();
        unfold(event.target);
    });

    stage.addEventListener('pointerdown', (event) => {
        touched = event.pointerType === 'touch';
        loosen();
    });
    stage.addEventListener('focusin', loosen);
    stage.addEventListener('focusout', (event) => {
        if (!stage.contains(event.relatedTarget)) release();
    });

    box.addEventListener('focusin', (event) => {
        const note = event.target.closest?.('[data-note]');
        if (!mode || !note || note.hasAttribute('data-shown')) return;
        const at = steps.findIndex((step) => step.note === Number(note.dataset.note));
        if (at >= 0) go(at);
    });

    host.addEventListener('load', () => {
        walk.shaped = '';
        walkthroughSoon();
    }, true);

    buttons.forEach((button) => {
        button.addEventListener('click', () => {
            paint(index + Number(button.dataset.step));
        });
    });

    host.addEventListener('keydown', (event) => {
        if (mode !== 'pager' || event.altKey || event.ctrlKey || event.metaKey) return;
        if (!pane.contains(event.target) || event.target === stage) return;
        if (WALKTHROUGH_KEYS[event.key]) {
            event.preventDefault();
            paint(index + WALKTHROUGH_KEYS[event.key]);
        } else if (event.key === 'Home' || event.key === 'End') {
            event.preventDefault();
            paint(event.key === 'Home' ? 0 : steps.length - 1);
        }
    });

    const idle = copy?.dataset.tooltip || 'Copy';
    const copied = (message) => {
        copy.dataset.tooltip = message;
        copy.classList.add('success');
        window.setTimeout(() => {
            copy.classList.remove('success');
            copy.dataset.tooltip = idle;
        }, TIMING.tooltipHold());
    };
    copy?.addEventListener('click', () => {
        copyText(codes ? codes[version] : walkthroughSource(payload))
            .then((done) => copied(done ? 'Copied!' : 'Copy failed'));
    });

    return walk;
}

function initWalkthroughs() {
    document.querySelectorAll('[data-walkthrough]').forEach((host) => {
        const walk = createWalkthrough(host);
        if (walk) walkthroughs.push(walk);
    });
    if (!walkthroughs.length) return;
    walkthroughMeasure();
    onScroll(walkthroughTick);

    if ('ResizeObserver' in window) {
        const panes = new ResizeObserver(() => {
            walkthroughDraw();
            walkthroughSoon();
        });
        walkthroughs.forEach((walk) => panes.observe(walk.pane));
        new ResizeObserver(walkthroughSoon).observe(document.body);
    }

    document.addEventListener('km:fold', walkthroughMeasure);
    document.addEventListener('focusin', (event) => {
        if (walkthroughMoved(event.target)) walkthroughReach(event.target);
    });

    let width = window.innerWidth;
    let height = window.innerHeight;
    let resizing = 0;
    window.addEventListener('resize', () => {
        window.clearTimeout(resizing);
        resizing = window.setTimeout(() => {
            const moved = Math.abs(window.innerHeight - height);
            if (window.innerWidth === width && moved < WALKTHROUGH_JITTER) return;
            width = window.innerWidth;
            height = window.innerHeight;
            walkthroughMeasure();
        }, WALKTHROUGH_SETTLE);
    }, { passive: true });

    window.matchMedia('(prefers-reduced-motion: reduce)')
        .addEventListener?.('change', walkthroughMeasure);
    document.fonts?.ready.then(walkthroughMeasure);
}

ready(() => {
    for (const init of [
        syncThemeColor,
        initPrintColours,
        initSystemColours,
        initThemeToggle,
        initKeyboardModality,
        initSidebar,
        initScrollTop,
        initCalNamespaces,
        initShowMore,
        initHeaderSearch,
        initAnchorScrolling,
        initCopyUrl,
        initHeaderLinks,
        initHeaderBorder,
        initImageZoom,
        initTouchReveal,
        initHeaderNavDropdowns,
        initDropdowns,
        initHighlightedLines,
        initCopyButtonNames,
        initScrollable,
        initYouTubeCards,
        initRepositoryWidgets,
        initInkReveal,
        initPageReveal,
        initArticleBackground,
        initWalkthroughs,
    ]) {
        try {
            init();
        } catch (error) {
            console.error(error);
        }
    }
});
