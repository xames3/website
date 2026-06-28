const WORDS_PER_MINUTE = 225;
const SCROLL_DURATION_MIN_MS = 300;
const SCROLL_DURATION_MAX_MS = 1800;
const ANCHOR_SCROLL_MIN_MS = 1500;
const ANCHOR_SCROLL_MAX_MS = 4000;
const ANCHOR_SCROLL_BASE_MS = 2500;
const ANCHOR_SCROLL_PX_FACTOR = 1.5;
const ANCHOR_SCROLL_DIST_CAP_MS = 1000;
const HEADER_OFFSET_DEFAULT_PX = 40;
const ANCHOR_EXTRA_OFFSET_DEFAULT_PX = 12;
const HEADER_BORDER_SCROLL_THRESHOLD = 250;
const TOOLTIP_DISPLAY_MS = 1800;
const DROPDOWN_OPEN_DELAY_MS = 40;
const DROPDOWN_CLOSE_DELAY_MS = 140;
const DESKTOP_BREAKPOINT_PX = 1024;
const YOUTUBE_FETCH_TIMEOUT_MS = 8000;
const REVEAL_STEP_MS = 90;

function getDurationMs(cssVar = '--km-duration-normal', fallback = 500) {
    try {
        const raw = getComputedStyle(document.documentElement)
            .getPropertyValue(cssVar).trim();
        if (!raw) return fallback;
        if (raw.endsWith('ms')) return Math.max(0, parseFloat(raw));
        if (raw.endsWith('s')) return Math.max(0, parseFloat(raw) * 1000);
        const n = Number(raw);
        return isNaN(n) ? fallback : n;
    } catch { return fallback; }
}

window.simpleGetDurationMs = getDurationMs;

function applyTheme(mode, prevMode, maxWait) {
    const root = document.documentElement;
    const dur = getDurationMs('--km-duration-normal', 500);
    const debounce = Math.max(60, Math.round(dur * 0.25));
    const timeout = maxWait ?? Math.max(dur * 3, dur + 500);

    // Resolve 'system' to actual rendered value
    const resolve = (m) => {
        if (m === 'system') return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        return m || 'light';
    };

    // Alpine's :data-theme binding fires before $watch, so data-theme may already
    // equal mode. Briefly revert to previous value so transitions have something to
    // animate from, then force a reflow to commit both theme-transition + old value.
    const resolvedPrev = resolve(prevMode);
    if (resolvedPrev && resolvedPrev !== mode && root.getAttribute('data-theme') === mode) {
        root.setAttribute('data-theme', resolvedPrev);
    }

    root.classList.add('theme-transition');
    void root.offsetWidth; // force style recalc: commit theme-transition with old data-theme
    root.setAttribute('data-theme', mode); // triggers smooth transitions

    let doneTimer;
    function cleanup() {
        root.classList.remove('theme-transition');
        root.removeEventListener('transitionend', onEnd, true);
        if (doneTimer) clearTimeout(doneTimer);
    }
    function onEnd(e) {
        if (!e || !e.propertyName) return;
        if (['color', 'background-color', 'border-color', 'fill', 'stroke',
            'box-shadow', 'text-decoration-color'].includes(e.propertyName)) {
            if (doneTimer) clearTimeout(doneTimer);
            doneTimer = setTimeout(cleanup, debounce);
        }
    }
    root.addEventListener('transitionend', onEnd, true);
    doneTimer = setTimeout(cleanup, timeout);
}

window.simpleApplyTheme = applyTheme;

document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('content')
        || document.querySelector('[role="main"]')
        || document.querySelector('section');
    if (!root) return;

    const totalWords = Array.from(root.querySelectorAll('p')).reduce((acc, p) => {
        if (p.closest('pre, code, figure, figcaption, .literal-block-wrapper, .highlight, .code-block-caption, .math, .sidebar, .site-sidebar, .sphinxsidebar, .admonition, nav, header, footer')) {
            return acc;
        }
        const clone = p.cloneNode(true);
        clone.querySelectorAll('code, pre, kbd, samp, .linenos, .copybtn, .headerlink, svg, i.fa, .fa')
            .forEach(n => n.remove());
        const text = (clone.textContent || '').replace(/\s+/g, ' ').trim();
        if (!text || text.length < 20) return acc;
        return acc + text.split(/\s+/).filter(tok => /[\p{L}\p{N}]/u.test(tok)).length;
    }, 0);

    if (totalWords > 0) {
        const minutes = Math.ceil(totalWords / WORDS_PER_MINUTE);
        const rt = document.getElementById('readingTime');
        if (rt) rt.innerHTML = `<i class='fa-solid fa-hourglass-start' style='margin-right: 0.5rem;'></i>${minutes} min read`;
    }
});

(function () {
    const search = document.querySelector('.site-header__search .site-search');
    if (!search) return;
    const input = search.querySelector('.site-search__input');
    const submit = search.querySelector('.site-search__submit');

    function open() {
        search.classList.add('is-open');
        if (input) {
            input.focus({ preventScroll: true });
            input.setAttribute('aria-expanded', 'true');
        }
    }
    function close() {
        if (input && input.value.trim()) return;
        search.classList.remove('is-open');
        if (input) input.setAttribute('aria-expanded', 'false');
    }

    if (submit) {
        submit.addEventListener('click', (e) => {
            if (!search.classList.contains('is-open')) {
                e.preventDefault();
                open();
            }
        });
    }
    if (input) {
        input.addEventListener('focus', () => {
            search.classList.add('is-open');
            input.setAttribute('aria-expanded', 'true');
        });
        input.addEventListener('blur', () => setTimeout(close, 0));
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { close(); input.blur(); }
        });
    }
    document.addEventListener('click', (e) => {
        if (!search.contains(e.target)) close();
    });
})();

(function () {
    function getCssVarRaw(name) {
        try { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
        catch { return ''; }
    }

    function toPx(val, basePx) {
        if (!val) return basePx;
        if (val.endsWith('px')) return parseFloat(val) || basePx;
        if (val.endsWith('rem')) {
            const fs = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
            return (parseFloat(val) || 0) * fs;
        }
        if (val.endsWith('em')) {
            const fs = parseFloat(getComputedStyle(document.body).fontSize) || 16;
            return (parseFloat(val) || 0) * fs;
        }
        const n = parseFloat(val);
        return isNaN(n) ? basePx : n;
    }

    function getHeaderOffsetPx() {
        const cssPx = toPx(getCssVarRaw('--km-layout-header-offset'), HEADER_OFFSET_DEFAULT_PX)
            + toPx(getCssVarRaw('--km-layout-anchor-offset'), ANCHOR_EXTRA_OFFSET_DEFAULT_PX);
        const header = document.querySelector('header');
        const headerPx = header ? Math.ceil(header.getBoundingClientRect().height) : 0;
        return Math.max(0, cssPx, headerPx);
    }

    function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

    function smoothScrollTo(targetY, duration) {
        const startY = window.pageYOffset || document.documentElement.scrollTop || 0;
        const maxY = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
        const clampedTarget = Math.min(maxY, Math.max(0, targetY));
        const distance = clampedTarget - startY;

        if (Math.abs(distance) < 1) { window.scrollTo(0, clampedTarget); return Promise.resolve(); }

        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            window.scrollTo(0, clampedTarget);
            return Promise.resolve();
        }

        const start = performance.now();
        const dur = Math.max(SCROLL_DURATION_MIN_MS, Math.min(duration, SCROLL_DURATION_MAX_MS));
        const root = document.documentElement;
        const prevBehavior = root.style.scrollBehavior;
        root.style.scrollBehavior = 'auto';

        return new Promise(resolve => {
            function step(now) {
                const t = Math.min(1, (now - start) / dur);
                window.scrollTo(0, startY + distance * easeOutCubic(t));
                if (t < 1) requestAnimationFrame(step);
                else {
                    root.style.scrollBehavior = prevBehavior || '';
                    resolve();
                }
            }
            requestAnimationFrame(step);
        });
    }

    function onAnchorClick(e) {
        const href = this.getAttribute('href') || '';
        if (href === '#' || !href.startsWith('#')) return;
        const id = href.slice(1);
        const el = document.getElementById(id);
        if (!el) return;

        e.preventDefault();
        const rect = el.getBoundingClientRect();
        const headerOffset = getHeaderOffsetPx();
        const targetY = (window.pageYOffset || document.documentElement.scrollTop || 0) + rect.top - headerOffset;
        const base = getDurationMs('--km-duration-slow', ANCHOR_SCROLL_BASE_MS);
        const dist = Math.abs((window.pageYOffset || 0) - targetY);
        const duration = Math.max(ANCHOR_SCROLL_MIN_MS,
            Math.min(ANCHOR_SCROLL_MAX_MS, base + Math.min(ANCHOR_SCROLL_DIST_CAP_MS, dist * ANCHOR_SCROLL_PX_FACTOR)));

        smoothScrollTo(targetY, duration).then(() => {
            try { history.pushState(null, '', '#' + id); } catch { /* noop */ }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const links = document.querySelectorAll('a[href^="#"]');
        for (const link of links) {
            link.addEventListener('click', onAnchorClick, { passive: false });
        }
        if (location.hash && location.hash.length > 1) {
            const id = decodeURIComponent(location.hash.slice(1));
            const el = document.getElementById(id);
            if (el) {
                requestAnimationFrame(() => {
                    const root = document.documentElement;
                    const prevBehavior = root.style.scrollBehavior;
                    root.style.scrollBehavior = 'auto';
                    const rect = el.getBoundingClientRect();
                    const headerOffset = getHeaderOffsetPx();
                    const y = (window.pageYOffset || document.documentElement.scrollTop || 0) + rect.top - headerOffset;
                    window.scrollTo(0, Math.max(0, y));
                    root.style.scrollBehavior = prevBehavior || '';
                });
            }
        }
    });
})();

(function () {
    function showTooltip(el, text) {
        if (text) el.setAttribute('data-tooltip', text);
        el.classList.add('show-tooltip');
        setTimeout(() => el.classList.remove('show-tooltip'), TOOLTIP_DISPLAY_MS);
    }

    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch {
            return false;
        }
    }

    function getCanonicalUrl() {
        const c = document.querySelector('link[rel="canonical"]');
        return (c && c.href) ? c.href : window.location.href;
    }

    function initCopyUrl() {
        const links = document.querySelectorAll('a.copy-url');
        if (!links.length) return;
        links.forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                const ok = await copyToClipboard(getCanonicalUrl());
                showTooltip(link, ok ? 'Copied!' : 'Copy failed');
            }, { passive: false });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCopyUrl);
    } else {
        initCopyUrl();
    }
})();

(function () {
    function onScroll() {
        const sc = window.scrollY || document.documentElement.scrollTop;
        const header = document.querySelector('.site-header');
        if (!header) return;
        header.classList.toggle('site-header--with-border', sc > HEADER_BORDER_SCROLL_THRESHOLD);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();

(function () {
    document.addEventListener('pointerdown', (e) => {
        const el = e.target.closest('.sd-card, .admonition, a:not(.headerlink), button');
        if (!el) return;
        el.classList.add('is-active');
        function release() {
            el.classList.remove('is-active');
            el.removeEventListener('pointerup', release);
            el.removeEventListener('pointerleave', release);
            el.removeEventListener('blur', release);
        }
        el.addEventListener('pointerup', release, { passive: true, once: true });
        el.addEventListener('pointerleave', release, { passive: true, once: true });
        el.addEventListener('blur', release, { passive: true, once: true });
    }, { passive: true });
})();

(function () {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    function setupZoom(el, wrapperParent, isStandalone = false) {
        if (!el || el.classList.contains('no-zoom')) {
            if (wrapperParent) wrapperParent.dataset.zoomReady = 'true';
            return;
        }

        const wrapper = document.createElement('div');
        wrapper.className = isStandalone ? 'zoom-inner zoom-inner--standalone' : 'zoom-inner';

        if (el instanceof HTMLImageElement) {
            el.style.cssText = 'display:block;width:100%;height:auto';
            if (isStandalone) el.style.margin = '0';
        }

        const scale = document.createElement('div');
        scale.className = 'zoom-scale';

        const parent = wrapperParent || el.parentElement;
        parent.insertBefore(wrapper, el);
        wrapper.appendChild(scale);
        scale.appendChild(el);
    }

    // Figures with .zoom class
    const figures = document.querySelectorAll('#content figure.zoom:not([data-zoom-ready]) > img');
    for (const el of figures) {
        const figure = el.parentElement;
        if (!figure || figure.dataset.zoomReady === 'true') continue;
        setupZoom(el, figure);
        figure.dataset.zoomReady = 'true';
    }

    // Standalone images with .zoom class
    const singles = document.querySelectorAll('#content img.zoom:not(figure img):not(.no-zoom):not([data-zoom-ready])');
    for (const img of singles) {
        if (img.dataset.zoomReady === 'true') continue;
        setupZoom(img, null, true);
        img.dataset.zoomReady = 'true';
    }
})();

function initLeftSidebarAccordion() {
    const sidebars = document.querySelectorAll('.site-sidebar--primary');
    if (!sidebars.length) return;

    sidebars.forEach((sidebar) => {
        let uid = 0;

        function setExpanded(li, expanded) {
            li.setAttribute('aria-expanded', expanded ? 'true' : 'false');
        }
        function collapseOthers(except) {
            for (const o of sidebar.querySelectorAll('li.has-children[aria-expanded="true"]')) {
                if (o !== except) setExpanded(o, false);
            }
        }
        function toggle(li) {
            const isOpen = li.getAttribute('aria-expanded') === 'true';
            if (isOpen) setExpanded(li, false);
            else { collapseOthers(li); setExpanded(li, true); }
        }

        for (const li of sidebar.querySelectorAll('li')) {
            const childList = li.querySelector(':scope > ul');
            const anchor = li.querySelector(':scope > a, :scope > p > a');
            if (!childList || !anchor) continue;

            childList.removeAttribute('hidden');
            childList.style.removeProperty('display');
            li.classList.add('has-children');

            const controlId = childList.id || `nav-branch-${++uid}`;
            childList.id = controlId;

            const btn = li.querySelector(':scope > button.nav-toggle, :scope > a > button.nav-toggle');
            if (btn) btn.setAttribute('aria-controls', controlId);

            const branchIsCurrent = li.classList.contains('current')
                || anchor.classList.contains('current')
                || !!li.querySelector(':scope > ul .current');

            if (branchIsCurrent) {
                setExpanded(li, false);
                requestAnimationFrame(() => setExpanded(li, true));
            } else {
                setExpanded(li, false);
            }

            if (btn) btn.addEventListener('click', (e) => {
                e.preventDefault(); e.stopPropagation(); toggle(li);
            }, { passive: false });

            anchor.addEventListener('click', (e) => {
                const href = anchor.getAttribute('href') || '';
                if (href && !href.startsWith('#')) {
                    e.preventDefault(); e.stopPropagation();
                    collapseOthers(li);
                    setExpanded(li, true);
                    const d = getDurationMs('--km-duration-normal', 500);
                    setTimeout(() => { window.location.href = href; }, d);
                } else {
                    e.preventDefault(); e.stopPropagation();
                    toggle(li);
                }
            }, { passive: false });

            anchor.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); toggle(li); }
                if (e.key === 'ArrowRight') { e.preventDefault(); e.stopPropagation(); collapseOthers(li); setExpanded(li, true); }
                if (e.key === 'ArrowLeft') { e.preventDefault(); e.stopPropagation(); setExpanded(li, false); }
            });
        }

        sidebar.addEventListener('click', (e) => {
            const toggleBtn = e.target.closest('button.nav-toggle');
            if (toggleBtn && sidebar.contains(toggleBtn)) {
                const li = toggleBtn.closest('li');
                if (li && li.classList.contains('has-children')) {
                    e.preventDefault(); e.stopPropagation();
                    toggle(li);
                }
            }
        }, { passive: false });

        const expanded = sidebar.querySelectorAll('li.has-children[aria-expanded="true"]');
        if (expanded.length > 1) {
            const keep = Array.from(expanded).find(li => li.querySelector(':scope .current')) || expanded[0];
            collapseOthers(keep);
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLeftSidebarAccordion);
} else {
    initLeftSidebarAccordion();
}

(function () {
    try {
        document.querySelectorAll('[x-cloak]').forEach(el => {
            el.removeAttribute('x-cloak');
            el.style.removeProperty('display');
        });
    } catch { /* noop */ }

    if (document.body.dataset.sidebarInit === '1') return;
    document.body.dataset.sidebarInit = '1';

    function initMobileSidebar() {
        const sidebar = document.querySelector('.site-sidebar--primary');
        if (!sidebar) return;

        let backdrop = document.querySelector('.site-sidebar__backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'site-sidebar__backdrop';
            document.body.appendChild(backdrop);
        }

        const toggles = Array.from(document.querySelectorAll('[data-sidebar-toggle]'));
        const closers = Array.from(document.querySelectorAll('[data-sidebar-close]'));

        function open() {
            document.body.classList.add('site-body--sidebar-open', 'site-body--locked');
        }
        function close() {
            document.body.classList.remove('site-body--sidebar-open', 'site-body--locked');
        }
        function toggle(e) {
            if (e) e.preventDefault();
            if (document.body.classList.contains('site-body--sidebar-open')) close(); else open();
        }

        toggles.forEach(btn => btn.addEventListener('click', toggle, { passive: false }));
        backdrop.addEventListener('click', close);
        closers.forEach(btn => btn.addEventListener('click', (e) => { e.preventDefault(); close(); }));
        document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
        sidebar.addEventListener('click', e => { if (e.target.closest('a')) close(); });

        let lastW = window.innerWidth;
        window.addEventListener('resize', () => {
            const w = window.innerWidth;
            if (w !== lastW) {
                if (w >= DESKTOP_BREAKPOINT_PX) close();
                lastW = w;
            }
        }, { passive: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileSidebar, { once: true });
    } else {
        initMobileSidebar();
    }
})();

(function () {
    function buildHeaderNavDropdowns() {
        const nav = document.querySelector('.site-header__nav-tree');
        if (!nav) return;
        const captions = Array.from(nav.querySelectorAll('p.caption'));
        if (!captions.length) return;

        let uid = 0;
        captions.forEach((caption) => {
            const list = caption.nextElementSibling;
            if (!list || list.tagName !== 'UL') return;

            const wrapper = document.createElement('div');
            wrapper.className = 'site-header__nav-group';
            caption.parentNode.insertBefore(wrapper, caption);
            wrapper.appendChild(caption);
            wrapper.appendChild(list);

            const listId = list.id || `nav-group-${++uid}`;
            list.id = listId;
            caption.setAttribute('tabindex', '0');
            caption.setAttribute('role', 'button');
            caption.setAttribute('aria-haspopup', 'true');
            caption.setAttribute('aria-controls', listId);
            caption.setAttribute('aria-expanded', 'false');

            let openTimer = null;
            let closeTimer = null;

            const open = () => {
                clearTimeout(closeTimer);
                openTimer = setTimeout(() => {
                    wrapper.classList.add('is-open');
                    caption.setAttribute('aria-expanded', 'true');
                }, DROPDOWN_OPEN_DELAY_MS);
            };
            const close = () => {
                clearTimeout(openTimer);
                closeTimer = setTimeout(() => {
                    wrapper.classList.remove('is-open');
                    caption.setAttribute('aria-expanded', 'false');
                }, DROPDOWN_CLOSE_DELAY_MS);
            };

            caption.addEventListener('mouseenter', open, { passive: true });
            wrapper.addEventListener('mouseenter', open, { passive: true });
            wrapper.addEventListener('mouseleave', close, { passive: true });
            caption.addEventListener('focus', open, { passive: true });
            wrapper.addEventListener('focusout', (e) => {
                if (!wrapper.contains(e.relatedTarget)) close();
            });

            caption.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    wrapper.classList.contains('is-open') ? close() : open();
                }
                if (e.key === 'Escape') { close(); caption.blur(); }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', buildHeaderNavDropdowns, { once: true });
    } else {
        buildHeaderNavDropdowns();
    }
})();

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('h1').forEach(h1 => {
        const text = h1.textContent;
        const trimmed = text.replace(/^\s+/, '');
        if (text !== trimmed) h1.textContent = trimmed;
    });
});

(function () {
    function intersectOnce(nodes, onEnter) {
        const list = Array.from(nodes);
        if (!list.length) return;
        if (!('IntersectionObserver' in window)) { list.forEach(onEnter); return; }
        const io = new IntersectionObserver((entries) => {
            for (const e of entries) {
                if (e.isIntersecting) { io.unobserve(e.target); onEnter(e.target); }
            }
        }, { rootMargin: '200px' });
        list.forEach(n => io.observe(n));
    }

    async function enrichYouTubeCard(card) {
        const host = card.matches('[data-youtube-id]') ? card : card.closest('[data-youtube-id]');
        if (!host || host.dataset.youtubeEnriched === '1') return;
        const vid = host.getAttribute('data-youtube-id');
        if (!vid) { host.dataset.youtubeEnriched = '1'; return; }

        const url = 'https://www.youtube.com/oembed?url='
            + encodeURIComponent('https://www.youtube.com/watch?v=' + vid) + '&format=json';

        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), YOUTUBE_FETCH_TIMEOUT_MS);
        try {
            const res = await fetch(url, { signal: ctrl.signal });
            if (!res.ok) throw new Error(String(res.status));
            const data = await res.json();
            const titleEl = host.querySelector('.site-youtube-card__title');
            const channelEl = host.querySelector('.site-youtube-card__channel');
            if (titleEl && data.title) titleEl.textContent = data.title;
            if (channelEl && data.author_name) channelEl.textContent = data.author_name;
        } catch {
            /* Network errors are non-critical; card keeps its fallback text. */
        } finally {
            clearTimeout(timer);
            host.dataset.youtubeEnriched = '1';
        }
    }

    function boot() {
        const cards = document.querySelectorAll(
            '.site-youtube-card[data-youtube-id], .youtube-card-container[data-youtube-id]');
        if (cards.length) intersectOnce(cards, enrichYouTubeCard);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

function formatNumber(num) {
    if (num >= 1000) return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    return num;
}

(function (C, A, L) {
    let p = function (a, ar) { a.q.push(ar); };
    let d = C.document;
    C.Cal = C.Cal || function () {
        let cal = C.Cal;
        let ar = arguments;
        if (!cal.loaded) {
            cal.ns = {};
            cal.q = cal.q || [];
            d.head.appendChild(d.createElement('script')).src = A;
            cal.loaded = true;
        }
        if (ar[0] === L) {
            const api = function () { p(api, arguments); };
            const namespace = ar[1];
            api.q = api.q || [];
            if (typeof namespace === 'string') {
                cal.ns[namespace] = cal.ns[namespace] || api;
                p(cal.ns[namespace], ar);
                p(cal, ['initNamespace', namespace]);
            } else p(cal, ar);
            return;
        }
        p(cal, ar);
    };
})(window, 'https://app.cal.com/embed/embed.js', 'init');

Cal('init', 'quick-chat', { origin: 'https://app.cal.com' });
Cal.ns['quick-chat']('ui', { hideEventTypeDetails: false, layout: 'month_view' });

(function () {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );
    document.querySelectorAll('.marker, .pencil').forEach((el) => {
        observer.observe(el);
    });
})();

(function () {
    const root = document.documentElement;
    const assigned = new Set();
    let delay = 0;
    function assign(el) {
        if (!el || assigned.has(el)) return;
        assigned.add(el);
        el.classList.add('page-reveal-item');
        el.style.setProperty('--km-reveal-delay', delay + 'ms');
        delay += REVEAL_STEP_MS;
    }
    function setupReveal() {
        assign(document.querySelector('.site-header'));
        assign(document.querySelector('.site-breadcrumbs'));
        const content = document.getElementById('content');
        const topSection = content && content.querySelector(':scope > section');
        if (topSection) {
            const h1 = topSection.querySelector(':scope > h1');
            const lead = topSection.querySelector(':scope > .lead');
            const author = topSection.querySelector(':scope > .site-article');
            assign(h1);
            assign(lead);
            assign(author);
            for (const child of topSection.children) {
                if (child.tagName !== 'SECTION') assign(child);
            }
            for (const section of topSection.querySelectorAll(':scope > section')) {
                assign(section);
            }
        } else if (content) {
            assign(content);
        }
        assign(document.querySelector('.site-feedback-shell'));
        assign(document.querySelector('.site-pagination'));
        assign(document.querySelector('.site-footer'));
    }
    function triggerReveal() {
        requestAnimationFrame(() => {
            root.classList.remove('no-transitions');
            root.classList.add('page-loaded');
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupReveal, { once: true });
    } else {
        setupReveal();
    }
    if (document.readyState === 'complete') {
        triggerReveal();
    } else {
        window.addEventListener('load', triggerReveal, { once: true });
    }
    window.addEventListener('pageshow', (e) => {
        if (e.persisted) root.classList.add('page-loaded');
    });
})();

(function () {
    function initArticleBackground() {
        const aside = document.querySelector('.site-article[data-background]');
        if (!aside) return;
        const urls = aside.getAttribute('data-background').trim().split(/\s+/).filter(Boolean);
        if (!urls.length) return;
        const main = document.querySelector('.site-layout__content');
        if (!main) return;
        main.style.isolation = 'isolate';
        const mainRect = main.getBoundingClientRect();
        const meta = aside.querySelector('.site-article__meta');
        const metaBottom = (meta || aside).getBoundingClientRect().bottom;
        const fs = parseFloat(getComputedStyle(document.documentElement).fontSize);
        const borderY = metaBottom - fs * 2;
        if (urls.length > 1) {
            for (let i = urls.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [urls[i], urls[j]] = [urls[j], urls[i]];
            }
        }
        const overlay = document.createElement('div');
        overlay.className = 'site-article__bg';
        overlay.setAttribute('aria-hidden', 'true');
        overlay.style.top = '0';
        overlay.style.height = `${borderY - mainRect.top}px`;
        overlay.style.backgroundImage = `url("${urls[0]}")`;
        main.appendChild(overlay);
        if (urls.length > 1) {
            let idx = 0;
            setInterval(() => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    idx = (idx + 1) % urls.length;
                    overlay.style.backgroundImage = `url("${urls[idx]}")`;
                    overlay.style.opacity = '';
                }, 800);
            }, 6000);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initArticleBackground, { once: true });
    } else {
        initArticleBackground();
    }
})();
