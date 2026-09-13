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

const root = document.documentElement;

function ready(fn) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
        fn();
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

window.simpleGetDurationMs = getDurationMs;

const TIMING = {
    dropdownMin: () => getDurationMs('--km-duration-dropdown-min', 340),
    dropdownMax: () => getDurationMs('--km-duration-dropdown-max', 760),
    revealStep: () => getDurationMs('--km-reveal-step', 90),
    scrollMin: () => getDurationMs('--km-scroll-min', 450),
    scrollMax: () => getDurationMs('--km-scroll-max', 900),
    tooltipHold: () => getDurationMs('--km-tooltip-hold', 1800),
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

function applyTheme(mode) {
    const resolved = resolveTheme(mode);
    const commit = () => {
        root.setAttribute('data-theme', resolved);
        root.classList.toggle('dark', resolved === 'dark');
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

window.simpleApplyTheme = applyTheme;

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

    const tail = () => button.getBoundingClientRect().height + CLAMP_GAP_PX;

    const fit = () => {
        const top = window.scrollY + content.getBoundingClientRect().top;
        const viewport = window.visualViewport?.height || window.innerHeight;
        const room = Math.max(CLAMP_MIN_PX, viewport - top - tail());
        page.style.setProperty('--km-show-more-clamp', `${Math.round(room)}px`);
    };

    const settle = (next) => {
        window.clearTimeout(timer);
        page.classList.remove('site-page--clamping');
        page.classList.toggle('site-page--clamped', !next);
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
        if (window.scrollY <= targetY) return;
        smoothScrollTo(targetY, TIMING.scrollMin());
    };

    const toggle = (next, animate = true) => {
        if (next === expanded) return;
        expanded = next;
        button.setAttribute('aria-expanded', next ? 'true' : 'false');
        if (label) {
            label.textContent = next
                ? button.dataset.labelLess
                : button.dataset.labelMore;
        }

        const start = content.getBoundingClientRect().height;
        const { collapsed, full } = measure();
        if (!next) keepInView(collapsed);
        if (!animate || prefersReducedMotion()) {
            settle(next);
            return;
        }

        page.classList.toggle('site-page--clamped', !next);
        page.classList.add('site-page--clamping');
        content.style.maxHeight = `${start}px`;
        void content.offsetHeight;
        content.style.maxHeight = `${next ? full : collapsed}px`;
        window.clearTimeout(timer);
        timer = window.setTimeout(
            () => settle(next),
            getDurationMs('--km-duration-clamp', 420) + CLAMP_SETTLE_MS,
        );
    };

    const holds = (href) => {
        if (!href.startsWith('#') || href.length < 2) return false;
        let id = href.slice(1);
        try { id = decodeURIComponent(id); } catch { /* noop */ }
        const target = document.getElementById(id);
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
        if (!expanded && holds(location.hash)) toggle(true, false);
    });

    window.addEventListener('resize', rafThrottle(fit), { passive: true });

    if (holds(location.hash)) toggle(true, false);
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
        input.setAttribute('aria-expanded', 'true');
    };
    const close = () => {
        if (input && input.value.trim()) return;
        search.classList.remove('is-open');
        if (input) input.setAttribute('aria-expanded', 'false');
    };

    submit?.addEventListener('click', (event) => {
        if (search.classList.contains('is-open')) return;
        event.preventDefault();
        open();
    });

    input?.addEventListener('focus', () => {
        search.classList.add('is-open');
        input.setAttribute('aria-expanded', 'true');
    });
    input?.addEventListener('blur', () => setTimeout(close, 0));
    input?.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        close();
        input.blur();
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

function scrollToElement(element) {
    const targetY = anchorTargetY(element);
    const base = TIMING.scrollMin();
    const distance = Math.abs(window.scrollY - targetY);

    const duration = Math.max(TIMING.scrollMin(), Math.min(
        TIMING.scrollMax(),
        base + Math.min(ANCHOR_SCROLL_DIST_CAP_MS, distance * ANCHOR_SCROLL_PX_FACTOR),
    ));
    return smoothScrollTo(targetY, duration);
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
        const id = decodeURIComponent(href.slice(1));
        const target = document.getElementById(id);
        if (!target) return;

        event.preventDefault();
        scrollToElement(target).then(() => {
            try { history.pushState(null, '', `#${id}`); } catch { /* noop */ }
        });
    });

    settleHash();
}

function settleHash() {
    if (location.hash.length <= 1) return;
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
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

function initCopyUrl() {
    const links = document.querySelectorAll('a.copy-url');
    if (!links.length) return;
    const canonical = document.querySelector('link[rel="canonical"]');

    links.forEach((link) => {
        link.addEventListener('click', async (event) => {
            event.preventDefault();
            event.stopPropagation();
            let copied = false;
            try {
                await navigator.clipboard.writeText(canonical?.href || window.location.href);
                copied = true;
            } catch { /* clipboard unavailable */ }
            link.setAttribute('data-tooltip', copied ? 'Copied!' : 'Copy failed');
            link.classList.add('show-tooltip');
            setTimeout(() => link.classList.remove('show-tooltip'), TIMING.tooltipHold());
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
        const open = () => {
            clearTimeout(closeTimer);
            openTimer = setTimeout(() => {
                group.classList.add('is-open');
                caption.setAttribute('aria-expanded', 'true');
            }, DROPDOWN_OPEN_DELAY_MS);
        };
        const close = () => {
            clearTimeout(openTimer);
            closeTimer = setTimeout(() => {
                group.classList.remove('is-open');
                caption.setAttribute('aria-expanded', 'false');
            }, DROPDOWN_CLOSE_DELAY_MS);
        };

        caption.addEventListener('mouseenter', open, { passive: true });
        group.addEventListener('mouseenter', open, { passive: true });
        group.addEventListener('mouseleave', close, { passive: true });
        caption.addEventListener('focus', open, { passive: true });
        group.addEventListener('focusout', (event) => {
            if (!group.contains(event.relatedTarget)) close();
        });
        caption.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                if (group.classList.contains('is-open')) close(); else open();
            } else if (event.key === 'Escape') {
                close();
                caption.blur();
            }
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

            const height = content.scrollHeight;
            const duration = Math.min(TIMING.dropdownMax(),
                Math.max(TIMING.dropdownMin(), height * DROPDOWN_PX_FACTOR));
            details.classList.add('is-animating');

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

    const watch = encodeURIComponent(`https://www.youtube.com/watch?v=${id}`);
    fetchJson(`https://www.youtube.com/oembed?url=${watch}&format=json`).then((data) => {
        if (!data) return;
        const title = card.querySelector('.site-youtube-card__title');
        const channel = card.querySelector('.site-youtube-card__channel');
        if (title && data.title) title.textContent = data.title;
        if (channel && data.author_name) channel.textContent = data.author_name;
    });
}

function initYouTubeCards() {
    onVisible(
        document.querySelectorAll('.site-youtube-card[data-youtube-id], .youtube-card-container[data-youtube-id]'),
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
        reel.animate([{ transform: 'translateY(0%)' }, { transform: shift }], {
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
        document.querySelectorAll('.marker, .pencil'),
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
        element.classList.add('page-reveal-item');
        element.style.setProperty('--km-reveal-delay', `${delay}ms`);
        delay += TIMING.revealStep();
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

    if (urls.length === 1) return;
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
    const seen = new Set();
    document.querySelectorAll('[data-cal-namespace]').forEach((el) => {
        const ns = el.getAttribute('data-cal-namespace');
        if (!ns || seen.has(ns)) return;
        seen.add(ns);
        Cal('init', ns, { origin: CAL_ORIGIN });
        Cal.ns[ns]('ui', { hideEventTypeDetails: false, layout: 'month_view' });
    });
}

ready(() => {
    initCalNamespaces();
    initShowMore();
    initHeaderSearch();
    initAnchorScrolling();
    initCopyUrl();
    initHeaderBorder();
    initImageZoom();
    initTouchReveal();
    initHeaderNavDropdowns();
    initDropdowns();
    initYouTubeCards();
    initRepositoryWidgets();
    initInkReveal();
    initPageReveal();
    initArticleBackground();
});
