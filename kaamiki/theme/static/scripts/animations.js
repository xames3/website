(() => {
    'use strict';

    const {
        REVEAL_SHOWN,
        REVEAL_WAITING,
        TIMING,
        clamp,
        decodeId,
        fetchJson,
        getCssVar,
        getDurationMs,
        headerHeight,
        isModifiedClick,
        onScroll,
        onVisible,
        prefersReducedMotion,
        rafThrottle,
        say,
        settleHash,
        springProgress,
    } = window.Kaamiki;
    const root = document.documentElement;

    const GLIDE_STOPS = ['wheel', 'touchstart', 'pointerdown', 'keydown'];
    const GLIDE_KEYS = new Set(['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' ']);
    const GLIDE_BASE_MS = 300;
    const GLIDE_PX_FACTOR = 0.1;
    const GLIDE_MIN_MS = 400;
    const GLIDE_MAX_MS = 900;
    const CLAMP_SLACK_PX = 48;
    const CLAMP_SETTLE_MS = 60;
    const CLAMP_MIN_PX = 320;
    const DROPDOWN_PX_FACTOR = 0.9;
    const ARTICLE_BG_INTERVAL_MS = 7000;
    const TICKER_CELLS = 11;
    const TICKER_BLUR_PX = 2;
    const REVEAL_STEPS = 6;
    const REVEAL_SLACK_MS = 8;

    function toPx(value) {
        const number = parseFloat(value);
        return value.endsWith('rem') ? number * parseFloat(getComputedStyle(root).fontSize) : number;
    }

    function viewportHeight() {
        return window.visualViewport?.height || window.innerHeight;
    }

    let stableProbe = null;

    function stableHeight() {
        if (!stableProbe) {
            stableProbe = document.createElement('div');
            stableProbe.style.cssText = 'position: absolute; top: 0; width: 0; height: 100svh; visibility: hidden; pointer-events: none;';
            stableProbe.setAttribute('aria-hidden', 'true');
            document.body.append(stableProbe);
        }
        return stableProbe.offsetHeight || window.innerHeight;
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

    const idleStirs = new Set();
    let idleWired = false;

    function wireIdle() {
        if (idleWired) return;
        idleWired = true;
        for (const type of [
            'pointermove', 'pointerdown', 'keydown', 'touchstart', 'focusin',
        ]) {
            window.addEventListener(type, () => idleStirs.forEach((stir) => stir()), { passive: true });
        }
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

        idleStirs.add(stir);
        wireIdle();
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
            const room = Math.max(CLAMP_MIN_PX, stableHeight() - top - tail());
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

    let glideStop = null;

    function glideTo(targetY) {
        const startY = window.scrollY;
        const endY = clamp(targetY, 0, Math.max(0, root.scrollHeight - window.innerHeight));
        if (Math.abs(endY - startY) < 1) return Promise.resolve(true);
        if (prefersReducedMotion()) {
            window.scrollTo(0, endY);
            return Promise.resolve(true);
        }
        glideStop?.();
        const distance = endY - startY;
        const duration = clamp(GLIDE_BASE_MS + Math.abs(distance) * GLIDE_PX_FACTOR, GLIDE_MIN_MS, GLIDE_MAX_MS);
        const spring = springProgress();
        return new Promise((resolve) => {
            let frame = 0;
            const began = performance.now();
            const finish = (arrived) => {
                cancelAnimationFrame(frame);
                GLIDE_STOPS.forEach((type) => window.removeEventListener(type, stop, true));
                glideStop = null;
                resolve(arrived);
            };
            const stop = (event) => {
                if (event?.type === 'keydown' && !GLIDE_KEYS.has(event.key)) return;
                if (event?.type === 'wheel' && !event.deltaX && !event.deltaY) return;
                finish(false);
            };
            const step = (now) => {
                const time = clamp((now - began) / duration, 0, 1);
                window.scrollTo({ top: startY + distance * spring(time), behavior: 'instant' });
                if (time === 1) finish(true);
                else frame = requestAnimationFrame(step);
            };
            glideStop = stop;
            GLIDE_STOPS.forEach((type) => window.addEventListener(type, stop, { capture: true, passive: true }));
            frame = requestAnimationFrame(step);
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
            const room = stableHeight() - headerHeight()
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
            const bottoms = Array.from(body.children, (_) => _.getBoundingClientRect().bottom);
            return Math.max(0, ...bottoms) - body.getBoundingClientRect().top;
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
        const easing = getCssVar('--km-spring-smooth');

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

    function formatCount(value) {
        return value >= 1000
            ? `${(value / 1000).toFixed(1).replace(/\.0$/, '')}k`
            : String(value);
    }

    function tickerSymbol(character) {
        const symbol = document.createElement('span');
        symbol.className = 'km-ticker__symbol';
        symbol.textContent = character;
        return symbol;
    }

    function tickerWheel(place, shown, travel) {
        const digit = document.createElement('span');
        digit.className = 'km-ticker__digit';
        digit.classList.toggle('km-is-shown', shown);
        const reel = document.createElement('span');
        reel.className = 'km-ticker__reel';
        for (let i = 0; i < TICKER_CELLS; i += 1) {
            const cell = document.createElement('span');
            cell.className = 'km-ticker__cell';
            cell.textContent = String(i % 10);
            reel.appendChild(cell);
        }
        digit.appendChild(reel);
        return { digit, reel, place, shown, travel, at: 0 };
    }

    function turnTickerWheel(wheel, value, progress, landed) {
        if (!wheel.shown && value >= 10 ** wheel.place) {
            wheel.shown = true;
            wheel.digit.classList.add('km-is-shown');
        }
        const at = (wheel.travel * progress) % 10;
        const blur = landed ? 0 : Math.min(TICKER_BLUR_PX, (at - wheel.at + 10) % 10);
        wheel.reel.style.transform = `translateY(-${(at / TICKER_CELLS) * 100}%)`;
        wheel.reel.style.filter = blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : '';
        wheel.at = at;
    }

    function buildTicker(field, text) {
        const decimal = text.includes('.');
        const target = Number(text.replace(/\D/g, ''));
        const places = Math.max(String(target).length, decimal ? 2 : 1);
        const digits = String(target).padStart(places, '0');
        const reduced = prefersReducedMotion();
        const ticker = document.createElement('span');
        ticker.className = 'km-ticker__wheels';
        ticker.setAttribute('aria-hidden', 'true');
        const wheels = [];
        for (let place = places - 1; place >= 0; place -= 1) {
            const index = places - 1 - place;
            const travel = Number(digits[index]) + 10 * index;
            const wheel = tickerWheel(place, reduced || place < (decimal ? 2 : 1), travel);
            wheels.push(wheel);
            ticker.appendChild(wheel.digit);
            if (decimal && place === 1) ticker.appendChild(tickerSymbol('.'));
        }
        if (/[kmb]$/.test(text)) ticker.appendChild(tickerSymbol(text.slice(-1)));
        const label = document.createElement('span');
        label.className = 'sr-only';
        label.textContent = text;

        wheels.forEach((wheel) => turnTickerWheel(wheel, reduced ? target : 0, reduced ? 1 : 0));
        field.replaceChildren(label, ticker);

        return (duration) => {
            if (reduced || !target) return;
            const began = performance.now();
            const spring = springProgress();
            const count = (now) => {
                const time = clamp((now - began) / duration, 0, 1);
                const progress = spring(time);
                wheels.forEach((wheel) => turnTickerWheel(wheel, target * progress, progress, time === 1));
                if (time < 1) requestAnimationFrame(count);
            };
            requestAnimationFrame(count);
        };
    }

    async function loadRepository(widget) {
        const project = widget.getAttribute('data-km-repository');
        const fields = widget.querySelectorAll('[data-km-repository-count]');
        if (!project || !fields.length) return;

        const data = await fetchJson(`https://api.github.com/repos/${project}`) || {};
        fields.forEach((field) => {
            const raw = Number(data[field.getAttribute('data-km-repository-count')]);
            const count = Number.isFinite(raw) ? Math.max(0, Math.trunc(raw)) : 0;
            buildTicker(field, formatCount(count))(TIMING.tickerDuration());
        });
    }

    function initRepositoryWidgets() {
        onVisible(
            document.querySelectorAll('.km-github-repository[data-km-repository]'),
            loadRepository,
            { rootMargin: '0px 0px -10% 0px' },
        );
    }

    function initTickers() {
        document.querySelectorAll('.km-ticker').forEach((field) => {
            const duration = parseFloat(field.style.getPropertyValue('--km-ticker-duration'));
            const count = buildTicker(field, field.textContent);
            onVisible([field], () => count(duration), { rootMargin: '0px 0px -10% 0px' });
        });
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
                    screen = screenHeight();
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

    function screenHeight() {
        const probe = document.createElement('div');
        probe.style.cssText = 'position: absolute; top: 0; width: 0; height: 100lvh; visibility: hidden;';
        document.body.append(probe);
        const height = probe.getBoundingClientRect().height;
        probe.remove();
        return height || window.innerHeight;
    }

    function stopGlide() {
        glideStop?.();
    }

    Object.assign(window.Kaamiki, {
        glideTo,
        stopGlide,
        initShowMore,
        initDropdowns,
        initRepositoryWidgets,
        initTickers,
        initInkReveal,
        initPageReveal,
        initArticleBackground,
    });
})();
