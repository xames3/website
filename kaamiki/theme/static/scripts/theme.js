(() => {
    'use strict';

    const {
        FOCUSABLE,
        TIMING,
        anchorTargetY,
        copyText,
        decodeId,
        fetchJson,
        getDurationMs,
        glideTo,
        headerHeight,
        isModifiedClick,
        layoutTop,
        onVisible,
        prefersReducedMotion,
        rafThrottle,
        ready,
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
    const SIDEBAR_WIDE_PX = 768;
    const SCROLLTOP_AFTER_PX = 200;
    const TOOLTIP_ROOM_PX = 32;

    function initHeaderHeight() {
        const header = document.querySelector('.km-header');
        if (!header) return;
        const fit = () => root.style.setProperty('--km-header-height', `${headerHeight()}px`);
        fit();
        new ResizeObserver(rafThrottle(fit)).observe(header);
    }
    function initKeyboardModality() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Tab' || event.key?.startsWith('Arrow')) root.setAttribute('data-km-keyboard', '');
        }, true);
        document.addEventListener('pointerdown', () => root.removeAttribute('data-km-keyboard'), true);
    }

    function initLogoInvert() {
        const SOLID_RATIO = 0.98;
        const verdicts = new Map();

        const isBlack = (image) => {
            if (!image.naturalWidth) return false;
            const scale = Math.min(1, 64 / Math.max(image.naturalWidth, image.naturalHeight));
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
            canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
            const context = canvas.getContext('2d', { willReadFrequently: true });
            context.drawImage(image, 0, 0, canvas.width, canvas.height);
            const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
            let opaque = 0;
            let black = 0;
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] < 32) continue;
                opaque += 1;
                if (Math.max(data[i], data[i + 1], data[i + 2]) < 64) black += 1;
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
            try { history.pushState(history.state, '', `#${id}`); } catch {}
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
        link.classList.toggle('km-tooltip-below', text.top - frame.top < TOOLTIP_ROOM_PX);
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
        document.querySelectorAll('.km-tabs').forEach((set) => {
            const tabs = Array.from(set.querySelectorAll(':scope > input'), (input) => {
                const label = input.nextElementSibling;
                return [input, label, label?.nextElementSibling];
            });
            const shaped = ([, label, panel]) => label?.matches('label') && panel?.matches('.km-tabs__panel');
            if (!tabs.length || !tabs.every(shaped)) return;
            const bar = document.createElement('div');
            bar.className = ['km-tabs__bar', set.dataset.kmBar].filter(Boolean).join(' ');
            set.prepend(bar);
            bars.push(bar);
            tabs.forEach(([input, label, panel]) => {
                bar.append(input, label);
                panels.set(input, panel);
            });
        });
        if (!bars.length) return;

        const kept = (group) => `km:tabs:${group}`;
        const group = (input) => input.closest('.km-tabs')?.dataset.kmGroup;
        const choose = (set, key) => {
            const input = Array.from(set.querySelectorAll('input[data-km-key]')).find((_) => _.dataset.kmKey === key);
            if (input && !input.checked) input.checked = true;
        };
        const linked = location.hash.length > 1
            ? document.getElementById(decodeId(location.hash.slice(1)))
            : null;
        document.querySelectorAll('.km-tabs[data-km-group]').forEach((set) => {
            if (linked && set.contains(linked)) return;
            let key = null;
            try { key = localStorage.getItem(kept(set.dataset.kmGroup)); } catch {}
            if (key) choose(set, key);
        });

        const mark = () => panels.forEach((panel, input) => {
            panel.classList.toggle('km-is-current', input.checked);
        });
        const place = (bar, slide) => {
            const label = bar.querySelector(':scope > input:checked + label');
            if (!label) return;
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            bar.classList.toggle('km-is-sliding', slide && !bar.closest('.km-tabs--still'));
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
        document.addEventListener('keydown', (event) => {
            if (!panels.has(event.target) || (event.key !== 'Home' && event.key !== 'End')) return;
            const inputs = Array.from(event.target.closest('.km-tabs__bar').querySelectorAll(':scope > input'));
            const to = event.key === 'Home' ? inputs[0] : inputs[inputs.length - 1];
            event.preventDefault();
            to.checked = true;
            to.focus();
            to.dispatchEvent(new Event('change', { bubbles: true }));
        });
        document.addEventListener('change', (event) => {
            if (!panels.has(event.target)) return;
            const named = group(event.target);
            if (named) {
                try { localStorage.setItem(kept(named), event.target.dataset.kmKey); } catch {}
                document.querySelectorAll(`.km-tabs[data-km-group="${CSS.escape(named)}"]`).forEach((set) => {
                    if (!set.contains(event.target)) choose(set, event.target.dataset.kmKey);
                });
            }
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

        // NOTE(xames3): One dropdown is open at a time and `km-is-open` is
        // the only thing that shows it, so the pointer, the keyboard and the
        // timers can't disagree. A pointer that rests on the seam between two
        // triggers crosses it again and again, so a menu only gives way to the
        // next once the pointer has settled there, and a pointer that comes
        // back first leaves things as they were. One on its way down into the
        // open dropdown is let through, even over the triggers beside it.
        let uid = 0;
        let current = null;
        let timer = 0;
        const trail = [];
        const track = (event) => {
            const now = performance.now();
            trail.push({ x: event.clientX, y: event.clientY, at: now });
            while (trail.length > 1 && now - trail[0].at > DROPDOWN_AIM_WINDOW_MS) trail.shift();
        };
        const aimed = () => {
            const to = trail[trail.length - 1];
            if (!current || !to || performance.now() - to.at > DROPDOWN_AIM_WINDOW_MS) return false;
            const box = current.list.getBoundingClientRect();
            if (to.y >= box.top) return false;
            if (trail.length < 2) return to.x >= box.left && to.x <= box.right;
            const from = trail[0];
            if (to.y <= from.y) return false;
            const side = (a, b, c) => (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y);
            const left = { x: box.left, y: box.top };
            const right = { x: box.right, y: box.top };
            const signs = [side(to, left, from), side(to, right, left), side(to, from, right)];
            return signs.every((sign) => sign >= 0) || signs.every((sign) => sign <= 0);
        };

        const place = ({ group, list }) => {
            group.style.setProperty('--km-dropdown-shift', '0px');
            const drop = Math.max(0, nav.getBoundingClientRect().bottom - group.getBoundingClientRect().bottom);
            const wrapped = drop > 1;
            const box = list.getBoundingClientRect();
            const room = document.documentElement.clientWidth - DROPDOWN_EDGE_PX;
            const left = Math.max(DROPDOWN_EDGE_PX - box.left, Math.min(0, room - box.right));
            group.style.setProperty('--km-dropdown-drop', `${wrapped ? drop : 0}px`);
            group.style.setProperty('--km-dropdown-shift', `${left}px`);
            group.dataset.kmWrapped = wrapped ? 'true' : '';
        };
        const hide = () => {
            clearTimeout(timer);
            if (!current) return;
            current.group.classList.remove('km-is-open');
            current.trigger.setAttribute('aria-expanded', 'false');
            current = null;
            document.removeEventListener('mousemove', track);
            trail.length = 0;
        };
        const show = (menu) => {
            clearTimeout(timer);
            if (current === menu) return;
            hide();
            menu.group.classList.add('km-is-open');
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
            list.id = list.id || `km-nav-group-${++uid}`;
            if (!isLink) {
                trigger.setAttribute('tabindex', '0');
                trigger.setAttribute('role', 'button');
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
                    const until = performance.now() + DROPDOWN_SWITCH_DELAY_MS + DROPDOWN_AIM_MS;
                    const attempt = () => {
                        if (aimed() && performance.now() < until) later(attempt, DROPDOWN_AIM_STEP_MS);
                        else show(menu);
                    };
                    later(attempt, DROPDOWN_SWITCH_DELAY_MS);
                }
            }, { passive: true });
            group.addEventListener('mouseleave', () => {
                if (group.querySelector(':focus-visible')) return;
                const delay = group.dataset.kmWrapped ? DROPDOWN_WRAPPED_CLOSE_DELAY_MS : DROPDOWN_CLOSE_DELAY_MS;
                const until = performance.now() + delay + DROPDOWN_AIM_MS;
                const attempt = () => {
                    if (aimed() && performance.now() < until) later(attempt, DROPDOWN_AIM_STEP_MS);
                    else hide();
                };
                later(attempt, delay);
            }, { passive: true });
            group.addEventListener('focusout', (event) => {
                if (current === menu && !group.contains(event.relatedTarget)) hide();
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
            if (node.tagName === 'UL') node.classList.add('km-header__nav-links');
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
        if (!id || block.hasAttribute('data-km-private')) return;
        const title = block.hasAttribute('data-km-youtube-title')
            ? null
            : block.querySelector('.km-youtube-block__title');
        const channel = block.hasAttribute('data-km-youtube-channel')
            ? null
            : block.querySelector('.km-youtube-block__channel');
        if (!title && !channel) return;

        const watch = encodeURIComponent(`https://www.youtube.com/watch?v=${id}`);
        fetchJson(`https://www.youtube.com/oembed?url=${watch}&format=json`).then((data) => {
            if (!data) return;
            if (title && data.title) title.textContent = data.title;
            if (channel && data.author_name) channel.textContent = data.author_name;
        });
    }

    function initYouTubeBlocks() {
        onVisible(
            document.querySelectorAll('.km-youtube-block[data-km-youtube-id]'),
            enrichYouTubeBlock,
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

    function initVideoFlags() {
        document.querySelectorAll('.km-media--video video').forEach((video) => {
            const frame = video.closest('.km-media__frame');
            const sync = () => frame.classList.toggle('km-is-paused', video.paused);
            ['play', 'pause', 'ended', 'loadedmetadata'].forEach((name) => {
                video.addEventListener(name, sync, { passive: true });
            });
            sync();
        });
    }

    ready(() => {
        const {
            initShowMore,
            initAccordions,
            initRepositoryWidgets,
            initTickers,
            initRotators,
            initInkReveal,
            initTranscripts,
            initPageReveal,
            initArticleBackground,
        } = window.Kaamiki;
        Object.freeze(window.Kaamiki);
        for (const init of [
            initHeaderHeight,
            initKeyboardModality,
            initLogoInvert,
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
            initAccordions,
            initHighlightedLines,
            initCopyButtonNames,
            initScrollable,
            initYouTubeBlocks,
            initYouTubeFacades,
            initVideoFlags,
            initRepositoryWidgets,
            initTickers,
            initRotators,
            initInkReveal,
            initTranscripts,
            initPageReveal,
            initArticleBackground,
        ]) {
            try {
                init();
            } catch (error) {
                console.error(error);
            }
        }
    });
})();
