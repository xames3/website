(() => {
    'use strict';

    const SCROLL_QUIET_FRAMES = 3;
    const SCROLL_PATIENCE_MS = 3000;
    const GLIDE_STOPS = ['wheel', 'touchstart', 'pointerdown', 'keydown'];
    const GLIDE_KEYS = new Set(['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' ']);
    const HASH_SETTLE_MS = 2600;
    const CLAMP_SLACK_PX = 48;
    const CLAMP_SETTLE_MS = 60;
    const CLAMP_MIN_PX = 320;
    const PIXELATE_RATIO = 20;
    const DROPDOWN_OPEN_DELAY_MS = 40;
    const DROPDOWN_CLOSE_DELAY_MS = 140;
    const DROPDOWN_PX_FACTOR = 0.9;
    const FETCH_TIMEOUT_MS = 8000;
    const ARTICLE_BG_INTERVAL_MS = 7000;
    const TICKER_RADIX = 10;
    const TICKER_MAX_LAPS = 4;
    const TICKER_EASING = 'cubic-bezier(0.25, 1, 0.5, 1)';
    const TICKER_BLUR = 'blur(1.5px)';
    const TICKER_BLUR_AT = 0.4;
    const FOCUSABLE = 'a[href], button, input, select, textarea, summary, iframe, [tabindex]';
    const SIDEBAR_WIDE_PX = 768;
    const SCROLLTOP_AFTER_PX = 200;
    const REVEAL_STEPS = 6;
    const REVEAL_SLACK_MS = 8;
    const REVEAL_WAITING = 'km-page-reveal-item';
    const REVEAL_SHOWN = 'km-page-reveal-item--shown';
    const COLOUR_MODE_KEY = 'km:colourMode';
    const WALKTHROUGH_MIN_LINES = 6;
    const WALKTHROUGH_JITTER = 120;
    const WALKTHROUGH_SETTLE = 120;
    const WALKTHROUGH_WIDE = 880;
    const WALKTHROUGH_PAD = 16;
    const WALKTHROUGH_SHARE = 0.6;
    const WALKTHROUGH_ROOM = 24;
    const WALKTHROUGH_ARM = 120;
    const WALKTHROUGH_HOLD = 350;
    const WALKTHROUGH_INPUT = 500;
    const WALKTHROUGH_GLIDE = 1500;
    const WALKTHROUGH_FOCUS = 300;
    const WALKTHROUGH_STACK_LINES = 12;
    const walkthroughs = [];
    let walkthroughHeld = null;
    let walkthroughHand = 0;
    let walkthroughWired = false;

    window.Kaamiki = Object.freeze({ walkthroughs });

    const root = document.documentElement;
    const STRINGS = JSON.parse(root.dataset.kmStrings);

    function say(key, values = {}) {
        return STRINGS[key].replace(/\{(\w+)\}/g, (match, name) => (name in values ? values[name] : match));
    }

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

    const TIMING = {
        dropdownMin: () => getDurationMs('--km-duration-dropdown-min'),
        dropdownMax: () => getDurationMs('--km-duration-dropdown-max'),
        revealStep: () => getDurationMs('--km-reveal-step'),
        tooltipHold: () => getDurationMs('--km-tooltip-hold'),
        fast: () => getDurationMs('--km-duration-fast'),
        showMoreHold: () => getDurationMs('--km-show-more-hold'),
        tickerBase: () => getDurationMs('--km-ticker-base'),
        tickerStep: () => getDurationMs('--km-ticker-step'),
    };

    function toPx(value) {
        const number = parseFloat(value);
        return value.endsWith('rem') ? number * parseFloat(getComputedStyle(root).fontSize) : number;
    }

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

    function syncThemeColor() {
        const meta = document.querySelector('meta[name="theme-color"]');
        const background = document.body && getComputedStyle(document.body).backgroundColor;
        if (meta && background) meta.setAttribute('content', background);
    }

    let shownTheme = root.dataset.kmTheme || 'dark';

    function applyTheme(mode) {
        shownTheme = mode;
        const commit = () => {
            root.setAttribute('data-km-theme', mode);
            root.classList.toggle('km-dark', mode === 'dark');
            syncThemeColor();
        };

        if (prefersReducedMotion() || typeof document.startViewTransition !== 'function') {
            commit();
            return;
        }

        root.classList.add('km-theme-switching');
        const transition = document.startViewTransition(commit);
        transition.finished
            .catch(() => { /* superseded by a newer switch */ })
            .finally(() => root.classList.remove('km-theme-switching'));
    }

    function initPrintColours() {
        let before = null;
        window.addEventListener('beforeprint', () => {
            before = root.getAttribute('data-km-theme');
            root.classList.add('km-no-transitions');
            root.setAttribute('data-km-theme', 'light');
            root.classList.remove('km-dark');
        });
        window.addEventListener('afterprint', () => {
            if (before === null) return;
            root.setAttribute('data-km-theme', before);
            root.classList.toggle('km-dark', before === 'dark');
            root.classList.remove('km-no-transitions');
            before = null;
        });
    }

    function initSystemColours() {
        if (root.dataset.kmColourMode !== 'system') return;
        let chosen = null;
        if (root.hasAttribute('data-km-colour-toggle')) {
            try {
                chosen = localStorage.getItem(COLOUR_MODE_KEY);
            } catch { /* storage unavailable */ }
        }
        if (chosen) return;
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (event) => {
            applyTheme(event.matches ? 'light' : 'dark');
        });
    }

    function initThemeToggle() {
        document.querySelectorAll('.km-footer__theme-toggle').forEach((button) => {
            button.addEventListener('click', () => {
                const mode = shownTheme === 'light' ? 'dark' : 'light';
                try { localStorage.setItem(COLOUR_MODE_KEY, mode); } catch { /* storage unavailable */ }
                applyTheme(mode);
            });
        });
    }

    function initKeyboardModality() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Tab' || event.key?.startsWith('Arrow')) root.setAttribute('data-km-keyboard', '');
        }, true);
        document.addEventListener('pointerdown', () => root.removeAttribute('data-km-keyboard'), true);
    }

    function initSidebar() {
        const sidebar = document.getElementById('km-sidebar');
        const toggle = document.querySelector('.km-header__menu-toggle');
        const backdrop = document.querySelector('.km-sidebar__backdrop');
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
            document.body.classList.toggle('km-body--locked', next);
            sidebar.classList.toggle('km-sidebar--visible', next);
            toggle.setAttribute('aria-expanded', String(next));
            if (backdrop) backdrop.hidden = !next;
            if (next && keyed) requestAnimationFrame(() => enter());
            else if (!next && restore && inside) toggle.focus({ preventScroll: true });
        };
        toggle.addEventListener('click', (event) => show(!open, true, event.detail === 0));
        backdrop?.addEventListener('click', () => show(false));
        sidebar.addEventListener('click', (event) => {
            const link = event.target.closest?.('a[href^="#"]');
            if (!open || !link || isModifiedClick(event)) return;
            show(false);
            if (link.getAttribute('href') !== '#') return;
            event.preventDefault();
            glideTo(0);
        });
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
        const button = document.getElementById('km-scrolltop');
        if (!button) return;
        let last = 0;
        button.addEventListener('click', () => glideTo(0));
        window.addEventListener('scroll', () => {
            const y = window.scrollY;
            const bottom = y + window.innerHeight >= root.scrollHeight - SCROLLTOP_AFTER_PX;
            button.classList.toggle(
                'km-scrolltop--hidden',
                !(y > last && (y > SCROLLTOP_AFTER_PX || bottom)),
            );
            last = Math.max(0, y);
        }, { passive: true });
    }

    function viewportHeight() {
        return window.visualViewport?.height || window.innerHeight;
    }

    function showMoreDock() {
        return toPx(getCssVar('--km-show-more-dock'));
    }

    function keepInView(content, collapsed, tail) {
        const top = window.scrollY + content.getBoundingClientRect().top;
        const targetY = Math.max(0, top + collapsed + tail - viewportHeight());
        const distance = window.scrollY - targetY;
        if (distance <= 0) return Promise.resolve();
        return glideTo(targetY);
    }

    function foldMotion(host, content, clamped, clamping, settled) {
        let timer = 0;
        const settle = (next) => {
            window.clearTimeout(timer);
            host.classList.remove(clamping);
            settled(!next);
            content.style.maxHeight = '';
        };
        const clamp = (next, from, to) => {
            host.classList.toggle(clamped, !next);
            host.classList.add(clamping);
            content.style.maxHeight = `${from}px`;
            void content.offsetHeight;
            content.style.maxHeight = `${to}px`;
            window.clearTimeout(timer);
            timer = window.setTimeout(
                () => settle(next),
                getDurationMs('--km-duration-clamp') + CLAMP_SETTLE_MS,
            );
        };
        const stop = () => window.clearTimeout(timer);
        return { settle, clamp, stop };
    }

    function idleShell(shell, button, name, awake) {
        let timer = 0;
        let stirred = 0;

        const riding = () => shell.getBoundingClientRect().bottom > viewportHeight() - showMoreDock() - 1;

        const rest = () => {
            window.clearTimeout(timer);
            timer = 0;
            shell.classList.remove(name);
        };

        const idle = () => {
            timer = 0;
            if (!awake()) return;
            const hold = TIMING.showMoreHold();
            const quiet = performance.now() - stirred;
            if (quiet < hold) {
                timer = window.setTimeout(idle, hold - quiet);
                return;
            }
            if (button.matches(':hover, :focus-visible')) {
                timer = window.setTimeout(idle, hold);
                return;
            }
            if (riding()) shell.classList.add(name);
        };

        const stir = () => {
            if (!awake()) return;
            stirred = performance.now();
            shell.classList.remove(name);
            if (!timer) timer = window.setTimeout(idle, TIMING.showMoreHold());
        };

        for (const type of [
            'pointermove', 'pointerdown', 'keydown', 'touchstart', 'focusin',
        ]) {
            window.addEventListener(type, stir, { passive: true });
        }
        onScroll(stir);
        return { stir, rest };
    }

    function initShowMore() {
        const page = document.querySelector('.km-page--clamped');
        if (!page) return;
        const content = page.querySelector('.km-page__content');
        const shell = page.querySelector('[data-km-show-more]');
        const button = shell?.querySelector('.km-page__more-button');
        const label = button?.querySelector('.km-page__more-label');
        if (!content || !shell || !button) return;
        if (getComputedStyle(shell).display === 'none') {
            page.classList.remove('km-page--clamped');
            return;
        }

        let expanded = false;

        const tail = () => button.getBoundingClientRect().height + showMoreDock();

        const fit = () => {
            const top = window.scrollY + content.getBoundingClientRect().top;
            const room = Math.max(CLAMP_MIN_PX, viewportHeight() - top - tail());
            page.style.setProperty('--km-show-more-clamp', `${Math.round(room)}px`);
        };

        let folded = true;
        const fold = (next) => {
            page.classList.toggle('km-page--clamped', next);
            if (next === folded) return;
            folded = next;
            document.dispatchEvent(new Event('km:fold'));
        };

        const motion = foldMotion(page, content, 'km-page--clamped', 'km-page--clamping', fold);

        const measure = () => {
            content.style.maxHeight = '';
            page.classList.add('km-page--clamped');
            const collapsed = content.getBoundingClientRect().height;
            page.classList.remove('km-page--clamped');
            const full = content.getBoundingClientRect().height;
            return { collapsed, full };
        };

        fit();
        const { collapsed: first, full: whole } = measure();
        motion.settle(false);
        if (whole - first < CLAMP_SLACK_PX) {
            page.classList.remove('km-page--clamped');
            shell.remove();
            return;
        }

        const { stir, rest } = idleShell(shell, button, 'km-page__more--idle', () => expanded);
        let turn = 0;

        const toggle = (next, animate = true) => {
            if (next === expanded) return;
            expanded = next;
            try { history.replaceState({ ...history.state, kmExpanded: next }, ''); } catch { /* noop */ }
            button.setAttribute('aria-expanded', next ? 'true' : 'false');
            if (label) {
                label.textContent = next
                    ? button.dataset.kmLabelLess
                    : button.dataset.kmLabelMore;
            }
            if (next) stir();
            else rest();

            const start = content.getBoundingClientRect().height;
            const current = ++turn;
            motion.stop();
            if (next) {
                const { full } = measure();
                if (!animate || prefersReducedMotion()) {
                    motion.settle(true);
                    return;
                }
                const room = viewportHeight() - content.getBoundingClientRect().top;
                motion.clamp(true, start, Math.min(full, Math.max(start, room, viewportHeight())));
                return;
            }
            const room = page.style.getPropertyValue('--km-show-more-clamp');
            const collapsed = Math.min(start, toPx(room));
            if (!animate || prefersReducedMotion()) {
                keepInView(content, collapsed, tail());
                motion.settle(false);
                return;
            }
            keepInView(content, collapsed, tail()).then(() => {
                if (current !== turn) return;
                const shown = viewportHeight() - content.getBoundingClientRect().top;
                motion.clamp(false, Math.min(start, Math.max(collapsed, shown)), collapsed);
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

        window.addEventListener('resize', rafThrottle(fit), { passive: true });
        new ResizeObserver(rafThrottle(fit)).observe(document.body);
        document.fonts.ready.then(fit);

        if (holds(location.hash) || history.state?.kmExpanded) toggle(true, false);
    }

    function initHeaderSearch() {
        const search = document.querySelector('.km-header__search .km-search');
        if (!search) return;
        const input = search.querySelector('.km-search__input');
        const submit = search.querySelector('.km-search__submit');

        const open = () => {
            search.classList.add('km-is-open');
            if (!input) return;
            input.focus({ preventScroll: true });
        };
        const close = () => {
            if (input && input.value.trim()) return;
            search.classList.remove('km-is-open');
        };

        submit?.addEventListener('click', (event) => {
            if (search.classList.contains('km-is-open')) return;
            event.preventDefault();
            open();
        });

        input?.addEventListener('focus', () => search.classList.add('km-is-open'));
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

    function scrollSettled(endY) {
        const began = performance.now();
        let last = window.scrollY;
        let moved = false;
        let quiet = 0;
        return new Promise((resolve) => {
            const look = (now) => {
                const y = window.scrollY;
                moved = moved || y !== last;
                quiet = y === last ? quiet + 1 : 0;
                last = y;
                if (Math.abs(y - endY) < 1 || (moved && quiet >= SCROLL_QUIET_FRAMES)
                    || now - began > SCROLL_PATIENCE_MS) {
                    resolve();
                    return;
                }
                requestAnimationFrame(look);
            };
            requestAnimationFrame(look);
        });
    }

    function glideTo(targetY) {
        const endY = clamp(targetY, 0, Math.max(0, root.scrollHeight - window.innerHeight));
        if (Math.abs(endY - window.scrollY) < 1) return Promise.resolve(true);
        if (prefersReducedMotion()) {
            window.scrollTo(0, endY);
            return Promise.resolve(true);
        }
        let stopped = false;
        const stop = (event) => {
            if (event.type === 'keydown' && !GLIDE_KEYS.has(event.key)) return;
            if (event.type === 'wheel' && !event.deltaX && !event.deltaY) return;
            release();
            stopped = true;
            const previousBehavior = root.style.scrollBehavior;
            root.style.scrollBehavior = 'auto';
            window.scrollTo(0, window.scrollY);
            root.style.scrollBehavior = previousBehavior || '';
        };
        const release = () => {
            GLIDE_STOPS.forEach((type) => window.removeEventListener(type, stop, true));
        };
        GLIDE_STOPS.forEach((type) => window.addEventListener(type, stop, { capture: true, passive: true }));
        window.scrollTo({ top: endY, behavior: 'smooth' });
        return scrollSettled(endY).then(() => {
            release();
            return !stopped;
        });
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

    function scrollToElement(element) {
        return glideTo(anchorTargetY(element));
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
            try { history.pushState(history.state, '', `#${id}`); } catch { /* noop */ }
            scrollToElement(target).then((arrived) => {
                if (arrived && !target.contains(link)) focusTarget(target);
            });
        });

        if (!revisited()) settleHash();
    }

    function revisited() {
        const [entry] = performance.getEntriesByType('navigation');
        return entry?.type === 'reload' || entry?.type === 'back_forward';
    }

    function focusTarget(element) {
        if (!element.matches(FOCUSABLE)) element.setAttribute('tabindex', '-1');
        element.focus({ preventScroll: true });
    }

    function reachFocus(target) {
        const began = performance.now();
        let last = window.scrollY;
        let quiet = 0;
        const look = (now) => {
            if (document.activeElement !== target) return;
            quiet = window.scrollY === last ? quiet + 1 : 0;
            last = window.scrollY;
            if (quiet < SCROLL_QUIET_FRAMES) {
                if (now - began < SCROLL_PATIENCE_MS) requestAnimationFrame(look);
                return;
            }
            const top = headerHeight();
            const rect = target.getBoundingClientRect();
            const fits = rect.height <= window.innerHeight - top;
            const seen = fits
                ? rect.top >= top - 1 && rect.bottom <= window.innerHeight + 1
                : rect.top < window.innerHeight && rect.bottom > top;
            if (!seen) glideTo(layoutTop(target) - top);
        };
        requestAnimationFrame(look);
    }

    function initFocusInView() {
        document.addEventListener('focusin', (event) => {
            if (!root.hasAttribute('data-km-keyboard')) return;
            if (event.target.closest?.('.km-header, #km-sidebar')) return;
            reachFocus(event.target);
        });
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

    const tooltipTimers = new WeakMap();

    function flashTooltip(link, message, transient = false) {
        window.clearTimeout(tooltipTimers.get(link));
        link.setAttribute('data-tooltip', message);
        void link.offsetWidth;
        link.classList.add('km-show-tooltip');
        tooltipTimers.set(link, window.setTimeout(() => {
            link.classList.remove('km-show-tooltip');
            if (!transient) return;
            tooltipTimers.set(link, window.setTimeout(
                () => link.removeAttribute('data-tooltip'),
                getDurationMs('--km-duration-fast'),
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
        document.querySelectorAll('.km-copy-url').forEach((link) => {
            link.addEventListener('click', async (event) => {
                event.preventDefault();
                event.stopPropagation();
                const copied = await copyText(canonicalUrl());
                flashTooltip(link, copied ? say('copied') : say('failed'));
            });
        });
    }

    function measureHeaderLink(link, x) {
        const frame = link.parentElement.getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(link.parentElement);
        const text = range.getBoundingClientRect();
        link.style.setProperty('--km-headerlink-top', `${text.top - frame.top}px`);
        link.style.setProperty('--km-headerlink-x', `${(x ?? text.left) - frame.left}px`);
        return text;
    }

    function headingLink(event) {
        const heading = event.target.closest('h1, h2, h3, h4, h5, h6');
        const link = heading?.querySelector(':scope > a.headerlink');
        if (!link) return null;
        const other = event.target.closest(FOCUSABLE);
        if (other && other !== heading
            && (heading.contains(other) || !other.matches('[tabindex]'))) return null;
        if (String(window.getSelection())) return null;
        const text = measureHeaderLink(link, event.clientX);
        return event.clientY >= text.top && event.clientY <= text.bottom ? link : null;
    }

    function initHeaderLinks() {
        const copying = root.hasAttribute('data-km-copy-links');
        document.querySelectorAll('a.headerlink').forEach((link) => {
            link.parentElement.classList.add('km-has-headerlink');
        });
        document.addEventListener('focusin', (event) => {
            if (event.target.matches?.('a.headerlink')) measureHeaderLink(event.target);
        });
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a.headerlink');
            if (!link) {
                headingLink(event)?.click();
                return;
            }
            if (event.isTrusted) measureHeaderLink(link, event.detail ? event.clientX : undefined);
            if (!copying) return;
            copyText(canonicalUrl(link.getAttribute('href') || '')).then((copied) => {
                flashTooltip(link, copied ? say('copied') : say('failed'), true);
            });
        });
    }

    function initCopyButtonNames() {
        const cells = document.querySelectorAll('div.highlight > pre').length;
        if (!cells) return;
        const name = () => {
            const buttons = document.querySelectorAll('button.copybtn');
            buttons.forEach((button) => {
                if (button.hasAttribute('aria-label')) return;
                const title = button.querySelector('svg title')?.textContent.trim();
                button.setAttribute('aria-label', title || button.dataset.tooltip || say('copy'));
            });
            return buttons.length >= cells;
        };
        if (name()) return;
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
        document.fonts.ready.then(measure);
        window.addEventListener('resize', soon, { passive: true });
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }

    function initTabSets() {
        const bars = [];
        const panels = new Map();
        document.querySelectorAll('.sd-tab-set').forEach((set) => {
            const tabs = Array.from(set.querySelectorAll(':scope > input'), (input) => {
                const label = input.nextElementSibling;
                return [input, label, label?.nextElementSibling];
            });
            const shaped = ([, label, panel]) => label?.matches('label') && panel?.matches('.sd-tab-content');
            if (!tabs.length || !tabs.every(shaped)) return;
            const bar = document.createElement('div');
            bar.className = 'km-tab-bar';
            set.prepend(bar);
            bars.push(bar);
            tabs.forEach(([input, label, panel]) => {
                bar.append(input, label);
                panels.set(input, panel);
            });
        });
        if (!bars.length) return;

        const mark = () => panels.forEach((panel, input) => {
            panel.classList.toggle('km-is-current', input.checked);
        });
        const place = (bar, slide) => {
            const label = bar.querySelector(':scope > input:checked + label');
            if (!label) return;
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            bar.classList.toggle('km-is-sliding', slide);
            bar.style.setProperty('--km-tab-x', `${box.left - view.left - bar.clientLeft + bar.scrollLeft}px`);
            bar.style.setProperty('--km-tab-y', `${box.top - view.top - bar.clientTop + bar.scrollTop}px`);
            bar.style.setProperty('--km-tab-width', `${box.width}px`);
            bar.style.setProperty('--km-tab-height', `${box.height}px`);
        };
        const settle = () => {
            mark();
            bars.forEach((bar) => place(bar, false));
        };
        const reveal = (label) => {
            const bar = label.parentElement;
            const inset = parseFloat(getComputedStyle(bar).paddingLeft);
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            const start = box.left - view.left - bar.clientLeft - inset;
            const end = box.right - view.left - bar.clientLeft - bar.clientWidth + inset;
            const shift = start < 0 ? start : Math.min(Math.max(end, 0), start);
            if (shift) bar.scrollBy({ left: shift, behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
        };

        settle();
        document.addEventListener('DOMContentLoaded', settle, { once: true });
        const watch = new ResizeObserver((entries) => {
            new Set(entries.map(({ target }) => target.parentElement)).forEach((bar) => place(bar, false));
        });
        bars.forEach((bar) => bar.querySelectorAll(':scope > label').forEach((label) => watch.observe(label)));
        document.addEventListener('change', (event) => {
            if (!panels.has(event.target)) return;
            mark();
            bars.forEach((bar) => place(bar, true));
            reveal(event.target.nextElementSibling);
        });
    }

    function initScrollable() {
        const blocks = Array.from(document.querySelectorAll('.highlight pre, #km-content table'));
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
        document.fonts.ready.then(mark);
        window.addEventListener('resize', soon, { passive: true });
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }

    function initImageZoom() {
        if (prefersReducedMotion()) return;

        const wrap = (image, standalone) => {
            const inner = document.createElement('div');
            inner.className = standalone ? 'km-zoom-inner km-zoom-inner--standalone' : 'km-zoom-inner';
            const scale = document.createElement('div');
            scale.className = 'km-zoom-scale';
            image.parentElement.insertBefore(inner, image);
            inner.appendChild(scale);
            scale.appendChild(image);
        };

        document.querySelectorAll('#km-content figure.km-zoom > img').forEach((image) => wrap(image, false));
        document.querySelectorAll('#km-content img.km-zoom:not(figure img)').forEach((image) => wrap(image, true));
    }

    function initPixelatedBlur() {
        const draw = (image, canvas) => {
            const width = Math.max(1, Math.round(image.naturalWidth / PIXELATE_RATIO));
            const height = Math.max(1, Math.round(image.naturalHeight / PIXELATE_RATIO));
            canvas.width = width;
            canvas.height = height;
            canvas.getContext('2d').drawImage(image, 0, 0, width, height);
            canvas.classList.add('km-is-drawn');
        };

        document.querySelectorAll('#km-content figure.km-pixelated-blur img').forEach((image) => {
            const frame = document.createElement('div');
            frame.className = 'km-pixelated-frame';
            const canvas = document.createElement('canvas');
            canvas.className = 'km-pixelated-canvas';
            canvas.setAttribute('aria-hidden', 'true');
            image.parentElement.insertBefore(frame, image);
            frame.append(image, canvas);

            const paint = () => {
                try {
                    draw(image, canvas);
                } catch (error) {
                    console.error(error);
                }
            };
            if (image.complete && image.naturalWidth) paint();
            else image.addEventListener('load', paint, { once: true });
        });
    }

    function initTouchReveal() {
        if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
        const selector = '#km-content figure.km-zoom, #km-content figure.km-fuzzy-blur, #km-content figure.km-pixelated-blur';
        const figures = document.querySelectorAll(selector);
        if (!figures.length) return;

        document.addEventListener('click', (event) => {
            const figure = event.target.closest(selector);
            if (figure && event.target.closest('a')) return;
            const shouldReveal = figure && !figure.classList.contains('km-is-revealed');
            figures.forEach((node) => node.classList.remove('km-is-revealed'));
            if (shouldReveal) figure.classList.add('km-is-revealed');
        });
    }

    function initHeaderNavDropdowns() {
        const nav = document.querySelector('.km-header__nav-tree');
        if (!nav) return;

        let uid = 0;
        Array.from(nav.querySelectorAll('p.caption')).forEach((caption) => {
            const list = caption.nextElementSibling;
            if (list?.tagName !== 'UL') return;

            const group = document.createElement('div');
            group.className = 'km-header__nav-group';
            caption.parentNode.insertBefore(group, caption);
            group.append(caption, list);

            list.id = list.id || `km-nav-group-${++uid}`;
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
                group.classList.toggle('km-is-open', next);
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
                    set(!group.classList.contains('km-is-open'));
                } else if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    set(true);
                    list.querySelector('a[href]')?.focus();
                }
            });
            group.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape' || !group.classList.contains('km-is-open')) return;
                set(false);
                caption.focus();
            });
        });
    }

    function dropdownFold(details, summary, content, index) {
        const CLAMPED = 'km-dropdown--clamped';
        const CLAMPING = 'km-dropdown--clamping';
        const LONG = 'km-dropdown--long';
        let body = null;
        let shell = null;
        let button = null;
        let label = null;
        let motion = null;
        let idle = null;
        let expanded = false;
        let turn = 0;

        const tail = () => (button ? button.getBoundingClientRect().height : 0);

        const limit = () => {
            const style = getComputedStyle(content);
            const room = viewportHeight() - headerHeight()
                - summary.getBoundingClientRect().height
                - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) - tail();
            return Math.max(CLAMP_MIN_PX, Math.round(room));
        };

        const full = () => {
            if (!body) {
                const style = getComputedStyle(content);
                return content.getBoundingClientRect().height
                    - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom);
            }
            const clamped = details.classList.contains(CLAMPED);
            details.classList.remove(CLAMPED);
            const height = body.getBoundingClientRect().height;
            details.classList.toggle(CLAMPED, clamped);
            return height;
        };

        const name = (next) => {
            button.setAttribute('aria-expanded', String(next));
            label.textContent = next ? say('less') : say('more');
        };

        const toggle = (next, animate = true) => {
            if (next === expanded) return;
            expanded = next;
            name(next);
            if (next) idle.stir();
            else idle.rest();
            const start = body.getBoundingClientRect().height;
            const current = ++turn;
            motion.stop();
            if (next) {
                const height = full();
                if (!animate || prefersReducedMotion()) {
                    motion.settle(true);
                    return;
                }
                const room = viewportHeight() - body.getBoundingClientRect().top;
                motion.clamp(true, start, Math.min(height, Math.max(start, room, viewportHeight())));
                return;
            }
            const collapsed = Math.min(start, limit());
            const keep = () => keepInView(body, collapsed, tail() + showMoreDock());
            if (!animate || prefersReducedMotion()) {
                keep();
                motion.settle(false);
                return;
            }
            keep().then(() => {
                if (current !== turn) return;
                const shown = viewportHeight() - body.getBoundingClientRect().top;
                motion.clamp(false, Math.min(start, Math.max(collapsed, shown)), collapsed);
            });
        };

        const measure = () => {
            if (!details.open) return;
            if (details.classList.contains('km-is-animating') || details.classList.contains(CLAMPING)) return;
            if (full() - limit() < CLAMP_SLACK_PX) {
                if (!body) return;
                expanded = false;
                name(false);
                idle.rest();
                details.classList.remove(LONG, CLAMPED);
                return;
            }
            build();
            details.classList.add(LONG);
            details.style.setProperty('--km-dropdown-clamp', `${limit()}px`);
            if (!expanded) details.classList.add(CLAMPED);
        };

        const soon = rafThrottle(measure);

        const build = () => {
            if (body) return;
            body = document.createElement('div');
            body.className = 'km-dropdown__body';
            body.id = `km-dropdown-body-${index}`;
            body.append(...content.childNodes);
            shell = document.createElement('div');
            shell.className = 'km-dropdown__more';
            button = document.createElement('button');
            button.type = 'button';
            button.className = 'km-dropdown__more-button';
            button.setAttribute('aria-controls', body.id);
            label = document.createElement('span');
            label.className = 'km-dropdown__more-label';
            const icon = document.createElement('i');
            icon.className = `${root.dataset.kmMoreIcon} km-dropdown__more-icon`;
            icon.setAttribute('aria-hidden', 'true');
            button.append(label, icon);
            shell.append(button);
            content.append(body, shell);
            name(false);
            motion = foldMotion(details, body, CLAMPED, CLAMPING, (next) => {
                details.classList.toggle(CLAMPED, next);
            });
            idle = idleShell(shell, button, 'km-dropdown__more--idle', () => expanded && details.open);
            button.addEventListener('click', () => toggle(!expanded));
            body.addEventListener('focusin', (event) => {
                if (expanded || !details.classList.contains(CLAMPED)) return;
                if (event.target.getBoundingClientRect().bottom > shell.getBoundingClientRect().top) {
                    toggle(true, false);
                }
            });
            const watch = new ResizeObserver(soon);
            Array.from(body.children).forEach((child) => watch.observe(child));
        };

        const reset = () => {
            if (!body || !expanded) return;
            expanded = false;
            name(false);
            idle.rest();
            motion.settle(false);
        };

        window.addEventListener('resize', soon, { passive: true });
        new ResizeObserver(soon).observe(content);
        document.fonts.ready.then(soon);
        return { measure, reset };
    }

    function initDropdowns() {
        const easing = getCssVar('--km-ease-smooth');

        document.querySelectorAll('details.sd-dropdown').forEach((details, index) => {
            const summary = details.querySelector(':scope > summary');
            const content = details.querySelector(':scope > .sd-summary-content');
            if (!summary || !content) return;
            const fold = dropdownFold(details, summary, content, index);

            let animation = null;
            let wanted = details.open;

            const finish = (opening) => {
                details.classList.remove('km-is-animating', 'km-is-closing');
                if (opening) {
                    fold.measure();
                    return;
                }
                details.open = false;
                fold.reset();
            };

            const frame = (state) => ({
                height: `${state.height}px`,
                paddingTop: `${state.top}px`,
                paddingBottom: `${state.bottom}px`,
                opacity: state.opacity,
            });

            summary.addEventListener('click', (event) => {
                if (isModifiedClick(event)) return;
                event.preventDefault();

                const opening = animation ? !wanted : !details.open;
                wanted = opening;
                const moving = getComputedStyle(content);
                const from = animation ? {
                    height: content.getBoundingClientRect().height,
                    top: parseFloat(moving.paddingTop),
                    bottom: parseFloat(moving.paddingBottom),
                    opacity: Number(moving.opacity),
                } : null;
                animation?.cancel();
                animation = null;
                details.classList.toggle('km-is-closing', !opening);
                if (opening && !details.open) {
                    details.open = true;
                    fold.measure();
                }
                if (prefersReducedMotion()) {
                    finish(opening);
                    return;
                }

                details.classList.add('km-is-animating');
                const style = getComputedStyle(content);
                const top = parseFloat(style.paddingTop);
                const bottom = parseFloat(style.paddingBottom);
                const box = content.getBoundingClientRect();
                const room = Math.max(0, viewportHeight() - box.top);
                const start = from || (opening
                    ? { height: 0, top: 0, bottom: 0, opacity: 0 }
                    : { height: box.height, top, bottom, opacity: 1 });
                if (!opening) start.height = Math.min(start.height, room);
                const end = opening
                    ? { height: Math.min(box.height, Math.max(room, viewportHeight(), start.height)), top, bottom, opacity: 1 }
                    : { height: 0, top: 0, bottom: 0, opacity: 0 };
                const duration = Math.min(TIMING.dropdownMax(), Math.max(
                    TIMING.dropdownMin(),
                    Math.abs(end.height - start.height) * DROPDOWN_PX_FACTOR,
                ));

                const current = content.animate([frame(start), frame(end)], {
                    duration, easing, fill: 'both',
                });
                animation = current;
                current.finished.then(() => {
                    current.cancel();
                    animation = null;
                    finish(opening);
                }).catch(() => { /* superseded by a newer toggle */ });
            });

            if (details.open) fold.measure();
        });
    }

    function enrichYouTubeCard(card) {
        const id = card.getAttribute('data-km-youtube-id');
        if (!id) return;
        const title = card.hasAttribute('data-km-youtube-title')
            ? null
            : card.querySelector('.km-youtube-card__title');
        const channel = card.hasAttribute('data-km-youtube-channel')
            ? null
            : card.querySelector('.km-youtube-card__channel');
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
            document.querySelectorAll('.km-youtube-card[data-km-youtube-id]'),
            enrichYouTubeCard,
        );
    }

    function initYouTubeFacades() {
        document.querySelectorAll('[data-km-facade]').forEach((facade) => {
            facade.addEventListener('click', (event) => {
                if (event.button !== 0 || event.metaKey || event.ctrlKey
                    || event.shiftKey || event.altKey) return;
                event.preventDefault();
                const url = new URL(facade.getAttribute('data-km-facade-src'), window.location.href);
                url.searchParams.set('autoplay', '1');
                const frame = document.createElement('iframe');
                frame.className = 'km-media__iframe';
                frame.src = url.href;
                frame.title = facade.getAttribute('data-km-facade-title') || '';
                frame.allow = facade.getAttribute('data-km-facade-allow') || '';
                frame.referrerPolicy = facade.getAttribute('data-km-facade-referrer') || '';
                frame.allowFullscreen = true;
                facade.replaceWith(frame);
                frame.focus();
            });
        });
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
        column.className = 'km-github-repository__digit';
        const reel = document.createElement('span');
        reel.className = 'km-github-repository__reel';
        for (let i = 0; i <= stops; i += 1) {
            const cell = document.createElement('span');
            cell.className = 'km-github-repository__cell';
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
        ticker.className = 'km-github-repository__ticker';
        const columns = [];

        for (const character of value) {
            if (character < '0' || character > '9') {
                const symbol = document.createElement('span');
                symbol.className = 'km-github-repository__symbol';
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
            if (reduced) {
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
        const project = widget.getAttribute('data-km-repository');
        const fields = widget.querySelectorAll('[data-km-repository-count]');
        if (!project || !fields.length) return;

        const data = await fetchJson(`https://api.github.com/repos/${project}`) || {};
        fields.forEach((field) => {
            const raw = Number(data[field.getAttribute('data-km-repository-count')]);
            const count = Number.isFinite(raw) ? Math.max(0, Math.trunc(raw)) : 0;
            renderTicker(field, formatCount(count));
        });
    }

    function initRepositoryWidgets() {
        onVisible(
            document.querySelectorAll('.km-github-repository[data-km-repository]'),
            loadRepository,
            { rootMargin: '0px 0px -10% 0px' },
        );
    }

    function initInkReveal() {
        onVisible(
            document.querySelectorAll('.km-sharpie, .km-pencil'),
            (element) => element.classList.add('km-is-visible'),
            { threshold: 0.1 },
        );
    }

    function revealBlocks(node) {
        return Array.from(node?.children ?? []).flatMap((child) => (
            child.tagName === 'SECTION' ? revealBlocks(child) : [child]
        ));
    }

    function initPageReveal() {
        if (prefersReducedMotion()) return;
        const blocks = [
            document.querySelector('.km-header'),
            document.querySelector('.km-breadcrumbs'),
            ...revealBlocks(document.getElementById('km-content')),
            document.querySelector('.km-feedback-shell'),
            document.querySelector('.km-layout__meta'),
            document.querySelector('.km-page__more-button'),
            document.querySelector('.km-pagination'),
            document.querySelector('.km-footer'),
        ].filter(Boolean);

        const limit = TIMING.revealStep() * REVEAL_STEPS;
        const duration = getDurationMs('--km-reveal-duration');
        const nudges = ['wheel', 'touchmove', 'keydown', 'pointerdown', 'scroll'];
        const hurried = new Set();
        const anchor = window.scrollY;
        let waiting = blocks;
        let step = TIMING.revealStep();
        let began = null;
        let last = -Infinity;
        let busy = 0;
        let screen = 0;
        let done = false;

        const release = (block, animate) => {
            if (animate) block.classList.add(REVEAL_SHOWN);
            else block.classList.remove(REVEAL_WAITING);
            block.dispatchEvent(new Event('km:reveal'));
        };

        const finish = () => {
            if (done) return;
            done = true;
            nudges.forEach((type) => window.removeEventListener(type, nudge));
            waiting.forEach((block) => release(block, false));
            waiting = [];
            blocks.forEach((block) => block.classList.remove(REVEAL_WAITING, REVEAL_SHOWN));
            hurried.forEach((block) => {
                block.style.removeProperty('animation-duration');
                if (!block.getAttribute('style')) block.removeAttribute('style');
            });
        };

        const nudge = (event) => {
            if (event.type !== 'scroll' || window.scrollY !== anchor) finish();
        };

        const play = (block, now, late) => {
            if (late) {
                block.style.animationDuration = `${Math.round(busy - now)}ms`;
                hurried.add(block);
            } else {
                busy = now + duration;
            }
            release(block, true);
        };

        const edges = (fold) => {
            const known = new Map();
            const clip = (node) => {
                if (!node || node === document.body) return [0, fold];
                if (!known.has(node)) {
                    let [top, bottom] = clip(node.parentElement);
                    if (getComputedStyle(node).overflowY !== 'visible') {
                        const box = node.getBoundingClientRect();
                        top = Math.max(top, box.top);
                        bottom = Math.min(bottom, box.bottom);
                    }
                    known.set(node, [top, bottom]);
                }
                return known.get(node);
            };
            return clip;
        };

        const inView = (block, clip) => {
            const box = block.getBoundingClientRect();
            const [top, bottom] = clip(block.parentElement);
            return (box.width > 0 || box.height > 0) && box.bottom >= top && box.top < bottom;
        };

        const tick = (now) => {
            if (done) return;
            try {
                if (root.classList.contains('km-page-loading')) {
                    requestAnimationFrame(tick);
                    return;
                }
                if (began === null) {
                    began = now;
                    screen = walkthroughScreen();
                }
                const late = now - began >= limit + duration;
                if (late && now >= busy) {
                    finish();
                    return;
                }
                const fold = Math.max(window.innerHeight, screen);
                const clip = edges(fold);
                const ready = waiting.filter((block) => inView(block, clip));
                step = Math.min(step, limit / Math.max(1, ready.length - 1));
                const next = last + step;
                if (ready.length && (late || now >= next - REVEAL_SLACK_MS)) {
                    const block = ready[0];
                    const at = waiting.indexOf(block);
                    waiting.slice(0, at).forEach((passed) => {
                        const box = passed.getBoundingClientRect();
                        if (box.bottom > 0 && box.top < 2 * fold) play(passed, now, late);
                        else release(passed, false);
                    });
                    waiting = waiting.slice(at + 1);
                    play(block, now, late);
                    last = now - next > step ? now : next;
                } else if (!ready.length && now >= busy) {
                    finish();
                    return;
                }
                requestAnimationFrame(tick);
            } catch (error) {
                finish();
                console.error(error);
            }
        };
        blocks.forEach((block) => block.classList.add(REVEAL_WAITING));
        nudges.forEach((type) => window.addEventListener(type, nudge, { passive: true }));
        requestAnimationFrame(tick);
    }

    function initArticleBackground() {
        const article = document.querySelector('.km-article[data-km-background]');
        const main = document.querySelector('.km-layout__content');
        if (!article || !main) return;

        const urls = article.getAttribute('data-km-background').trim().split(/\s+/).filter(Boolean);
        if (!urls.length) return;

        for (let i = urls.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [urls[i], urls[j]] = [urls[j], urls[i]];
        }

        main.style.isolation = 'isolate';
        const overlay = document.createElement('div');
        overlay.className = 'km-article__bg';
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
            const anchor = article.querySelector('.km-article__meta') || article;
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
        new ResizeObserver(measure).observe(main);
        document.fonts.ready.then(measure);
        article.addEventListener('animationend', measure);

        if (urls.length === 1 || prefersReducedMotion()) return;
        const every = Number(article.getAttribute('data-km-interval')) || ARTICLE_BG_INTERVAL_MS;
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
            }, getDurationMs('--km-duration-slow') + 50);
        }, every);
    }

    function clamp(value, low, high) {
        return Math.max(low, Math.min(high, value));
    }

    function readWalkthroughPayload(host) {
        return JSON.parse(host.querySelector('[data-km-payload]').textContent);
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
        value.dataset.kmKey = item.key;
        value.setAttribute('data-km-long', '');
        value.setAttribute('role', 'button');
        value.tabIndex = 0;
        const open = opened.has(item.key);
        if (open) value.setAttribute('data-km-open', '');
        value.setAttribute('aria-expanded', String(open));
        value.append(short, full);
        return value;
    }

    function walkthroughEntry(item, opened) {
        const entry = document.createElement('span');
        entry.className = 'km-walkthrough__var';
        if (item.fresh) entry.setAttribute('data-km-fresh', '');
        if (item.kind) entry.dataset.kmKind = item.kind;
        entry.append(
            item.name ? `${item.name}: ` : `${item.mark} `,
            walkthroughValue(item, opened),
        );
        return entry;
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

    function walkthroughFrame() {
        walkthroughs.forEach((walk) => walk.update());
    }

    const walkthroughTick = rafThrottle(() => walkthroughFrame());

    function walkthroughMeasure() {
        walkthroughs.forEach((walk) => walk.measure());
        walkthroughFrame();
    }

    function walkthroughRefit() {
        walkthroughs.forEach((walk) => {
            if (walk.shape() !== walk.shaped) walk.measure();
        });
        walkthroughFrame();
    }

    let walkthroughSettling = 0;

    function walkthroughSoon() {
        window.clearTimeout(walkthroughSettling);
        walkthroughSettling = window.setTimeout(walkthroughRefit, WALKTHROUGH_SETTLE);
    }

    function initWalkthroughs() {
        document.querySelectorAll('[data-km-walkthrough]').forEach((host) => {
            walkthroughs.push(createWalkthrough(host));
        });
        if (!walkthroughs.length) return;
        walkthroughMeasure();
        onScroll(walkthroughTick);

        const panes = new ResizeObserver(walkthroughSoon);
        walkthroughs.forEach((walk) => {
            panes.observe(walk.pane);
            panes.observe(walk.track);
        });
        new ResizeObserver(walkthroughSoon).observe(document.body);

        document.addEventListener('km:fold', walkthroughMeasure);

        let width = window.innerWidth;
        let height = window.innerHeight;
        let resizing = 0;
        window.addEventListener('resize', () => {
            window.clearTimeout(resizing);
            resizing = window.setTimeout(() => {
                const moved = Math.abs(window.innerHeight - height);
                if (window.innerWidth === width && moved < WALKTHROUGH_JITTER) {
                    walkthroughHeld?.recentre();
                    return;
                }
                width = window.innerWidth;
                height = window.innerHeight;
                walkthroughMeasure();
            }, WALKTHROUGH_SETTLE);
        }, { passive: true });

        window.matchMedia('(prefers-reduced-motion: reduce)')
            .addEventListener('change', walkthroughMeasure);
        document.fonts.ready.then(walkthroughMeasure);
    }

    function walkthroughFocus() {
        const top = headerHeight();
        return top + (window.innerHeight - top) / 2;
    }

    function walkthroughJump(top) {
        window.scrollTo({ top, behavior: 'instant' });
    }

    function walkthroughConsumes(element, dy) {
        for (let node = element; node instanceof Element && node !== document.body; node = node.parentElement) {
            if (!/auto|scroll/.test(getComputedStyle(node).overflowY)) continue;
            const spare = dy > 0
                ? node.scrollHeight - node.clientHeight - node.scrollTop
                : node.scrollTop;
            if (spare > 1) return true;
        }
        return false;
    }

    function walkthroughView(frame) {
        const stage = frame.querySelector('[data-km-stage]');
        const lines = new Map();
        frame.querySelectorAll('[data-km-line]').forEach((line) => {
            lines.set(Number(line.dataset.kmLine), line);
        });
        return {
            frame,
            stage,
            lines,
            code: stage.querySelector('pre'),
            out: frame.querySelector('[data-km-out]'),
            marked: [],
            filled: [],
            current: null,
        };
    }

    function walkthroughMark(view, step) {
        view.marked.forEach((line) => line.removeAttribute('data-km-current'));
        view.marked = [];
        for (let line = step.line; line <= (step.end ?? step.line); line += 1) {
            const found = view.lines.get(line);
            if (!found) continue;
            found.setAttribute('data-km-current', '');
            view.marked.push(found);
        }
        view.current = view.marked[0] || null;
    }

    function walkthroughAnnotate(view, step, comment, opened) {
        view.filled.forEach((slot) => slot.replaceChildren());
        view.filled = [];
        const groups = new Map();
        const add = (at, item) => {
            if (!view.lines.has(at)) return;
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
        const { open = '#', close = '' } = comment || {};
        groups.forEach((items, at) => {
            const slot = view.lines.get(at).querySelector('[data-km-ann]');
            slot.append(`${open} `);
            items.forEach((item, n) => {
                if (n) slot.append(', ');
                slot.append(walkthroughEntry(item, opened));
            });
            if (close) slot.append(` ${close}`);
            view.filled.push(slot);
        });
    }

    function walkthroughFollow(view, room, shift) {
        const line = view.current;
        if (!line) return shift;
        const rect = line.getBoundingClientRect();
        const top = rect.top - view.code.getBoundingClientRect().top;
        const pad = Math.min(room / 3, rect.height * 2);
        let target = shift;
        if (top < target + pad) target = top - pad;
        else if (top + rect.height > target + room - pad) {
            target = top + rect.height - room + pad;
        }
        return clamp(Math.round(target), 0, Math.max(0, view.code.offsetHeight - room));
    }

    function walkthroughEdge(view, above, below) {
        const { stage } = view;
        stage.toggleAttribute('data-km-more', stage.scrollWidth - stage.clientWidth - stage.scrollLeft > 2);
        stage.toggleAttribute('data-km-above', above > 2);
        stage.toggleAttribute('data-km-below', below > 2);
    }

    function walkthroughWire() {
        if (walkthroughWired) return;
        walkthroughWired = true;
        const steps = { ArrowDown: 60, ArrowUp: -60 };
        const pages = { PageDown: 1, PageUp: -1 };
        const hand = (wait) => {
            walkthroughHand = Math.max(walkthroughHand, performance.now() + wait);
        };
        const taken = (event, dy) => event.target.closest?.('.km-header')
            || walkthroughConsumes(event.target, dy);
        window.addEventListener('wheel', (event) => {
            if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
            hand(WALKTHROUGH_INPUT);
            if (!walkthroughHeld || taken(event, event.deltaY)) return;
            const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? window.innerHeight : 1;
            walkthroughHeld.nudge(event.deltaY * unit);
        }, { passive: true });
        window.addEventListener('keydown', (event) => {
            if (event.altKey || event.ctrlKey || event.metaKey) return;
            if (event.target.closest?.('input, textarea, select, [contenteditable]')) return;
            if (event.key === 'Escape') {
                walkthroughHeld?.release();
                return;
            }
            const space = event.key === ' ' && !event.target.closest?.('button, a, summary, [role="button"]');
            let delta = steps[event.key];
            if (delta === undefined && (event.key in pages || space)) {
                delta = (event.key in pages ? pages[event.key] : event.shiftKey ? -1 : 1) * window.innerHeight * 0.85;
            }
            if (delta === undefined) return;
            hand(WALKTHROUGH_INPUT);
            if (walkthroughHeld) {
                event.preventDefault();
                walkthroughHeld.nudge(delta);
            }
        });
        let touchY = 0;
        window.addEventListener('touchstart', (event) => {
            touchY = event.touches[0].clientY;
            hand(WALKTHROUGH_INPUT);
        }, { passive: true });
        window.addEventListener('touchmove', (event) => {
            hand(WALKTHROUGH_INPUT);
            const y = event.touches[0].clientY;
            const delta = touchY - y;
            touchY = y;
            if (walkthroughHeld && !taken(event, delta)) walkthroughHeld.nudge(delta);
        }, { passive: true });
        ['touchend', 'touchcancel'].forEach((name) => {
            window.addEventListener(name, () => hand(WALKTHROUGH_GLIDE), { passive: true });
        });
    }

    function createWalkthrough(host) {
        const payload = readWalkthroughPayload(host);
        const { steps } = payload;
        const pane = host.querySelector('[data-km-pane]');
        const frame = host.querySelector('[data-km-frame]');
        const box = host.querySelector('[data-km-notes]');
        const track = host.querySelector('[data-km-track]');
        const counter = frame.querySelector('[data-km-counter]');
        const blocks = Array.from(track.querySelectorAll('[data-km-note]'));
        const main = walkthroughView(frame);
        const { stage, code, out } = main;
        host.querySelectorAll('img[loading="lazy"]').forEach((image) => {
            image.loading = 'eager';
        });
        let carry = 0;
        const owned = blocks.map((_, at) => {
            const own = [];
            steps.forEach((step, n) => {
                if (step.note === at) own.push(n);
            });
            if (!own.length) return [carry];
            carry = own[own.length - 1];
            return own;
        });
        const printed = [];
        let text = '';
        steps.forEach((step) => {
            text += step.out || '';
            printed.push(text.length);
        });
        const idle = counter ? counter.textContent : '';

        const opened = new Set();
        const walk = {
            host, pane, track, shaped: '', update, measure, shape, nudge, release, recentre,
        };
        let snaps = [];
        let keys = [];
        let index = -1;
        let active = -1;
        let mode = '';
        let shift = 0;
        let room = 0;
        let height = 0;
        let total = 0;
        let progress = 0;
        let heldAt = 0;
        let heldY = 0;
        let focusedAt = 0;
        let armed = false;
        let unseen = true;
        let lastAway = null;
        let loose = false;
        let touched = false;
        let steady = false;

        function shape() {
            return [
                host.getClientRects().length > 0,
                host.closest('.km-page--clamped') !== null,
                pane.clientWidth,
                code.offsetHeight,
                headerHeight(),
                blocks.map((block) => block.offsetHeight).join(','),
            ].join(' ');
        }

        function annotate(step) {
            const focused = stage.contains(document.activeElement)
                ? document.activeElement.closest('[data-km-long]')?.dataset.kmKey
                : undefined;
            walkthroughAnnotate(main, step, payload.comment, opened);
            if (focused === undefined) return;
            const again = Array.from(stage.querySelectorAll('[data-km-long]'))
                .find((value) => value.dataset.kmKey === focused);
            steady = true;
            (again || stage).focus({ preventScroll: true });
            steady = false;
        }

        function follow() {
            shift = walkthroughFollow(main, room, shift);
            host.style.setProperty('--km-walkthrough-shift', `${shift}px`);
        }

        function edge() {
            const top = loose ? stage.scrollTop : shift;
            const below = loose
                ? stage.scrollHeight - stage.clientHeight - top
                : code.offsetHeight - room - shift;
            walkthroughEdge(main, mode === 'stage' ? top : 0, mode === 'stage' ? below : 0);
        }

        function print(at) {
            if (!out || !text) return;
            const end = printed[at];
            const start = end - (steps[at].out || '').length;
            out.replaceChildren();
            if (start > 0) out.append(text.slice(0, start));
            if (end > start) {
                const fresh = document.createElement('span');
                fresh.setAttribute('data-km-fresh', '');
                fresh.textContent = text.slice(start, end);
                out.append(fresh);
            }
            const before = out.offsetHeight;
            out.style.height = 'auto';
            const after = out.offsetHeight;
            if (Math.abs(after - before) > 0.5) {
                out.style.height = `${before}px`;
                void out.offsetHeight;
            }
            out.style.height = `${after}px`;
            out.scrollTop = out.scrollHeight;
        }

        function loosen() {
            if (loose || mode !== 'stage' || steady || touched) return;
            loose = true;
            stage.setAttribute('data-km-loose', '');
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
            stage.removeAttribute('data-km-loose');
            void code.offsetHeight;
        }

        function ease() {
            if (!loose) return;
            rejoin();
            follow();
            edge();
        }

        function unfold(value) {
            const open = value.toggleAttribute('data-km-open');
            value.setAttribute('aria-expanded', String(open));
            if (open) opened.add(value.dataset.kmKey);
            else opened.delete(value.dataset.kmKey);
            edge();
        }

        function rest() {
            rejoin();
            main.marked.forEach((line) => line.removeAttribute('data-km-current'));
            main.marked = [];
            main.filled.forEach((slot) => slot.replaceChildren());
            main.filled = [];
            main.current = null;
            blocks.forEach((block) => {
                block.removeAttribute('data-km-active');
                block.removeAttribute('aria-current');
            });
            out?.replaceChildren();
            out?.style.removeProperty('height');
            if (counter) counter.textContent = idle;
            ['--km-walkthrough-stage', '--km-walkthrough-notes']
                .forEach((name) => host.style.removeProperty(name));
            host.style.setProperty('--km-walkthrough-shift', '0px');
            track.style.removeProperty('translate');
            keys = [];
            index = -1;
            active = -1;
            shift = 0;
        }

        function mark(at) {
            if (at === active) return;
            blocks[active]?.removeAttribute('data-km-active');
            blocks[active]?.removeAttribute('aria-current');
            active = at;
            blocks[at].setAttribute('data-km-active', '');
            blocks[at].setAttribute('aria-current', 'step');
        }

        function paint(at) {
            const next = clamp(at, 0, steps.length - 1);
            if (next === index) return;
            index = next;
            rejoin();
            const step = steps[index];
            walkthroughMark(main, step);
            annotate(step);
            print(index);
            follow();
            edge();
            if (counter) counter.textContent = `${index + 1} / ${steps.length}`;
        }

        function locate(value) {
            const into = clamp(value, 0, total);
            const found = keys.findIndex((item) => into <= item.to);
            const at = found < 0 ? keys.length - 1 : found;
            const key = keys[at];
            return { at, through: clamp((into - key.from) / Math.max(1, key.to - key.from), 0, 1) };
        }

        function render() {
            if (mode !== 'stage' || !keys.length) return;
            const { at: slot, through } = locate(progress);
            const key = keys[slot];
            track.style.translate = `0 ${-walkthroughSnap(key.a + (key.b - key.a) * through)}px`;
            let note = key.note;
            const own = owned[note];
            let at = own[Math.min(own.length - 1, Math.floor(through * own.length))];
            if (key.kind === 'move' && through >= 0.5) {
                note += 1;
                at = owned[note][0];
            } else if (key.kind === 'move') {
                at = own[own.length - 1];
            }
            mark(note);
            paint(at);
        }

        function centre() {
            return frame.getBoundingClientRect().top + height / 2;
        }

        function recentre() {
            walkthroughJump(window.scrollY + centre() - walkthroughFocus());
            heldY = window.scrollY;
        }

        function lock(side) {
            if (walkthroughHeld) return;
            progress = side > 0 ? 0 : total;
            recentre();
            const bar = window.innerWidth - root.clientWidth;
            root.style.overflow = 'hidden';
            if (bar > 0) root.style.paddingRight = `${bar}px`;
            walkthroughHeld = walk;
            heldAt = performance.now();
            render();
        }

        function release() {
            if (walkthroughHeld !== walk) return;
            walkthroughHeld = null;
            root.style.removeProperty('overflow');
            root.style.removeProperty('padding-right');
            armed = false;
        }

        function nudge(delta) {
            if (performance.now() - heldAt < WALKTHROUGH_HOLD) return;
            if ((delta > 0 && progress >= total) || (delta < 0 && progress <= 0)) {
                release();
                return;
            }
            progress = clamp(progress + delta, 0, total);
            render();
        }

        function update() {
            if (mode !== 'stage') return;
            if (walkthroughHeld === walk) {
                if (Math.abs(window.scrollY - heldY) <= 2) return;
                if (performance.now() - focusedAt < WALKTHROUGH_FOCUS) walkthroughJump(heldY);
                else release();
                return;
            }
            const away = centre() - walkthroughFocus();
            if (unseen || Math.abs(away) > window.innerHeight) {
                unseen = false;
                progress = away > 0 ? 0 : total;
                render();
            }
            if (Math.abs(away) > WALKTHROUGH_ARM) armed = true;
            const byHand = performance.now() < walkthroughHand;
            if (armed && byHand && !walkthroughHeld && lastAway !== null) {
                if (lastAway > 0 && away <= 0) lock(1);
                else if (lastAway < 0 && away >= 0) lock(-1);
            }
            lastAway = away;
        }

        function clearStack() {
            snaps.forEach((view) => view.frame.remove());
            snaps = [];
        }

        function stack() {
            blocks.forEach((block) => {
                const clone = frame.cloneNode(true);
                clone.removeAttribute('data-km-frame');
                clone.classList.add('km-walkthrough__snap');
                block.prepend(clone);
                snaps.push(walkthroughView(clone));
            });
            const [first] = snaps;
            const line = first.lines.get(1)?.getBoundingClientRect().height || 20;
            const whole = first.code.offsetHeight;
            const pad = Math.max(0, whole - line * first.lines.size);
            const most = Math.min(whole, pad + line * WALKTHROUGH_STACK_LINES);
            snaps.forEach((view, at) => {
                const upto = owned[at][owned[at].length - 1];
                const step = steps[upto];
                walkthroughMark(view, step);
                walkthroughAnnotate(view, step, payload.comment, opened);
                if (view.out) {
                    view.out.textContent = text.slice(0, printed[upto]);
                    view.out.hidden = !view.out.textContent;
                }
                view.frame.style.setProperty('--km-walkthrough-stage', `${most}px`);
                const to = walkthroughFollow(view, most, 0);
                view.frame.style.setProperty('--km-walkthrough-shift', `${to}px`);
                walkthroughEdge(view, to, whole - most - to);
            });
        }

        function measure() {
            const wasHeld = walkthroughHeld === walk;
            const where = wasHeld && keys.length ? locate(progress) : null;
            clearStack();
            rejoin();
            host.setAttribute('data-km-measuring', '');
            host.removeAttribute('data-km-mode');
            mode = '';
            rest();
            pane.style.removeProperty('min-height');
            if (host.getClientRects().length) {
                mode = 'stack';
                if (!prefersReducedMotion() && host.closest('.km-page--clamped') === null) {
                    host.setAttribute('data-km-mode', 'stage');
                    if (host.clientWidth >= WALKTHROUGH_WIDE) mode = 'stage';
                }
                host.setAttribute('data-km-mode', mode);
            }
            if (out) out.hidden = mode !== 'stage' || !text;
            if (mode === 'stage') {
                const top = headerHeight();
                const space = window.innerHeight - top;
                if (out && text) {
                    out.textContent = text;
                    out.style.height = 'auto';
                }
                const full = out && text ? out.offsetHeight : 0;
                const whole = code.offsetHeight;
                const line = main.lines.get(1)?.getBoundingClientRect().height || 20;
                const pad = Math.max(0, whole - line * main.lines.size);
                const least = Math.min(whole, pad + line * WALKTHROUGH_MIN_LINES);
                const caption = frame.offsetHeight - stage.offsetHeight - full;
                const most = Math.min(
                    whole,
                    Math.max(
                        least,
                        Math.min(
                            space * WALKTHROUGH_SHARE,
                            space - 2 * (full + WALKTHROUGH_ROOM),
                        ) - caption,
                    ),
                );
                room = most < whole
                    ? Math.max(least, pad + line * Math.floor((most - pad) / line))
                    : most;
                host.style.setProperty('--km-walkthrough-stage', `${room}px`);
                height = caption + room;
                host.style.setProperty('--km-walkthrough-notes', `${height}px`);
                pane.style.minHeight = `${pane.offsetHeight}px`;
                if (out) {
                    out.replaceChildren();
                    out.style.removeProperty('height');
                }
                const starts = [];
                const ends = [];
                blocks.forEach((block) => {
                    const size = block.offsetHeight;
                    const tall = size > height - 2 * WALKTHROUGH_PAD;
                    const from = tall
                        ? block.offsetTop - WALKTHROUGH_PAD
                        : block.offsetTop + size / 2 - height / 2;
                    starts.push(from);
                    ends.push(tall ? block.offsetTop + size - height + WALKTHROUGH_PAD : from);
                });
                let at = 0;
                blocks.forEach((_, note) => {
                    const hold = Math.max(
                        owned[note].length * payload.pace,
                        ends[note] - starts[note],
                    );
                    keys.push({
                        kind: 'hold', note, from: at, to: at + hold, a: starts[note], b: ends[note],
                    });
                    at += hold;
                    if (note === blocks.length - 1) return;
                    const move = Math.max(1, Math.abs(starts[note + 1] - ends[note]));
                    keys.push({
                        kind: 'move', note, from: at, to: at + move, a: ends[note], b: starts[note + 1],
                    });
                    at += move;
                });
                total = at;
                progress = clamp(progress, 0, total);
            } else if (mode === 'stack') {
                stack();
            }
            void host.offsetHeight;
            host.removeAttribute('data-km-measuring');
            walk.shaped = shape();
            unseen = true;
            lastAway = null;
            edge();
            if (!wasHeld) return;
            if (mode !== 'stage') {
                release();
                return;
            }
            if (where) {
                const key = keys[where.at];
                progress = key.from + (key.to - key.from) * where.through;
            }
            recentre();
            render();
        }

        function go(at) {
            const key = keys.find((item) => item.kind === 'hold' && item.note === at);
            if (!key || walkthroughHeld !== walk) return;
            progress = key.from + 1;
            render();
        }

        let copiedTimer = 0;
        let copiedButton = null;
        const later = (wait, then) => {
            copiedTimer = window.setTimeout(then, wait);
        };
        const copied = (button, done) => {
            window.clearTimeout(copiedTimer);
            copiedButton?.classList.remove('km-is-fading', 'success');
            copiedButton = button;
            button.classList.toggle('success', done);
            if (!done) return;
            later(TIMING.tooltipHold(), () => {
                button.classList.add('km-is-fading');
                later(TIMING.fast(), () => {
                    button.classList.remove('success');
                    later(TIMING.fast() * 2, () => button.classList.remove('km-is-fading'));
                });
            });
        };

        stage.addEventListener('scroll', rafThrottle(edge), { passive: true });

        host.addEventListener('click', (event) => {
            const value = event.target.closest?.('[data-km-long]');
            if (value) unfold(value);
            const button = event.target.closest?.('[data-km-copy]');
            if (button) copyText(walkthroughSource(payload)).then((done) => copied(button, done));
        });

        host.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter' && event.key !== ' ') return;
            if (!event.target.matches?.('[data-km-long]')) return;
            event.preventDefault();
            unfold(event.target);
        });

        host.addEventListener('focusin', () => {
            focusedAt = performance.now();
        });

        stage.addEventListener('pointerdown', (event) => {
            touched = event.pointerType === 'touch';
            loosen();
        });
        stage.addEventListener('focusin', loosen);
        stage.addEventListener('focusout', (event) => {
            if (!stage.contains(event.relatedTarget)) ease();
        });

        box.addEventListener('scroll', () => {
            box.scrollTop = 0;
        }, { passive: true });

        box.addEventListener('focusin', (event) => {
            const block = event.target.closest?.('[data-km-note]');
            if (mode !== 'stage' || !block) return;
            if (!walkthroughHeld) lock(centre() >= walkthroughFocus() ? 1 : -1);
            else if (walkthroughHeld !== walk) return;
            if (!block.hasAttribute('data-km-active')) go(Number(block.dataset.kmNote));
        });

        host.addEventListener('load', () => {
            walk.shaped = '';
            walkthroughSoon();
        }, true);

        walkthroughWire();
        return walk;
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
            initTabSets,
            initShowMore,
            initHeaderSearch,
            initAnchorScrolling,
            initFocusInView,
            initCopyUrl,
            initHeaderLinks,
            initImageZoom,
            initPixelatedBlur,
            initTouchReveal,
            initHeaderNavDropdowns,
            initDropdowns,
            initHighlightedLines,
            initCopyButtonNames,
            initScrollable,
            initYouTubeCards,
            initYouTubeFacades,
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
})();
