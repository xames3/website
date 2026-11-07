(() => {
    'use strict';

    const {
        FOCUSABLE,
        TIMING,
        anchorTargetY,
        announce,
        attempt,
        copyText,
        decodeId,
        fetchJson,
        glideTo,
        headerHeight,
        isModifiedClick,
        layoutTop,
        makeIcon,
        onVisible,
        prefersReducedMotion,
        rafThrottle,
        say,
        settleHash,
    } = window.Kaamiki;
    const root = document.documentElement;

    const SCROLL_QUIET_FRAMES = 3;
    const SCROLL_PATIENCE_MS = 3000;
    const PIXELATE_RATIO = 20;
    const DROPDOWN_OPEN_DELAY_MS = 40;
    const DROPDOWN_CLOSE_DELAY_MS = 140;
    const DROPDOWN_SWITCH_DELAY_MS = 90;
    const DROPDOWN_AIM_WINDOW_MS = 120;
    const DROPDOWN_AIM_STEP_MS = 60;
    const DROPDOWN_AIM_MS = 450;
    const DROPDOWN_WRAPPED_CLOSE_DELAY_MS = 700;
    const DROPDOWN_EDGE_PX = 8;
    const DROPDOWN_ROWS = 3;
    const SIDEBAR_WIDE_PX = 768;
    const NAV_WIDE_PX = 960;
    const NAV_WRAPPED = 'km-document--nav-wrapped';
    const SCROLLTOP_AFTER_PX = 200;
    const TOOLTIP_ROOM_PX = 32;

    function initHeaderHeight() {
        const header = document.querySelector('.km-header');
        if (!header) return;
        const fit = () => root.style.setProperty(
            '--km-header-height',
            `${headerHeight()}px`,
        );
        fit();
        new ResizeObserver(rafThrottle(fit)).observe(header);
    }
    function initKeyboardModality() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Tab'
                || event.key?.startsWith('Arrow')) {
                root.setAttribute('data-km-keyboard', '');
            }
        }, true);
        document.addEventListener(
            'pointerdown',
            () => root.removeAttribute('data-km-keyboard'),
            true,
        );
    }

    function initLogoInvert() {
        const SOLID_RATIO = 0.98;
        const verdicts = new Map();

        const isBlack = (image) => {
            if (!image.naturalWidth) return false;
            const scale = Math.min(
                1,
                64 / Math.max(image.naturalWidth, image.naturalHeight),
            );
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
            canvas.height = Math.max(
                1,
                Math.round(image.naturalHeight * scale),
            );
            const context = canvas
                .getContext('2d', { willReadFrequently: true });
            context.drawImage(image, 0, 0, canvas.width, canvas.height);
            const { data } = context
                .getImageData(0, 0, canvas.width, canvas.height);
            let opaque = 0;
            let black = 0;
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] < 32) continue;
                opaque += 1;
                if (Math.max(data[i], data[i + 1], data[i + 2]) < 64) {
                    black += 1;
                }
            }
            return opaque > 0 && black / opaque >= SOLID_RATIO;
        };

        document.querySelectorAll('.km-logo--single').forEach((image) => {
            const check = () => {
                const key = image.currentSrc || image.src;
                if (!verdicts.has(key)) {
                    try {
                        verdicts.set(key, isBlack(image));
                    } catch {
                        verdicts.set(key, false);
                    }
                }
                image.classList.toggle('km-logo--invert', verdicts.get(key));
            };
            if (image.complete) check();
            else image.addEventListener('load', check, { once: true });
        });
    }

    function initNavFit() {
        const tree = document.querySelector('.km-header__nav-tree');
        if (!tree || !document.querySelector('.km-layout--nav-in-header')) {
            return;
        }
        const wraps = () => {
            const tops = new Set(Array.from(tree.querySelectorAll(
                '.km-header__nav-group, .km-header__nav-links > li',
            )).map((item) => Math.round(item.getBoundingClientRect().top)));
            return tops.size > 1;
        };
        let icons = root.classList.contains('km-document--no-icons');
        const fit = () => {
            root.classList.remove(NAV_WRAPPED);
            if (window.innerWidth >= NAV_WIDE_PX && wraps()) {
                root.classList.add(NAV_WRAPPED);
            }
        };
        let frame = 0;
        const later = () => {
            cancelAnimationFrame(frame);
            frame = requestAnimationFrame(fit);
        };
        fit();
        window.addEventListener('resize', later, { passive: true });
        window.addEventListener('load', later, { once: true });
        document.fonts.ready.then(later);
        new MutationObserver(() => {
            const now = root.classList.contains('km-document--no-icons');
            if (now !== icons) {
                icons = now;
                later();
            }
        }).observe(root, { attributes: true, attributeFilter: ['class'] });
    }

    function initSidebar() {
        const sidebar = document.getElementById('km-sidebar');
        const toggle = document.querySelector('.km-header__menu-toggle');
        const backdrop = document.querySelector('.km-sidebar__backdrop');
        if (!sidebar || !toggle) return;
        let open = false;
        const stops = () => Array.from(sidebar.querySelectorAll(FOCUSABLE))
            .filter((element) => (
                element.tabIndex >= 0 && element.getClientRects().length
            ));
        const enter = (frames = 0) => {
            if (!open) return;
            if (getComputedStyle(sidebar).visibility !== 'visible'
                && frames < 30) {
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
            else if (!next && restore && inside) {
                toggle.focus({ preventScroll: true });
            }
        };
        toggle.addEventListener('click', (event) => (
            show(!open, true, event.detail === 0)
        ));
        backdrop?.addEventListener('click', () => show(false));
        sidebar.addEventListener('click', (event) => {
            const spot = toggle.getBoundingClientRect();
            if (
                open
                && !event.target.closest?.('a, button, input')
                && event.clientX >= spot.left && event.clientX <= spot.right
                && event.clientY >= spot.top && event.clientY <= spot.bottom
            ) {
                show(false);
                return;
            }
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
            const focusedIndex = items.indexOf(document.activeElement);
            const next = focusedIndex < 0
                ? 0
                : focusedIndex + (event.shiftKey ? -1 : 1);
            event.preventDefault();
            items[(next + items.length) % items.length].focus();
        });
        window.addEventListener('resize', () => {
            const nested = document.querySelector('.km-layout--nav-in-header');
            const wide = nested ? NAV_WIDE_PX : SIDEBAR_WIDE_PX;
            if (open && window.innerWidth >= wide
                && !(nested && root.classList.contains(NAV_WRAPPED))) {
                show(false, false);
            }
        }, { passive: true });
    }

    function initScrollTop() {
        const button = document.getElementById('km-scrolltop');
        if (!button) return;
        let last = 0;
        button.addEventListener('click', () => glideTo(0));
        window.addEventListener('scroll', () => {
            const y = window.scrollY;
            if (y !== last) {
                const bottom = y + window.innerHeight
                    >= root.scrollHeight - SCROLLTOP_AFTER_PX;
                button.classList.toggle(
                    'km-scrolltop--hidden',
                    !(y > SCROLLTOP_AFTER_PX && (y < last || bottom)),
                );
            }
            last = Math.max(0, y);
        }, { passive: true });
    }

    function initHeaderSearch() {
        const search = document.querySelector('.km-header__search .km-search');
        if (!search) return;
        const input = search.querySelector('.km-search__input');
        const submit = search.querySelector('.km-search__submit');

        const open = () => {
            search.classList.add('km-search--open');
            if (!input) return;
            input.focus({ preventScroll: true });
        };
        const close = () => {
            if (input && input.value.trim()) return;
            search.classList.remove('km-search--open');
        };

        submit?.addEventListener('click', (event) => {
            if (search.classList.contains('km-search--open')) return;
            event.preventDefault();
            open();
        });

        input?.addEventListener('focus', () => (
            search.classList.add('km-search--open')
        ));
        input?.addEventListener('blur', () => setTimeout(close, 0));
        input?.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;
            close();
            input.blur();
        });

        const apple = /Mac|iPhone|iPad|iPod/.test(
            navigator.userAgentData?.platform || navigator.platform || '',
        );
        window.addEventListener('keydown', (event) => {
            if (!input || String(event.key).toLowerCase() !== 'k') return;
            if (!(apple ? event.metaKey : event.ctrlKey)
                || event.altKey || event.shiftKey) return;
            event.preventDefault();
            input.focus();
        });

        document.addEventListener('click', (event) => {
            if (!search.contains(event.target)) close();
        });
    }

    function scrollToElement(element) {
        return glideTo(anchorTargetY(element));
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
            attempt(() => history.pushState(history.state, '', `#${id}`));
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
                if (now - began < SCROLL_PATIENCE_MS) {
                    requestAnimationFrame(look);
                }
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
            if (event.target.closest?.('.km-header, .km-sidebar')) return;
            reachFocus(event.target);
        });
    }

    const tooltipTimers = new WeakMap();

    function flashTooltip(link, message, transient = false) {
        announce(message);
        window.clearTimeout(tooltipTimers.get(link));
        link.setAttribute('data-tooltip', message);
        void link.offsetWidth;
        link.classList.add('km-tooltip', 'km-tooltip--visible');
        tooltipTimers.set(link, window.setTimeout(() => {
            link.classList.remove('km-tooltip--visible');
            if (!transient) return;
            tooltipTimers.set(link, window.setTimeout(
                () => link.removeAttribute('data-tooltip'),
                TIMING.normal(),
            ));
        }, TIMING.tooltipHold()));
    }

    function canonicalUrl(href) {
        const base = document.querySelector('link[rel="canonical"]')?.href
            || window.location.href;
        return href === undefined ? base : new URL(href, base).href;
    }

    function initCopyUrl() {
        document.querySelectorAll('[data-km-copy-url]').forEach((link) => {
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
        link.classList.toggle(
            'km-tooltip--below',
            text.top - frame.top < TOOLTIP_ROOM_PX,
        );
        link.style.setProperty(
            '--km-headerlink-top',
            `${text.top - frame.top}px`,
        );
        link.style.setProperty(
            '--km-headerlink-x',
            `${(x ?? text.left) - frame.left}px`,
        );
        return text;
    }

    function headingLink(event) {
        const heading = event.target.closest('h1, h2, h3, h4, h5, h6');
        const link = heading?.querySelector(':scope > a.headerlink');
        if (!link) return null;
        const other = event.target.closest(FOCUSABLE);
        if (other && other !== heading
            && (heading.contains(other)
                || !other.matches('[tabindex]'))) return null;
        if (String(window.getSelection())) return null;
        const text = measureHeaderLink(link, event.clientX);
        return event.clientY >= text.top && event.clientY <= text.bottom
            ? link
            : null;
    }

    function initHeaderLinks() {
        const copying = root.hasAttribute('data-km-copy-links');
        document.querySelectorAll('a.headerlink').forEach((link) => {
            link.parentElement.classList.add('km-page__heading--linked');
        });
        document.addEventListener('focusin', (event) => {
            if (event.target.matches?.('a.headerlink')) {
                measureHeaderLink(event.target);
            }
        });
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a.headerlink');
            if (!link) {
                headingLink(event)?.click();
                return;
            }
            if (event.isTrusted) {
                measureHeaderLink(
                    link,
                    event.detail ? event.clientX : undefined,
                );
            }
            if (!copying) return;
            copyText(canonicalUrl(link.getAttribute('href') || ''))
                .then((copied) => {
                    flashTooltip(
                        link,
                        copied ? say('copied') : say('failed'),
                        true,
                    );
                });
        });
    }

    function dressCopyButton(button) {
        if ('kmDressed' in button.dataset) return;
        button.dataset.kmDressed = '';
        const put = () => {
            if (button.querySelector('.km-copy__icon')) return;
            button.append(...[
                makeIcon('copy', 'km-copy__icon', 'km-copy__icon--copy'),
                makeIcon('copied', 'km-copy__icon', 'km-copy__icon--done'),
            ].filter(Boolean));
        };
        put();
        new MutationObserver(put).observe(button, { childList: true });
    }

    function initCopyButtonNames() {
        const cells = document.querySelectorAll('div.highlight > pre').length;
        if (!cells) return;
        const name = () => {
            const buttons = document.querySelectorAll('button.copybtn');
            buttons.forEach((button) => {
                dressCopyButton(button);
                if (button.hasAttribute('aria-label')) return;
                const title = button.querySelector('svg title')
                    ?.textContent.trim();
                button.setAttribute(
                    'aria-label',
                    title || button.dataset.tooltip || say('copy'),
                );
            });
            return buttons.length >= cells;
        };
        if (name()) return;
        const watch = new MutationObserver(() => {
            if (name()) watch.disconnect();
        });
        watch.observe(document.body, { childList: true, subtree: true });
        window.addEventListener(
            'load',
            () => setTimeout(() => watch.disconnect(), 5000),
            { once: true },
        );
    }

    function initHighlightedLines() {
        const blocks = [...document.querySelectorAll('.highlight pre')]
            .filter((pre) => pre.querySelector('.hll, .gi, .gd'));
        if (!blocks.length) return;
        const measure = () => {
            blocks.forEach((pre) => (
                pre.style.removeProperty('--km-code-width')
            ));
            const widths = blocks.map((pre) => {
                const { paddingLeft, paddingRight } = getComputedStyle(pre);
                return Math.max(
                    0,
                    pre.scrollWidth
                        - parseFloat(paddingLeft) - parseFloat(paddingRight),
                );
            });
            blocks.forEach((pre, blockIndex) => pre.style.setProperty(
                '--km-code-width',
                `${widths[blockIndex]}px`,
            ));
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
        document.querySelectorAll('.km-tabs').forEach((set) => {
            const tabs = Array.from(
                set.querySelectorAll(':scope > input'),
                (input) => {
                    const label = input.nextElementSibling;
                    return [input, label, label?.nextElementSibling];
                },
            );
            const shaped = ([, label, panel]) => (
                label?.matches('label') && panel?.matches('.km-tabs__panel')
            );
            if (!tabs.length || !tabs.every(shaped)) return;
            const bar = document.createElement('div');
            bar.className = ['km-tabs__bar', set.dataset.kmBar]
                .filter(Boolean).join(' ');
            bar.setAttribute('role', 'tablist');
            set.prepend(bar);
            bars.push(bar);
            tabs.forEach(([input, text, panel]) => {
                const label = document.createElement('span');
                label.className = text.className;
                label.id = text.id || `${input.id}-tab`;
                label.append(...text.childNodes);
                label.addEventListener('click', () => {
                    if (input.checked) return;
                    input.checked = true;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                });
                text.remove();
                bar.append(input, label);
                panels.set(input, panel);
                panel.id = panel.id || `${input.id}-panel`;
                label.setAttribute('role', 'tab');
                label.setAttribute('aria-controls', panel.id);
                panel.setAttribute('role', 'tabpanel');
                panel.setAttribute('aria-labelledby', label.id);
                input.setAttribute('tabindex', '-1');
                input.setAttribute('aria-hidden', 'true');
            });
        });
        if (!bars.length) return;

        const kept = (name) => `km:tabs:${name}`;
        const group = (input) => input.closest('.km-tabs')?.dataset.kmGroup;
        const nests = (set) => !!set.querySelector(
            `.km-tabs[data-km-group="${CSS.escape(set.dataset.kmGroup)}"]`,
        );
        const choose = (set, key) => {
            const input = Array.from(set.querySelectorAll('input[data-km-key]'))
                .find((tab) => (
                    tab.dataset.kmKey === key && tab.closest('.km-tabs') === set
                ));
            if (input && !input.checked) input.checked = true;
        };
        const linked = location.hash.length > 1
            ? document.getElementById(decodeId(location.hash.slice(1)))
            : null;
        document.querySelectorAll('.km-tabs[data-km-group]').forEach((set) => {
            if ((linked && set.contains(linked)) || nests(set)) return;
            const key = attempt(() => (
                localStorage.getItem(kept(set.dataset.kmGroup))
            ));
            if (key) choose(set, key);
        });

        const mark = () => panels.forEach((panel, input) => {
            const label = input.nextElementSibling;
            panel.classList.toggle('km-tabs__panel--current', input.checked);
            label.setAttribute('aria-selected', String(input.checked));
            label.tabIndex = input.checked ? 0 : -1;
        });
        const place = (bar, slide) => {
            const label = bar.querySelector(
                ':scope > input:checked + .km-tabs__label',
            );
            if (!label) return;
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            bar.classList.toggle('km-tabs__bar--sliding', slide);
            bar.style.setProperty(
                '--km-tab-x',
                `${box.left - view.left - bar.clientLeft + bar.scrollLeft}px`,
            );
            bar.style.setProperty(
                '--km-tab-y',
                `${box.top - view.top - bar.clientTop + bar.scrollTop}px`,
            );
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
            const end = box.right - view.left - bar.clientLeft
                - bar.clientWidth + inset;
            const shift = start < 0 ? start : Math.min(Math.max(end, 0), start);
            if (shift) {
                bar.scrollBy({
                    left: shift,
                    behavior: prefersReducedMotion() ? 'auto' : 'smooth',
                });
            }
        };

        settle();
        document.addEventListener('DOMContentLoaded', settle, { once: true });
        const watch = new ResizeObserver((entries) => {
            new Set(entries.map(({ target }) => target.parentElement))
                .forEach((bar) => place(bar, false));
        });
        bars.forEach((bar) => (
            bar.querySelectorAll(':scope > .km-tabs__label')
                .forEach((label) => watch.observe(label))
        ));
        document.addEventListener('keydown', (event) => {
            const label = event.target.closest?.(
                '.km-tabs__bar > [role="tab"]',
            );
            if (!label) return;
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                label.click();
                return;
            }
            const moves = {
                ArrowLeft: -1, ArrowRight: 1, Home: 0, End: 0,
            };
            if (!(event.key in moves)) return;
            const bar = label.parentElement;
            const tabs = Array.from(
                bar.querySelectorAll(':scope > [role="tab"]'),
            );
            const here = tabs.indexOf(label);
            const to = event.key === 'Home' ? 0
                : event.key === 'End' ? tabs.length - 1
                    : (here + moves[event.key] + tabs.length) % tabs.length;
            const input = bar.querySelectorAll(':scope > input')[to];
            event.preventDefault();
            input.checked = true;
            input.dispatchEvent(new Event('change', { bubbles: true }));
            tabs[to].focus();
        });
        document.addEventListener('change', (event) => {
            if (!panels.has(event.target)) return;
            const named = group(event.target);
            if (named) {
                attempt(() => localStorage.setItem(
                    kept(named),
                    event.target.dataset.kmKey,
                ));
                document.querySelectorAll(
                    `.km-tabs[data-km-group="${CSS.escape(named)}"]`,
                ).forEach((set) => {
                    if (!set.contains(event.target) && !nests(set)) {
                        choose(set, event.target.dataset.kmKey);
                    }
                });
            }
            mark();
            bars.forEach((bar) => place(bar, true));
            reveal(event.target.nextElementSibling);
        });
    }

    function initCarousels() {
        const carousels = document.querySelectorAll('[data-km-carousel]');
        carousels.forEach((carousel) => {
            const track = carousel.querySelector('.km-carousel__track');
            const [back, forward] = carousel.querySelectorAll(
                '[data-km-carousel-step]',
            );
            const items = () => Array.from(track.children)
                .filter((item) => item.offsetWidth > 0);
            const room = () => track.scrollWidth - track.clientWidth;
            const goTo = (left) => track.scrollTo({
                left,
                behavior: prefersReducedMotion() ? 'auto' : 'smooth',
            });
            const step = (way) => {
                const at = track.scrollLeft;
                const stops = items().map((item) => Math.min(
                    item.offsetLeft,
                    room(),
                ));
                if (way > 0) {
                    goTo(stops.find((stop) => stop > at + 1) ?? room());
                } else {
                    goTo(stops.findLast((stop) => stop < at - 1) ?? 0);
                }
            };
            const name = () => carousel.getAttribute('aria-label')
                || document.getElementById(
                    carousel.getAttribute('aria-labelledby'),
                )?.textContent.trim() || '';
            const update = () => {
                const left = room();
                const at = track.scrollLeft;
                const still = left <= 1;
                carousel.classList.toggle('km-carousel--still', still);
                if (still) {
                    track.removeAttribute('tabindex');
                    track.removeAttribute('role');
                    track.removeAttribute('aria-label');
                } else {
                    track.setAttribute('tabindex', '0');
                    track.setAttribute('role', 'group');
                    track.setAttribute('aria-label', name());
                }
                back?.setAttribute('aria-disabled', String(at <= 1));
                forward?.setAttribute('aria-disabled', String(at >= left - 1));
            };
            [back, forward].forEach((button) => {
                button?.addEventListener('click', () => {
                    if (button.getAttribute('aria-disabled') === 'true') {
                        return;
                    }
                    step(Number(button.dataset.kmCarouselStep));
                });
            });
            track.addEventListener('keydown', (event) => {
                if (event.target !== track || event.altKey || event.ctrlKey
                    || event.metaKey || event.shiftKey) return;
                if (event.key === 'ArrowRight') step(1);
                else if (event.key === 'ArrowLeft') step(-1);
                else return;
                event.preventDefault();
            });
            track.addEventListener('focusin', (event) => {
                const item = items().find(
                    (each) => each.contains(event.target),
                );
                if (!item) return;
                const at = track.scrollLeft;
                if (item.offsetLeft < at - 1
                    || item.offsetLeft + item.offsetWidth
                        > at + track.clientWidth + 1) {
                    track.scrollTo({
                        left: Math.min(item.offsetLeft, room()),
                        behavior: 'instant',
                    });
                }
            });
            const title = carousel.querySelector('.km-carousel__title');
            const nav = carousel.querySelector('.km-carousel__nav');
            const place = () => {
                if (!title || !nav) return;
                carousel.classList.add('km-carousel--measuring');
                nav.style.display = 'flex';
                const wide = title.getBoundingClientRect().width
                    + nav.getBoundingClientRect().width
                    + parseFloat(getComputedStyle(root).fontSize);
                const line = title.offsetTop + title.offsetHeight
                    - parseFloat(getComputedStyle(title).lineHeight) / 2
                    - nav.offsetHeight / 2;
                nav.style.display = '';
                carousel.classList.remove('km-carousel--measuring');
                const inline = wide <= carousel.clientWidth;
                carousel.classList.toggle('km-carousel--inline', inline);
                nav.style.insetBlockStart = inline ? `${line}px` : '';
            };
            const refresh = () => {
                update();
                place();
            };
            const soon = rafThrottle(refresh);
            track.addEventListener('scroll', soon, { passive: true });
            const watch = new ResizeObserver(soon);
            watch.observe(carousel);
            if (title) watch.observe(title);
            watch.observe(track);
            items().forEach((item) => watch.observe(item));
            document.fonts.ready.then(refresh);
            refresh();
            carousel.setAttribute('data-km-ready', '');

            const pace = Number(carousel.dataset.kmCarouselInterval);
            if (!pace || prefersReducedMotion()) return;
            const way = carousel.dataset.kmCarouselDirection === 'left'
                ? -1
                : 1;
            const holds = new Set();
            const hold = (reason, on) => {
                if (on) holds.add(reason);
                else holds.delete(reason);
            };
            carousel.addEventListener(
                'pointerenter',
                (event) => event.pointerType === 'mouse' && hold('hover', 1),
            );
            carousel.addEventListener('pointerleave', () => hold('hover', 0));
            carousel.addEventListener('focusin', () => hold('focus', 1));
            carousel.addEventListener('focusout', () => hold('focus', 0));
            carousel.addEventListener('touchstart', () => hold('touch', 1), {
                passive: true,
            });
            carousel.addEventListener('touchend', () => hold('touch', 0));
            carousel.addEventListener('touchcancel', () => hold('touch', 0));
            new IntersectionObserver((entries) => {
                hold('away', !entries.at(-1).isIntersecting);
            }).observe(carousel);
            setInterval(() => {
                if (holds.size || document.hidden || room() <= 1) return;
                const at = track.scrollLeft;
                if (way > 0 && at >= room() - 1) goTo(0);
                else if (way < 0 && at <= 1) goTo(room());
                else step(way);
            }, pace * 1000);
        });
    }

    function initRelatedPictures() {
        const waves = () => {
            const holder = document.createElement('span');
            holder.className = 'km-related__waves';
            holder.setAttribute('aria-hidden', 'true');
            ['a', 'b', 'c'].forEach((wave) => {
                const layer = document.createElement('span');
                layer.className = `km-byline__wave km-byline__wave--${wave}`;
                holder.append(layer);
            });
            return holder;
        };
        const swap = (image) => image.replaceWith(waves());
        document.querySelectorAll('.km-related__image > img').forEach(
            (image) => {
                if (image.complete && image.naturalWidth === 0
                    && image.currentSrc) {
                    swap(image);
                } else {
                    image.addEventListener('error', () => swap(image), {
                        once: true,
                    });
                }
            },
        );
    }

    function initScrollable() {
        const blocks = Array.from(document.querySelectorAll(
            '.highlight pre, .km-page__content table, .km-table',
        ));
        if (!blocks.length) return;
        const mark = () => {
            blocks.forEach((pre) => {
                const scrolls = pre.scrollWidth > pre.clientWidth + 1
                    || pre.scrollHeight > pre.clientHeight + 1;
                if (scrolls) {
                    pre.setAttribute('tabindex', '0');
                    pre.setAttribute('role', 'region');
                    pre.setAttribute(
                        'aria-label',
                        say(pre.matches('pre') ? 'code' : 'table'),
                    );
                } else {
                    pre.removeAttribute('tabindex');
                    pre.removeAttribute('role');
                    pre.removeAttribute('aria-label');
                }
            });
        };
        const soon = rafThrottle(mark);
        mark();
        document.fonts.ready.then(mark);
        window.addEventListener('resize', soon, { passive: true });
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }

    function initBreadcrumbs() {
        const nav = document.querySelector('.km-breadcrumbs');
        if (!nav) return;
        const links = Array.from(nav.querySelectorAll('.km-breadcrumbs__link'));
        if (links.length < 2) return;

        const separators = links.map((link) => link.previousElementSibling);
        const order = [...links.keys()]
            .slice(1, -1).concat(0, links.length - 1);
        const more = document.createElement('a');
        more.className = 'km-breadcrumbs__link km-breadcrumbs__link--more';
        more.textContent = '...';
        more.hidden = true;
        let gap = null;

        const show = (count) => {
            const out = order.slice(0, count);
            links.forEach((link, index) => {
                link.hidden = out.includes(index);
                if (separators[index]) separators[index].hidden = link.hidden;
            });
            gap?.remove();
            gap = null;
            more.hidden = count === 0;
            if (!count) return;
            const first = Math.min(...out);
            if (separators[first]) {
                gap = separators[first].cloneNode(true);
                gap.hidden = false;
                nav.insertBefore(gap, separators[first]);
                nav.insertBefore(more, separators[first]);
            } else {
                nav.insertBefore(more, links[first]);
            }
            more.href = links[Math.max(...out)].href;
            const names = links
                .flatMap((link, index) => (
                    out.includes(index) ? [link.textContent.trim()] : []
                ))
                .join(', ');
            more.setAttribute('aria-label', names);
            more.title = names;
        };
        const fit = () => {
            nav.classList.add('km-breadcrumbs--measuring');
            let count = 0;
            show(count);
            while (nav.scrollWidth > nav.clientWidth + 1
                && count < order.length) {
                count += 1;
                show(count);
            }
            nav.classList.remove('km-breadcrumbs--measuring');
        };
        const soon = rafThrottle(fit);
        fit();
        document.fonts.ready.then(fit);
        new ResizeObserver(soon).observe(nav.parentElement);
    }

    function initBylineFit() {
        const byline = document.querySelector('.km-byline--align-left');
        if (!byline || !byline.querySelector('.km-byline__language')) return;

        const parts = '.km-byline__profile, .km-byline__reading-time, '
            + '.km-byline__language, .km-byline__copy, .km-byline__source';
        const wraps = () => {
            const centres = Array.from(byline.querySelectorAll(parts))
                .filter((part) => part.getClientRects().length)
                .map((part) => {
                    const box = part.getBoundingClientRect();
                    return box.top + box.height / 2;
                });
            return Math.max(...centres) - Math.min(...centres) > 12;
        };
        const fit = () => {
            byline.classList.remove('km-byline--tight');
            if (wraps()) byline.classList.add('km-byline--tight');
        };
        const soon = rafThrottle(fit);
        fit();
        document.fonts.ready.then(fit);
        new ResizeObserver(soon).observe(byline.parentElement);
    }

    function initColumnFit() {
        const block = ':is([class*="highlight-"], .literal-block-wrapper)';
        const code = `:scope > .km-columns__column > ${block}`;
        const grids = Array.from(document.querySelectorAll('.km-columns'))
            .filter((grid) => grid.querySelector(code));
        if (!grids.length) return;

        const widths = new Map();
        const fit = (grid) => {
            grid.style.removeProperty('--km-columns-count');
            const declared = Number(
                getComputedStyle(grid).getPropertyValue('--km-columns-count'),
            );
            const cells = Array.from(grid.children).filter((cell) => (
                cell.classList.contains('km-columns__column')
            ));
            const room = grid.getBoundingClientRect().width;
            widths.set(grid, room);
            if (declared < 2 || !room || cells.some((cell) => (
                !cell.classList.contains('km-columns__column--span-1')
            ))) return;
            const widest = Math.max(...cells.map((cell) => {
                const saved = cell.getAttribute('style');
                const scrolling = Array.from(
                    cell.querySelectorAll(`:scope > ${block}`),
                );
                cell.style.cssText = 'flex: none; width: max-content; '
                    + 'max-width: none;';
                scrolling.forEach((each) => (
                    each.style.setProperty('contain', 'inline-size')
                ));
                const width = cell.getBoundingClientRect().width;
                scrolling.forEach((each) => {
                    each.style.removeProperty('contain');
                    if (!each.getAttribute('style')) {
                        each.removeAttribute('style');
                    }
                });
                if (saved === null) cell.removeAttribute('style');
                else cell.setAttribute('style', saved);
                return width;
            }));
            const gap = parseFloat(getComputedStyle(grid).columnGap) || 0;
            const count = Math.max(
                1,
                Math.min(declared, Math.floor((room + gap) / (widest + gap))),
            );
            if (count < declared) {
                grid.style.setProperty('--km-columns-count', count);
            }
        };
        const all = () => grids.forEach(fit);
        const watch = new ResizeObserver((entries) => entries.forEach(
            ({ target }) => {
                if (Math.abs(
                    target.getBoundingClientRect().width - widths.get(target),
                ) > 0.5) fit(target);
            },
        ));
        all();
        document.fonts.ready.then(all);
        grids.forEach((grid) => watch.observe(grid));
    }

    function initScrollFades() {
        const kinds = [
            { selector: '.highlight pre', axis: 'x', code: true },
            {
                selector: '.km-page__content table, .km-table, .km-tabs__bar',
                axis: 'x',
            },
            { selector: '.km-sidebar__content', axis: 'y' },
        ];
        const items = [];
        kinds.forEach(({ selector, axis, code }) => {
            document.querySelectorAll(selector).forEach((scroller) => {
                const host = code
                    ? scroller.closest('.highlight') || scroller
                    : scroller;
                host.classList.add('km-fade', `km-fade--${axis}`);
                if (code) host.classList.add('km-fade--code');
                items.push({ scroller, host, axis });
            });
        });
        if (!items.length) return;

        const update = () => {
            items.forEach(({ scroller, host, axis }) => {
                const across = axis === 'x';
                const room = (across
                    ? scroller.scrollWidth - scroller.clientWidth
                    : scroller.scrollHeight - scroller.clientHeight);
                const at = Math.abs(
                    across ? scroller.scrollLeft : scroller.scrollTop,
                );
                host.classList.toggle('km-fade--start', room > 1 && at > 1);
                host.classList.toggle(
                    'km-fade--end',
                    room > 1 && at < room - 1,
                );
            });
        };
        const soon = rafThrottle(update);
        update();
        document.fonts.ready.then(update);
        window.addEventListener('resize', soon, { passive: true });
        document.addEventListener('km:fold', soon);
        const watch = new ResizeObserver(soon);
        items.forEach(({ scroller }) => {
            scroller.addEventListener('scroll', soon, { passive: true });
            watch.observe(scroller);
        });
    }

    function initImageZoom() {
        const wrap = (node, standalone) => {
            const image = node.matches('img')
                ? node
                : node.querySelector('img');
            const inner = document.createElement('div');
            inner.className = standalone
                ? 'km-zoom-inner km-zoom-inner--standalone'
                : 'km-zoom-inner';
            if (image.style.width) {
                inner.style.width = image.style.width;
                inner.style.maxWidth = '100%';
            }
            const scale = document.createElement('div');
            scale.className = 'km-figure__scale';
            node.parentElement.insertBefore(inner, node);
            inner.appendChild(scale);
            scale.appendChild(node);
        };
        const pictures = (figures) => (
            `${figures} > img, ${figures} > a.image-reference`
        );

        document.querySelectorAll(
            '.km-page__content figure.km-figure--fuzzy-blur > img, '
            + '.km-page__content figure.km-figure--fuzzy-blur '
            + '> a.image-reference',
        ).forEach((node) => wrap(node, false));
        if (prefersReducedMotion()) return;
        document.querySelectorAll(pictures(
            '.km-page__content figure.km-figure--zoom'
            + ':not(.km-figure--fuzzy-blur)',
        )).forEach((node) => wrap(node, false));
        document.querySelectorAll(
            '.km-page__content img.km-figure--zoom:not(figure img)',
        ).forEach((image) => wrap(image, true));
    }

    function initPixelatedBlur() {
        const draw = (image, canvas) => {
            const width = Math.max(
                1,
                Math.round(image.naturalWidth / PIXELATE_RATIO),
            );
            const height = Math.max(
                1,
                Math.round(image.naturalHeight / PIXELATE_RATIO),
            );
            canvas.width = width;
            canvas.height = height;
            canvas.getContext('2d').drawImage(image, 0, 0, width, height);
            canvas.classList.add('km-figure__pixelated-canvas--drawn');
        };

        document.querySelectorAll(
            '.km-page__content figure.km-figure--pixelated-blur img',
        ).forEach((image) => {
            const frame = document.createElement('div');
            frame.className = 'km-figure__pixelated-frame';
            if (image.style.width) frame.style.width = image.style.width;
            const canvas = document.createElement('canvas');
            canvas.className = 'km-figure__pixelated-canvas';
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
        if (window.matchMedia('(hover: hover) and (pointer: fine)')
            .matches) return;
        const selector = '.km-page__content figure.km-figure--zoom, '
            + '.km-page__content figure.km-figure--fuzzy-blur, '
            + '.km-page__content figure.km-figure--pixelated-blur, '
            + '.km-page__content figure.km-figure--greyscale';
        const figures = document.querySelectorAll(selector);
        if (!figures.length) return;

        document.addEventListener('click', (event) => {
            const figure = event.target.closest(selector);
            if (figure && event.target.closest('a')) return;
            const shouldReveal = figure
                && !figure.classList.contains('km-figure--revealed');
            figures.forEach((node) => (
                node.classList.remove('km-figure--revealed')
            ));
            if (shouldReveal) figure.classList.add('km-figure--revealed');
        });
    }

    function initHeaderNavDropdowns() {
        const nav = document.querySelector('.km-header__nav-tree');
        if (!nav) return;

        let uid = 0;
        let current = null;
        let timer = 0;
        const trail = [];
        const track = (event) => {
            const now = performance.now();
            trail.push({ x: event.clientX, y: event.clientY, time: now });
            while (trail.length > 1
                && now - trail[0].time > DROPDOWN_AIM_WINDOW_MS) trail.shift();
        };
        const aimed = () => {
            const to = trail[trail.length - 1];
            if (!current || !to
                || performance.now() - to.time > DROPDOWN_AIM_WINDOW_MS) {
                return false;
            }
            const box = current.list.getBoundingClientRect();
            if (to.y >= box.top) return false;
            if (trail.length < 2) return to.x >= box.left && to.x <= box.right;
            const from = trail[0];
            if (to.y <= from.y) return false;
            const side = (a, b, c) => (
                (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
            );
            const left = { x: box.left, y: box.top };
            const right = { x: box.right, y: box.top };
            const signs = [
                side(to, left, from),
                side(to, right, left),
                side(to, from, right),
            ];
            return signs.every((sign) => sign >= 0)
                || signs.every((sign) => sign <= 0);
        };

        const place = ({ group, list }) => {
            group.style.setProperty('--km-dropdown-shift', '0px');
            const drop = Math.max(
                0,
                nav.getBoundingClientRect().bottom
                    - group.getBoundingClientRect().bottom,
            );
            const wrapped = drop > 1;
            const box = list.getBoundingClientRect();
            const room = document.documentElement.clientWidth
                - DROPDOWN_EDGE_PX;
            const left = Math.max(
                DROPDOWN_EDGE_PX - box.left,
                Math.min(0, room - box.right),
            );
            group.style.setProperty(
                '--km-dropdown-drop',
                `${wrapped ? drop : 0}px`,
            );
            group.style.setProperty('--km-dropdown-shift', `${left}px`);
            group.dataset.kmWrapped = wrapped ? 'true' : '';
        };
        const hide = () => {
            clearTimeout(timer);
            if (!current) return;
            current.group.classList.remove('km-header__nav-group--open');
            current.trigger.setAttribute('aria-expanded', 'false');
            current = null;
            document.removeEventListener('mousemove', track);
            trail.length = 0;
        };
        const show = (menu) => {
            clearTimeout(timer);
            if (current === menu) return;
            hide();
            menu.group.classList.add('km-header__nav-group--open');
            place(menu);
            menu.trigger.setAttribute('aria-expanded', 'true');
            current = menu;
            document.addEventListener('mousemove', track, { passive: true });
        };
        const later = (fn, delay) => {
            clearTimeout(timer);
            timer = setTimeout(fn, delay);
        };

        const dropdown = (group, trigger, list) => {
            const menu = { group, trigger, list };
            const isLink = trigger.tagName === 'A';
            const arrow = makeIcon('nav_arrow', 'km-header__arrow');
            const holder = isLink
                ? trigger
                : trigger.querySelector('.caption-text');
            if (arrow && holder) holder.append(arrow);
            list.id = list.id || `km-nav-group-${++uid}`;
            const count = list.querySelectorAll(':scope > li').length;
            list.style.setProperty(
                '--km-dropdown-rows',
                Math.max(1, Math.min(DROPDOWN_ROWS, count)),
            );
            list.style.setProperty(
                '--km-dropdown-columns',
                Math.max(1, Math.ceil(count / DROPDOWN_ROWS)),
            );
            if (!isLink) {
                trigger.setAttribute('tabindex', '0');
                trigger.setAttribute('role', 'button');
                trigger.removeAttribute('aria-level');
            }
            trigger.setAttribute('aria-haspopup', 'true');
            trigger.setAttribute('aria-controls', list.id);
            trigger.setAttribute('aria-expanded', 'false');

            group.addEventListener('mouseenter', () => {
                if (current === menu) {
                    clearTimeout(timer);
                } else if (!current) {
                    later(() => show(menu), DROPDOWN_OPEN_DELAY_MS);
                } else {
                    const until = performance.now()
                        + DROPDOWN_SWITCH_DELAY_MS + DROPDOWN_AIM_MS;
                    const attempt = () => {
                        if (aimed() && performance.now() < until) {
                            later(attempt, DROPDOWN_AIM_STEP_MS);
                        } else show(menu);
                    };
                    later(attempt, DROPDOWN_SWITCH_DELAY_MS);
                }
            }, { passive: true });
            group.addEventListener('mouseleave', () => {
                if (group.querySelector(':focus-visible')) return;
                const delay = group.dataset.kmWrapped
                    ? DROPDOWN_WRAPPED_CLOSE_DELAY_MS
                    : DROPDOWN_CLOSE_DELAY_MS;
                const until = performance.now() + delay + DROPDOWN_AIM_MS;
                const attempt = () => {
                    if (aimed() && performance.now() < until) {
                        later(attempt, DROPDOWN_AIM_STEP_MS);
                    } else hide();
                };
                later(attempt, delay);
            }, { passive: true });
            group.addEventListener('focusout', (event) => {
                if (current === menu
                    && !group.contains(event.relatedTarget)) hide();
            });
            trigger.addEventListener('keydown', (event) => {
                if (!isLink && (event.key === 'Enter' || event.key === ' ')) {
                    event.preventDefault();
                    if (current === menu) hide();
                    else show(menu);
                } else if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    show(menu);
                    list.querySelector('a[href]')?.focus();
                }
            });
            group.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape' || current !== menu) return;
                hide();
                trigger.focus();
            });
        };
        window.addEventListener('resize', hide, { passive: true });

        Array.from(nav.querySelectorAll('p.caption')).forEach((caption) => {
            const list = caption.nextElementSibling;
            if (list?.tagName !== 'UL') return;

            const group = document.createElement('div');
            group.className = 'km-header__nav-group';
            caption.parentNode.insertBefore(group, caption);
            group.append(caption, list);
            dropdown(group, caption, list);
        });

        Array.from(nav.children).forEach((node) => {
            if (node.tagName === 'UL') {
                node.classList.add('km-header__nav-links');
            }
        });

        nav.querySelectorAll('.km-header__nav-links > li').forEach((item) => {
            const link = item.querySelector(':scope > a');
            const list = item.querySelector(':scope > ul');
            if (!link || !list) return;

            item.classList.add('km-header__nav-group');
            dropdown(item, link, list);
        });
    }

    function enrichYouTubeBlock(block) {
        const id = block.getAttribute('data-km-youtube-id');
        if (!id) return;
        const title = block.querySelector('.km-thumbnail__title a');
        const channel = block.querySelector('.km-thumbnail__channel');
        const picture = block.querySelector('.km-thumbnail__image img');
        const writtenTitle = block.hasAttribute('data-km-youtube-title');
        const writtenChannel = block.hasAttribute('data-km-youtube-channel');

        const watch = encodeURIComponent(`https://www.youtube.com/watch?v=${id}`);
        fetchJson(`https://www.youtube.com/oembed?url=${watch}&format=json`).then((data) => {
            if (!data) return;
            if (!writtenTitle && title && data.title) {
                title.textContent = data.title;
                if (picture) picture.alt = data.title;
            }
            if (!writtenChannel && channel && data.author_name) {
                channel.textContent = data.author_name;
            }
            if (channel && data.author_url) linkChannel(channel, title, data.author_url);
        });
    }

    function linkChannel(channel, title, address) {
        let url;
        try {
            url = new URL(address);
        } catch {
            return;
        }
        if (url.protocol !== 'https:' || !/(^|\.)youtube\.com$/.test(url.hostname)) {
            return;
        }
        const link = document.createElement('a');
        link.href = url.href;
        if (title) {
            link.target = title.target;
            link.rel = title.rel;
        }
        link.append(...channel.childNodes);
        channel.append(link);
    }

    function initYouTubeBlocks() {
        onVisible(
            document.querySelectorAll('.km-thumbnail[data-km-youtube-id]'),
            enrichYouTubeBlock,
        );
    }

    function isSafari() {
        return /^((?!chrome|chromium|android|crios|fxios).)*safari/i
            .test(navigator.userAgent);
    }

    function initYouTubeFacades() {
        document.querySelectorAll('[data-km-facade]').forEach((facade) => {
            facade.addEventListener('click', (event) => {
                if (isModifiedClick(event)) return;
                event.preventDefault();
                const url = new URL(
                    facade.getAttribute('data-km-facade-src'),
                    window.location.href,
                );
                url.searchParams.set('autoplay', '1');
                if (isSafari()) url.searchParams.set('mute', '1');
                const frame = document.createElement('iframe');
                frame.className = 'km-media__iframe';
                frame.src = url.href;
                frame.title = facade.getAttribute('data-km-facade-title') || '';
                frame.allow = facade.getAttribute('data-km-facade-allow') || '';
                frame.referrerPolicy = facade
                    .getAttribute('data-km-facade-referrer') || '';
                frame.allowFullscreen = true;
                facade.replaceWith(frame);
                frame.focus();
            });
        });
    }

    function initVideoFlags() {
        document.querySelectorAll('.km-media--video video').forEach((video) => {
            const frame = video.closest('.km-media__frame');
            const sync = () => frame.classList.toggle(
                'km-media__frame--paused',
                video.paused,
            );
            ['play', 'pause', 'ended', 'loadedmetadata'].forEach((name) => {
                video.addEventListener(name, sync, { passive: true });
            });
            sync();
        });
    }

    function initVideoAutoplay() {
        const held = new WeakSet();
        const watcher = new IntersectionObserver((entries) => {
            entries.forEach(({ target, isIntersecting }) => {
                if (isIntersecting) {
                    if (held.delete(target)) target.play().catch(() => {});
                } else if (!target.paused) {
                    held.add(target);
                    target.pause();
                }
            });
        });
        document.querySelectorAll(
            '.km-media--video video[autoplay]',
        ).forEach((video) => {
            watcher.observe(video);
        });
    }

    const {
        initShowMore,
        initAccordions,
        initSearchHighlights,
        initRepositoryWidgets,
        initTickers,
        initRotators,
        initInkReveal,
        initTranscripts,
        initPageReveal,
        initBylineBackground,
    } = window.Kaamiki;
    Object.freeze(window.Kaamiki);
    for (const init of [
        initHeaderHeight,
        initKeyboardModality,
        initLogoInvert,
        initNavFit,
        initSidebar,
        initScrollTop,
        initTabSets,
        initCarousels,
        initRelatedPictures,
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
        initAccordions,
        initHighlightedLines,
        initCopyButtonNames,
        initScrollable,
        initScrollFades,
        initBreadcrumbs,
        initBylineFit,
        initColumnFit,
        initYouTubeBlocks,
        initYouTubeFacades,
        initVideoFlags,
        initVideoAutoplay,
        initRepositoryWidgets,
        initTickers,
        initRotators,
        initInkReveal,
        initTranscripts,
        initPageReveal,
        initBylineBackground,
        initSearchHighlights,
    ]) {
        try {
            init();
        } catch (error) {
            console.error(error);
        }
    }
})();
