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
    const ACCORDION_PX_FACTOR = 0.9;
    const ARTICLE_BG_INTERVAL_MS = 7000;
    const TICKER_CELLS = 11;
    const TICKER_BLUR_PX = 2;
    const ROTATE_STEP_IN_MS = 25;
    const ROTATE_STEP_OUT_MS = 15;
    const ROTATE_SHIFT = '0.25em';
    const ROTATE_BLUR = CSS.supports('hanging-punctuation', 'first') ? 'none' : 'blur(4px)';
    const ROTATE_JOINED = /[\p{Script=Devanagari}\p{Script=Bengali}\p{Script=Gurmukhi}\p{Script=Gujarati}\p{Script=Oriya}\p{Script=Tamil}\p{Script=Telugu}\p{Script=Kannada}\p{Script=Malayalam}\p{Script=Sinhala}\p{Script=Thai}\p{Script=Lao}\p{Script=Khmer}\p{Script=Myanmar}\p{Script=Tibetan}]/u;
    const ROTATE_STAGGER_MAX_MS = 400;
    const REVEAL_STEPS = 6;
    const REVEAL_SLACK_MS = 8;
    const SPEECH_WORD_MS = 170;
    const SPEECH_CHAR_MS = 14;
    const SPEECH_COMMA_MS = 260;
    const SPEECH_STOP_MS = 480;
    const SPEECH_MAX_MS = 9000;
    const SPEECH_GAP_WORDS = 5;
    const SPEECH_FIX_WORDS = 3;
    const SOUND_ALIKES = new Map(Object.entries({
        'your': "you're", "you're": 'your', 'their': 'there', 'there': 'their', "they're": 'there',
        'to': 'two', 'too': 'to', 'two': 'to', 'for': 'four', 'four': 'for', 'no': 'know', 'know': 'no',
        'knew': 'new', 'new': 'knew', 'write': 'right', 'right': 'write', 'one': 'won', 'won': 'one',
        'would': 'wood', 'hear': 'here', 'here': 'hear', 'by': 'buy', 'buy': 'by', 'be': 'bee',
        'see': 'sea', 'sea': 'see', 'son': 'sun', 'sun': 'son', 'whole': 'hole', 'hole': 'whole',
        'weak': 'week', 'week': 'weak', 'peace': 'piece', 'piece': 'peace', 'break': 'brake',
        'meat': 'meet', 'meet': 'meat', 'which': 'witch', 'way': 'weigh', 'wait': 'weight',
        'where': 'wear', 'wear': 'where', 'weather': 'whether', 'whether': 'weather', 'hour': 'our',
        'our': 'hour', 'its': "it's", "it's": 'its', 'then': 'than', 'than': 'then', 'of': 'off',
        'off': 'of', 'are': 'our', 'were': 'where', "we're": 'were', 'said': 'set', 'man': 'men',
        'men': 'man', 'live': 'leave', 'leave': 'live', 'loved': 'lived', 'lived': 'loved',
        'if': 'is', 'is': 'if', 'me': 'be', 'like': 'light', 'life': 'live', 'walk': 'work',
        'work': 'walk', 'calm': 'come', 'storm': 'store', 'form': 'from', 'from': 'form',
        'through': 'threw', 'threw': 'through', 'teach': 'each', 'learn': 'earn', 'master': 'muster',
        'want': "won't", 'something': 'some thing', 'someone': 'some one', 'will': 'well',
        'well': 'will', 'mind': 'mine', 'mine': 'mind', 'told': 'toll', 'feel': 'fill',
        'dream': 'cream', 'time': 'thyme', 'forward': 'foreword', 'moving': 'mooing',
    }));

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
        let whole = false;
        let gliding = 0;

        const tail = () => button.getBoundingClientRect().height + showMoreDock();

        const fit = () => {
            const top = window.scrollY + content.getBoundingClientRect().top;
            const room = Math.round(Math.max(CLAMP_MIN_PX, stableHeight() - top - tail()));
            page.style.setProperty('--km-show-more-clamp', `${room}px`);
            return { top, room };
        };

        let folded = true;
        const fold = (next) => {
            page.classList.toggle('km-page--clamped', next);
            if (next === folded) return;
            folded = next;
            document.dispatchEvent(new Event('km:fold'));
        };

        const measure = () => {
            content.style.maxHeight = '';
            page.classList.remove('km-page--clamped');
            const full = content.getBoundingClientRect().height;
            page.classList.add('km-page--clamped');
            return full;
        };

        const judge = (first = false) => {
            if (gliding || page.classList.contains('km-page--clamping')) return;
            shell.hidden = false;
            const { top, room } = fit();
            const full = page.classList.contains('km-page--clamped')
                ? measure()
                : content.getBoundingClientRect().height;
            const more = full - room >= CLAMP_SLACK_PX;
            const reading = window.scrollY + viewportHeight() > top + room + tail() + 1;
            if (more && whole && !first && !expanded && reading) {
                shell.hidden = true;
                return;
            }
            whole = !more;
            shell.hidden = whole;
            fold(more && !expanded);
        };

        const refit = rafThrottle(() => judge());

        const motion = foldMotion(page, content, 'km-page--clamped', 'km-page--clamping', (next) => {
            fold(next);
            refit();
        });

        judge(true);

        const { stir, rest } = idleShell(shell, button, 'km-page__more--idle', () => expanded && !whole);
        let turn = 0;

        const toggle = (next, animate = true) => {
            if (next === expanded || whole) return;
            expanded = next;
            try { history.replaceState({ ...history.state, kmExpanded: next }, ''); } catch {}
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
                const full = measure();
                page.classList.remove('km-page--clamped');
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
            gliding += 1;
            keepInView(content, collapsed, tail()).then(() => {
                gliding -= 1;
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
            if (expanded || whole) return;
            const link = event.target.closest?.('a[href]');
            if (!link || !holds(link.getAttribute('href') || '')) return;
            toggle(true, false);
        }, true);

        window.addEventListener('hashchange', () => {
            if (expanded || whole || !holds(location.hash)) return;
            toggle(true, false);
            settleHash();
        });

        const buried = (node) => {
            const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
            if (expanded || whole || !element || !content.contains(element)) return false;
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

        window.addEventListener('resize', refit, { passive: true });
        window.addEventListener('load', refit, { once: true });
        new ResizeObserver(refit).observe(document.body);
        document.fonts.ready.then(refit);
        document.fonts.addEventListener?.('loadingdone', refit);

        if (holds(location.hash) || history.state?.kmExpanded) toggle(true, false);
        root.classList.add('km-fold-ready');
        root.classList.remove('km-fold-failed');
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

    function accordionFold(details, summary, content, index) {
        const CLAMPED = 'km-accordion--clamped';
        const CLAMPING = 'km-accordion--clamping';
        const LONG = 'km-accordion--long';
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
            if (!details.open || details.dataset.kmWhole) return;
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
            details.style.setProperty('--km-accordion-clamp', `${limit()}px`);
            if (!expanded) details.classList.add(CLAMPED);
        };

        const soon = rafThrottle(measure);

        const build = () => {
            if (body) return;
            body = document.createElement('div');
            body.className = 'km-accordion__fold';
            body.id = `km-accordion-fold-${index}`;
            body.append(...content.childNodes);
            shell = document.createElement('div');
            shell.className = 'km-accordion__more';
            button = document.createElement('button');
            button.type = 'button';
            button.className = 'km-accordion__more-button';
            button.setAttribute('aria-controls', body.id);
            label = document.createElement('span');
            label.className = 'km-accordion__more-label';
            const icon = document.createElement('i');
            icon.className = `${root.dataset.kmMoreIcon} km-accordion__more-icon`;
            icon.setAttribute('aria-hidden', 'true');
            button.append(label, icon);
            shell.append(button);
            content.append(body, shell);
            name(false);
            motion = foldMotion(details, body, CLAMPED, CLAMPING, (next) => {
                details.classList.toggle(CLAMPED, next);
            });
            idle = idleShell(shell, button, 'km-accordion__more--idle', () => expanded && details.open);
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

    function initAccordions() {
        const easing = getCssVar('--km-spring-smooth');

        const folds = new Map();

        document.querySelectorAll('details.km-accordion').forEach((details, index) => {
            const summary = details.querySelector(':scope > summary');
            const content = details.querySelector(':scope > .km-accordion__body');
            if (!summary || !content) return;
            const fold = accordionFold(details, summary, content, index);
            folds.set(details, fold);

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
                if (opening && details.dataset.kmGroup) {
                    const group = CSS.escape(details.dataset.kmGroup);
                    document.querySelectorAll(`details.km-accordion[data-km-group="${group}"][open]`).forEach((other) => {
                        if (other === details || other.classList.contains('km-is-closing')) return;
                        other.querySelector(':scope > summary')?.click();
                    });
                }
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
                const duration = Math.min(TIMING.accordionMax(), Math.max(
                    TIMING.accordionMin(),
                    Math.abs(end.height - start.height) * ACCORDION_PX_FACTOR,
                ));

                const current = content.animate([frame(start), frame(end)], {
                    duration, easing, fill: 'both',
                });
                animation = current;
                current.finished.then(() => {
                    current.cancel();
                    animation = null;
                    finish(opening);
                }).catch(() => {});
            });

            if (details.open) fold.measure();
        });

        const reveal = (target) => {
            let opened = false;
            for (let host = target; host; host = host.parentElement) {
                if (host.matches('.km-tabs__panel')) {
                    const input = document.getElementById(host.dataset.kmTab);
                    if (input && !input.checked) {
                        input.checked = true;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                        opened = true;
                    }
                    continue;
                }
                if (!host.matches('details.km-accordion') || host.open) continue;
                const group = host.dataset.kmGroup;
                if (group) {
                    document.querySelectorAll(`details.km-accordion[data-km-group="${CSS.escape(group)}"][open]`).forEach((other) => {
                        if (other === host || other.contains(host)) return;
                        other.open = false;
                        folds.get(other)?.reset();
                    });
                }
                host.open = true;
                folds.get(host)?.measure();
                opened = true;
            }
            return opened;
        };
        const fromHash = () => {
            const id = decodeId(location.hash.slice(1));
            const target = id ? document.getElementById(id) : null;
            if (reveal(target)) target.scrollIntoView();
        };

        fromHash();
        window.addEventListener('hashchange', fromHash);
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a[href^="#"]');
            const id = link ? decodeId((link.getAttribute('href') || '').slice(1)) : '';
            if (id) reveal(document.getElementById(id));
        }, true);
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
            if (!Number.isFinite(raw)) return;
            field.closest('p').hidden = false;
            buildTicker(field, formatCount(Math.max(0, Math.trunc(raw))))(TIMING.tickerDuration());
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

    function rotateParts(text) {
        if (ROTATE_JOINED.test(text)) return [text];
        return Array.from(new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(text), (part) => part.segment);
    }

    function rotateLetters(word, text) {
        const letters = rotateParts(text).map((part) => {
            const letter = document.createElement('span');
            letter.className = 'km-rotate__letter';
            letter.textContent = part;
            return letter;
        });
        word.replaceChildren(...letters);
        return letters;
    }

    function playLetters(letters, entering) {
        const rest = { opacity: 1, filter: 'none', transform: 'none' };
        const away = {
            opacity: 0,
            filter: ROTATE_BLUR,
            transform: `translateY(${entering ? '' : '-'}${ROTATE_SHIFT})`,
        };
        const step = Math.min(entering ? ROTATE_STEP_IN_MS : ROTATE_STEP_OUT_MS, ROTATE_STAGGER_MAX_MS / letters.length);
        return letters.map((letter, index) => letter.animate(entering ? [away, rest] : [rest, away], {
            duration: TIMING.fast(),
            delay: (entering ? index : letters.length - 1 - index) * step,
            easing: getCssVar('--km-ease-expo'),
            fill: 'both',
        }));
    }

    function wordWidth(field) {
        const range = document.createRange();
        range.selectNodeContents(field);
        return range.getBoundingClientRect().width;
    }

    async function swapWord(field, current, next) {
        const from = wordWidth(field);
        const stage = document.createElement('span');
        stage.className = 'km-rotate__stage';
        stage.setAttribute('aria-hidden', 'true');
        const word = document.createElement('span');
        stage.appendChild(word);
        stage.style.width = `${from}px`;
        field.replaceChildren(stage);
        const leaving = playLetters(rotateLetters(word, current), false);
        await Promise.all(leaving.map((animation) => animation.finished));
        stage.style.width = '';
        word.textContent = next;
        const to = stage.getBoundingClientRect().width;
        const entering = playLetters(rotateLetters(word, next), true);
        const resize = stage.animate([{ width: `${from}px` }, { width: `${to}px` }], {
            duration: TIMING.rotateResize(),
            easing: getCssVar('--km-ease-expo'),
            fill: 'forwards',
        });
        await Promise.all([...entering, resize].map((animation) => animation.finished));
        field.textContent = next;
    }

    function buildRotator(field) {
        const words = field.dataset.kmWords.split('|');
        let index = 0;
        let busy = false;
        let timer;
        const advance = async () => {
            if (busy || document.hidden) return;
            busy = true;
            const current = words[index];
            index = (index + 1) % words.length;
            try {
                await swapWord(field, current, words[index]);
            } catch {
                field.textContent = words[index];
            }
            busy = false;
        };
        new IntersectionObserver((entries) => {
            clearInterval(timer);
            if (entries[entries.length - 1].isIntersecting) timer = setInterval(advance, TIMING.rotateHold());
        }).observe(field.parentElement);
    }

    function initRotators() {
        if (prefersReducedMotion()) return;
        document.querySelectorAll('.km-rotate[data-km-words]').forEach((field) => {
            if (!field.closest('a')) buildRotator(field);
        });
    }

    function initInkReveal() {
        onVisible(
            document.querySelectorAll('.km-sharpie, .km-pencil'),
            (element) => element.classList.add('km-is-visible'),
            { threshold: 0.1 },
        );
    }

    function spokenForm(text) {
        return text.replace(/^\W+|\W+$/g, '').toLowerCase().replace(/[\u2018\u2019]/g, "'");
    }

    function soundAlike(text) {
        const [, lead, core, trail] = text.match(/^(\W*)(.*?)(\W*)$/);
        const guess = SOUND_ALIKES.get(spokenForm(text));
        if (!guess) return null;
        const cased = core[0] === core[0].toUpperCase() ? guess[0].toUpperCase() + guess.slice(1) : guess;
        return lead + cased + trail;
    }

    function transcribe(quote) {
        const spoken = quote.querySelector('p');
        if (!spoken) return;
        const nodes = [];
        const walker = document.createTreeWalker(spoken, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) nodes.push(walker.currentNode);

        const words = [];
        nodes.forEach((node) => {
            const parts = node.textContent.split(/(\s+)/);
            node.replaceWith(...parts.map((part) => {
                if (!part.trim()) return part;
                const word = document.createElement('span');
                word.className = 'km-word';
                word.textContent = part;
                words.push(word);
                return word;
            }));
        });

        let at = 0;
        const delays = words.map((word) => {
            const text = word.textContent;
            const start = at;
            at += SPEECH_WORD_MS + SPEECH_CHAR_MS * text.length;
            if (/[,;:]$/.test(text)) at += SPEECH_COMMA_MS;
            else if (/[.!?\u2026\u2014]$/.test(text)) at += SPEECH_STOP_MS;
            return start;
        });
        delays.push(at);

        const guesses = words.map(() => null);
        const taken = [];
        const used = new Set();
        const order = words.map((_, index) => [Math.random(), index]).sort((a, b) => a[0] - b[0]);
        for (const [, index] of order) {
            const word = words[index];
            const key = spokenForm(word.textContent);
            const guess = soundAlike(word.textContent);
            if (!guess || word.closest('a') || used.has(key)) continue;
            if (taken.some((other) => Math.abs(other - index) < SPEECH_GAP_WORDS)) continue;
            guesses[index] = guess;
            used.add(key);
            taken.push(index);
        }

        const scale = Math.min(1, SPEECH_MAX_MS / at);
        const ms = (value) => `${Math.round(value * scale)}ms`;
        words.forEach((word, index) => {
            if (!guesses[index]) {
                word.style.setProperty('--km-delay', ms(delays[index]));
                return;
            }
            const fix = ms(delays[Math.min(index + SPEECH_FIX_WORDS, words.length)]);
            const heard = document.createElement('span');
            const guess = document.createElement('span');
            heard.className = 'km-heard';
            guess.className = 'km-guess';
            guess.setAttribute('aria-hidden', 'true');
            guess.textContent = guesses[index];
            guess.style.setProperty('--km-delay', ms(delays[index]));
            guess.style.setProperty('--km-fix', fix);
            word.style.setProperty('--km-delay', fix);
            guess.addEventListener('animationstart', (event) => {
                if (event.animationName !== 'km-guess-out') return;
                const from = heard.getBoundingClientRect().width;
                const to = word.getBoundingClientRect().width;
                const close = heard.animate(
                    [{ width: `${from}px` }, { width: `${to}px` }],
                    { duration: TIMING.fast(), easing: getCssVar('--km-spring-smooth'), fill: 'forwards' },
                );
                close.onfinish = () => {
                    guess.remove();
                    close.cancel();
                };
            });
            word.replaceWith(heard);
            heard.append(guess, word);
        });
        quote.style.setProperty('--km-transcript-total', ms(at));
        quote.classList.add('km-transcript');
    }

    function initTranscripts() {
        if (prefersReducedMotion()) return;
        const quotes = Array.from(document.querySelectorAll('blockquote.epigraph'));
        quotes.forEach(transcribe);
        onVisible(
            quotes.filter((quote) => quote.classList.contains('km-transcript')),
            (quote) => quote.classList.add('km-is-visible'),
            { rootMargin: '0px 0px -15% 0px' },
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
            document.querySelector('.km-feedback-section'),
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
        initAccordions,
        initRepositoryWidgets,
        initTickers,
        initRotators,
        initInkReveal,
        initTranscripts,
        initPageReveal,
        initArticleBackground,
    });
})();
