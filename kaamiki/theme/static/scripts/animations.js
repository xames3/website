(() => {
    'use strict';

    const {
        REVEAL_SHOWN,
        REVEAL_WAITING,
        TIMING,
        attempt,
        clamp,
        decodeId,
        fetchJson,
        getCssVar,
        glideTo,
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

    const CLAMP_SLACK_PX = 48;
    const CLAMP_SETTLE_MS = 60;
    const CLAMP_MIN_PX = 320;
    const CLAMP_MIN_SCREEN_PX = 480;
    const HIGHLIGHT_WAIT_MS = 2000;
    const HIDDEN_PARTS = '.km-tabs__panel:not(.km-tabs__panel--current), '
        + 'details.km-accordion:not([open])';
    const CLAMP_ACCORDION_MIN_PX = 80;
    const ACCORDION_PX_FACTOR = 0.9;
    const BYLINE_BG_INTERVAL_MS = 7000;
    const BYLINE_BG_HIDDEN = '0.001';
    const TICKER_CELLS = 11;
    const TICKER_BLUR_PX = 2;
    const STAT_SHIFT = '0.5em';
    const ROTATE_STEP_IN_MS = 25;
    const ROTATE_STEP_OUT_MS = 8;
    const ROTATE_LAG_MS = 200;
    const ROTATE_RESIZE_LAG_MS = 100;
    const ROTATE_SETTLE_MS = 80;
    const ROTATE_SHIFT = '0.25em';
    // https://developer.mozilla.org/en-US/docs/Web/CSS/hanging-punctuation#browser_compatibility
    const SAFARI = CSS.supports('hanging-punctuation', 'first');
    const ROTATE_BLUR = SAFARI ? 'none' : 'blur(4px)';
    const ROTATE_CLASS = [
        'Devanagari', 'Bengali', 'Gurmukhi', 'Gujarati', 'Oriya', 'Tamil',
        'Telugu', 'Kannada', 'Malayalam', 'Sinhala', 'Thai', 'Lao', 'Khmer',
        'Myanmar', 'Tibetan',
    ].map((name) => `\\p{Script=${name}}`).join('');
    const ROTATE_JOINED = new RegExp(`[${ROTATE_CLASS}]`, 'u');
    const ROTATE_STAGGER_MAX_MS = 400;
    const REVEAL_STEPS = 6;
    const REVEAL_SLACK_MS = 8;
    const TITLE_ITEM = 'km-title-item';
    const TITLE_STEPS = 4;
    const SPEECH_WORD_MS = 170;
    const SPEECH_CHAR_MS = 14;
    const SPEECH_COMMA_MS = 260;
    const SPEECH_STOP_MS = 480;
    const SPEECH_MAX_MS = 9000;
    const SPEECH_GAP_WORDS = 5;
    const SPEECH_FIX_WORDS = 3;
    const SOUND_ALIKES = new Map(Object.entries({
        'your': "you're", "you're": 'your', 'their': 'there', 'there': 'their',
        "they're": 'there', 'to': 'two', 'too': 'to', 'two': 'to',
        'for': 'four', 'four': 'for', 'no': 'know', 'know': 'no', 'knew': 'new',
        'new': 'knew', 'write': 'right', 'right': 'write', 'one': 'won',
        'won': 'one', 'would': 'wood', 'hear': 'here', 'here': 'hear',
        'by': 'buy', 'buy': 'by', 'be': 'bee', 'see': 'sea', 'sea': 'see',
        'son': 'sun', 'sun': 'son', 'whole': 'hole', 'hole': 'whole',
        'weak': 'week', 'week': 'weak', 'peace': 'piece', 'piece': 'peace',
        'break': 'brake', 'meat': 'meet', 'meet': 'meat', 'which': 'witch',
        'way': 'weigh', 'wait': 'weight', 'where': 'wear', 'wear': 'where',
        'weather': 'whether', 'whether': 'weather', 'hour': 'our',
        'our': 'hour', 'its': "it's", "it's": 'its', 'then': 'than',
        'than': 'then', 'of': 'off', 'off': 'of', 'are': 'our', 'were': 'where',
        "we're": 'were', 'said': 'set', 'man': 'men', 'men': 'man',
        'live': 'leave', 'leave': 'live', 'loved': 'lived', 'lived': 'loved',
        'if': 'is', 'is': 'if', 'me': 'be', 'like': 'light', 'life': 'live',
        'walk': 'work', 'work': 'walk', 'calm': 'come', 'storm': 'store',
        'form': 'from', 'from': 'form', 'through': 'threw', 'threw': 'through',
        'teach': 'each', 'learn': 'earn', 'master': 'muster', 'want': "won't",
        'something': 'some thing', 'someone': 'some one', 'will': 'well',
        'well': 'will', 'mind': 'mine', 'mine': 'mind', 'told': 'toll',
        'feel': 'fill', 'dream': 'cream', 'time': 'thyme',
        'forward': 'foreword', 'moving': 'mooing',
    }));

    function toPx(value) {
        const number = parseFloat(value);
        return value.endsWith('rem')
            ? number * parseFloat(getComputedStyle(root).fontSize)
            : number;
    }

    function viewportHeight() {
        return window.visualViewport?.height || window.innerHeight;
    }

    let stableProbe = null;

    function stableHeight() {
        if (!stableProbe) {
            stableProbe = document.createElement('div');
            stableProbe.style.cssText = 'position: absolute; top: 0; '
                + 'width: 0; height: 100svh; visibility: hidden; '
                + 'pointer-events: none;';
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
        const resize = (next, from, to) => {
            host.classList.toggle(clamped, !next);
            host.classList.add(clamping);
            content.style.maxHeight = `${from}px`;
            void content.offsetHeight;
            content.style.maxHeight = `${to}px`;
            window.clearTimeout(timer);
            timer = window.setTimeout(
                () => settle(next),
                TIMING.clamp() + CLAMP_SETTLE_MS,
            );
        };
        const stop = () => window.clearTimeout(timer);
        return { settle, resize, stop };
    }

    const idleStirs = new Set();
    let idleWired = false;

    function wireIdle() {
        if (idleWired) return;
        idleWired = true;
        for (const type of [
            'pointermove', 'pointerdown', 'keydown', 'touchstart', 'focusin',
        ]) {
            window.addEventListener(
                type,
                () => idleStirs.forEach((stir) => stir()),
                { passive: true },
            );
        }
    }

    function idleShell(shell, button, name, awake) {
        let timer = 0;
        let stirred = 0;

        const riding = () => (
            shell.getBoundingClientRect().bottom
                > viewportHeight() - showMoreDock() - 1
        );

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

        content.querySelectorAll('img[loading="lazy"]').forEach((image) => {
            image.loading = 'eager';
        });

        let expanded = false;
        let whole = false;
        let gliding = 0;

        const tail = () => (
            button.getBoundingClientRect().height + showMoreDock()
        );

        const fit = () => {
            const top = window.scrollY + content.getBoundingClientRect().top;
            const room = Math.round(
                Math.max(CLAMP_MIN_PX, stableHeight() - top - tail()),
            );
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

        const moving = () => content.getAnimations().some((animation) => (
            animation.transitionProperty === 'max-height'
        ));

        const judge = (first = false) => {
            if (gliding || page.classList.contains('km-page--clamping')
                || moving()) return;
            shell.hidden = false;
            const { top, room } = fit();
            const full = page.classList.contains('km-page--clamped')
                ? measure()
                : content.getBoundingClientRect().height;
            const more = stableHeight() >= CLAMP_MIN_SCREEN_PX
                && full - room >= CLAMP_SLACK_PX;
            const reading = window.scrollY + viewportHeight()
                > top + room + tail() + 1;
            if (more && whole && !first && !expanded && reading) {
                shell.hidden = true;
                return;
            }
            whole = !more;
            shell.hidden = whole;
            fold(more && !expanded);
        };

        const refit = rafThrottle(() => judge());

        const motion = foldMotion(
            page,
            content,
            'km-page--clamped',
            'km-page--clamping',
            (next) => {
                fold(next);
                refit();
            },
        );

        judge(true);

        const { stir, rest } = idleShell(
            shell,
            button,
            'km-page__more--idle',
            () => expanded && !whole,
        );
        let turn = 0;

        const toggle = (next, animate = true) => {
            if (next === expanded || whole) return;
            expanded = next;
            attempt(() => history.replaceState(
                { ...history.state, kmExpanded: next },
                '',
            ));
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
                const roomPx = viewportHeight()
                    - content.getBoundingClientRect().top;
                motion.resize(
                    true,
                    start,
                    Math.min(full, Math.max(start, roomPx, viewportHeight())),
                );
                return;
            }
            const clampValue = page.style
                .getPropertyValue('--km-show-more-clamp');
            const collapsed = Math.min(start, toPx(clampValue));
            if (!animate || prefersReducedMotion()) {
                keepInView(content, collapsed, tail());
                motion.settle(false);
                return;
            }
            gliding += 1;
            keepInView(content, collapsed, tail()).then(() => {
                gliding -= 1;
                if (current !== turn) return;
                const shown = viewportHeight()
                    - content.getBoundingClientRect().top;
                motion.resize(
                    false,
                    Math.min(start, Math.max(collapsed, shown)),
                    collapsed,
                );
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
            const element = node?.nodeType === Node.ELEMENT_NODE
                ? node
                : node?.parentElement;
            if (expanded || whole || !element
                || !content.contains(element)) return false;
            return element.getBoundingClientRect().bottom
                > shell.getBoundingClientRect().top;
        };

        document.addEventListener('focusin', (event) => {
            if (buried(event.target)) toggle(true, false);
        });

        document.addEventListener('selectionchange', () => {
            const selection = document.getSelection();
            if (selection && !selection.isCollapsed
                && buried(selection.focusNode)) {
                toggle(true, false);
            }
        });

        document.addEventListener('km:match', (event) => {
            if (buried(event.target)) toggle(true, false);
        });

        window.addEventListener('resize', refit, { passive: true });
        window.addEventListener('load', refit, { once: true });
        new ResizeObserver(refit).observe(document.body);
        document.fonts.ready.then(refit);
        document.fonts.addEventListener?.('loadingdone', refit);

        if (holds(location.hash)
            || history.state?.kmExpanded) toggle(true, false);
        root.classList.add('km-document--fold-ready');
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
            const chrome = body
                ? details.getBoundingClientRect().height
                    - body.getBoundingClientRect().height
                : summary.getBoundingClientRect().height
                    + parseFloat(style.paddingTop)
                    + parseFloat(style.paddingBottom) + tail();
            return Math.max(
                CLAMP_ACCORDION_MIN_PX,
                Math.round(stableHeight() - headerHeight() - chrome),
            );
        };

        const full = () => {
            if (!body) {
                const style = getComputedStyle(content);
                return content.getBoundingClientRect().height
                    - parseFloat(style.paddingTop)
                    - parseFloat(style.paddingBottom);
            }
            const bottoms = Array.from(
                body.children,
                (_) => _.getBoundingClientRect().bottom,
            );
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
                const room = viewportHeight()
                    - body.getBoundingClientRect().top;
                motion.resize(
                    true,
                    start,
                    Math.min(height, Math.max(start, room, viewportHeight())),
                );
                return;
            }
            const collapsed = Math.min(start, limit());
            const keep = () => (
                keepInView(body, collapsed, tail() + showMoreDock())
            );
            if (!animate || prefersReducedMotion()) {
                keep();
                motion.settle(false);
                return;
            }
            keep().then(() => {
                if (current !== turn) return;
                const shown = viewportHeight()
                    - body.getBoundingClientRect().top;
                motion.resize(
                    false,
                    Math.min(start, Math.max(collapsed, shown)),
                    collapsed,
                );
            });
        };

        const measure = () => {
            if (!details.open || details.dataset.kmWhole) return;
            if (details.classList.contains('km-accordion--animating')
                || details.classList.contains(CLAMPING)) return;
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
            icon.className = `${root.dataset.kmMoreIcon} `
                + 'km-accordion__more-icon';
            icon.setAttribute('aria-hidden', 'true');
            button.append(label, icon);
            shell.append(button);
            content.append(body, shell);
            name(false);
            motion = foldMotion(details, body, CLAMPED, CLAMPING, (next) => {
                details.classList.toggle(CLAMPED, next);
            });
            idle = idleShell(
                shell,
                button,
                'km-accordion__more--idle',
                () => expanded && details.open,
            );
            button.addEventListener('click', () => toggle(!expanded));
            const reach = (event) => {
                if (expanded || !details.classList.contains(CLAMPED)) return;
                if (event.target.getBoundingClientRect().bottom
                    > shell.getBoundingClientRect().top) {
                    toggle(true, false);
                }
            };
            body.addEventListener('focusin', reach);
            body.addEventListener('km:match', reach);
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

    function groupRivals(details) {
        const group = details.dataset.kmGroup;
        if (!group) return [];
        const open = document.querySelectorAll(
            `details.km-accordion[data-km-group="${CSS.escape(group)}"][open]`,
        );
        return Array.from(open).filter((other) => (
            !other.contains(details) && !details.contains(other)
        ));
    }

    const accordionFolds = new Map();

    function revealHidden(target) {
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
            groupRivals(host).forEach((other) => {
                other.open = false;
                accordionFolds.get(other)?.reset();
            });
            host.open = true;
            accordionFolds.get(host)?.measure();
            opened = true;
        }
        return opened;
    }

    function initAccordions() {
        const easing = getCssVar('--km-ease-swift');

        const accordions = document.querySelectorAll('details.km-accordion');
        accordions.forEach((details, index) => {
            const summary = details.querySelector(':scope > summary');
            const content = details
                .querySelector(':scope > .km-accordion__body');
            if (!summary || !content) return;
            const fold = accordionFold(details, summary, content, index);
            accordionFolds.set(details, fold);

            let animation = null;
            let wanted = details.open;

            const finish = (opening) => {
                details.classList.remove(
                    'km-accordion--animating',
                    'km-accordion--closing',
                );
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
                if (opening) {
                    groupRivals(details).forEach((other) => {
                        if (other.classList.contains(
                            'km-accordion--closing',
                        )) return;
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
                details.classList.toggle('km-accordion--closing', !opening);
                if (opening && !details.open) {
                    details.open = true;
                    fold.measure();
                }
                if (prefersReducedMotion()) {
                    finish(opening);
                    return;
                }

                details.classList.add('km-accordion--animating');
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
                    ? {
                        height: Math.min(
                            box.height,
                            Math.max(room, viewportHeight(), start.height),
                        ),
                        top,
                        bottom,
                        opacity: 1,
                    }
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

        const fromHash = () => {
            const id = decodeId(location.hash.slice(1));
            const target = id ? document.getElementById(id) : null;
            if (revealHidden(target)) target.scrollIntoView();
        };

        fromHash();
        window.addEventListener('hashchange', fromHash);
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a[href^="#"]');
            const id = link
                ? decodeId((link.getAttribute('href') || '').slice(1))
                : '';
            if (id) revealHidden(document.getElementById(id));
        }, true);
    }

    function initSearchHighlights() {
        if (!new URLSearchParams(location.search).get('highlight')) return;
        const shown = (mark) => (
            !mark.closest(HIDDEN_PARTS) && mark.getClientRects().length > 0
        );
        const watch = new MutationObserver(() => {
            const marks = Array.from(document.querySelectorAll(
                '.km-page__content span.highlighted',
            ));
            if (!marks.length) return;
            watch.disconnect();
            const first = marks.find(shown)
                || marks.find((mark) => revealHidden(mark));
            if (!first) return;
            first.dispatchEvent(new Event('km:match', { bubbles: true }));
            const centre = () => first.scrollIntoView({
                block: 'center',
                behavior: 'instant',
            });
            centre();
            const at = window.scrollY;
            document.fonts.ready.then(() => {
                if (window.scrollY === at) centre();
            });
        });
        watch.observe(document.body, { childList: true, subtree: true });
        window.setTimeout(() => watch.disconnect(), HIGHLIGHT_WAIT_MS);
    }

    function formatCount(value) {
        if (value < 1000) return String(value);
        const units = [[1e9, 'b'], [1e6, 'm'], [1e3, 'k']];
        let at = units.findIndex(([each]) => value >= each);
        const tenthsOf = (unit) => Math.floor((value * 10 + unit / 2) / unit);
        if (at > 0 && tenthsOf(units[at][0]) >= 10000) at -= 1;
        const [size, suffix] = units[at];
        const tenths = tenthsOf(size);
        return `${Math.floor(tenths / 10)}.${tenths % 10}`
            .replace(/\.0$/, '') + suffix;
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
        digit.classList.toggle('km-ticker__digit--shown', shown);
        const reel = document.createElement('span');
        reel.className = 'km-ticker__reel';
        for (let i = 0; i < TICKER_CELLS; i += 1) {
            const cell = document.createElement('span');
            cell.className = 'km-ticker__cell';
            cell.textContent = String(i % 10);
            reel.appendChild(cell);
        }
        digit.appendChild(reel);
        return { digit, reel, place, shown, travel, position: 0 };
    }

    function turnTickerWheel(wheel, value, progress, landed) {
        if (!wheel.shown && value >= 10 ** wheel.place) {
            wheel.shown = true;
            wheel.digit.classList.add('km-ticker__digit--shown');
        }
        const position = (wheel.travel * progress) % 10;
        const blur = landed
            ? 0
            : Math.min(TICKER_BLUR_PX, (position - wheel.position + 10) % 10);
        const lift = (position / TICKER_CELLS) * 100;
        wheel.reel.style.transform = `translateY(-${lift}%)`;
        wheel.reel.style.filter = blur > 0.05
            ? `blur(${blur.toFixed(2)}px)`
            : '';
        wheel.position = position;
    }

    function reserveTickerWidths(items) {
        if (!items.length) return;
        const marked = items.map(({ ticker }) => {
            const digits = Array.from(
                ticker.querySelectorAll('.km-ticker__digit'),
            );
            const shown = digits.map((digit) => (
                digit.classList.contains('km-ticker__digit--shown')
            ));
            ticker.classList.add('km-ticker__wheels--measuring');
            digits.forEach((digit) => (
                digit.classList.add('km-ticker__digit--shown')
            ));
            return { digits, shown };
        });
        const widths = items.map(({ ticker }) => (
            ticker.getBoundingClientRect().width
        ));
        marked.forEach(({ digits, shown }) => {
            digits.forEach((digit, index) => digit.classList.toggle(
                'km-ticker__digit--shown',
                shown[index],
            ));
        });
        items[0].ticker.getBoundingClientRect();
        items.forEach(({ ticker }) => (
            ticker.classList.remove('km-ticker__wheels--measuring')
        ));
        const sizes = items.map(({ field }) => (
            parseFloat(getComputedStyle(field).fontSize)
        ));
        items.forEach(({ field }, index) => {
            field.style.minWidth = `${widths[index] / sizes[index]}em`;
        });
    }

    function makeTicker(field, text) {
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
            const wheel = tickerWheel(
                place,
                reduced || place < (decimal ? 2 : 1),
                travel,
            );
            wheels.push(wheel);
            ticker.appendChild(wheel.digit);
            if (decimal && place === 1) ticker.appendChild(tickerSymbol('.'));
        }
        if (/[kmb]$/.test(text)) {
            ticker.appendChild(tickerSymbol(text.slice(-1)));
        }
        const label = document.createElement('span');
        label.className = 'sr-only';
        label.textContent = text;

        wheels.forEach((wheel) => turnTickerWheel(
            wheel,
            reduced ? target : 0,
            reduced ? 1 : 0,
        ));
        field.replaceChildren(label, ticker);

        const count = (duration) => {
            if (reduced || !target) return;
            const began = performance.now();
            const spring = springProgress();
            const turn = (now) => {
                const time = clamp((now - began) / duration, 0, 1);
                const progress = spring(time);
                wheels.forEach((wheel) => turnTickerWheel(
                    wheel,
                    target * progress,
                    progress,
                    time === 1,
                ));
                if (time < 1) requestAnimationFrame(turn);
            };
            requestAnimationFrame(turn);
        };
        return { ticker, count };
    }

    function buildTicker(field, text) {
        const { ticker, count } = makeTicker(field, text);
        reserveTickerWidths([{ field, ticker }]);
        return count;
    }

    function enterStat(stat, index) {
        stat.animate([
            {
                opacity: 0,
                filter: ROTATE_BLUR,
                transform: `translateY(${STAT_SHIFT})`,
            },
            { opacity: 1, filter: 'none', transform: 'none' },
        ], {
            duration: TIMING.normal(),
            delay: index * (TIMING.fast() / 2),
            easing: getCssVar('--km-ease-expo'),
            fill: 'backwards',
        });
    }

    const repositories = new Map();

    function repositoryData(project) {
        if (!repositories.has(project)) {
            repositories.set(
                project,
                fetchJson(`https://api.github.com/repos/${project}`),
            );
        }
        return repositories.get(project);
    }

    async function loadRepository(widget) {
        const project = widget.getAttribute('data-km-repository');
        const fields = widget.querySelectorAll('[data-km-repository-count]');
        if (!project || !fields.length) return;

        const data = await repositoryData(project) || {};
        let entered = 0;
        fields.forEach((field) => {
            const raw = Number(
                data[field.getAttribute('data-km-repository-count')],
            );
            if (!Number.isFinite(raw)) return;
            const stat = field.closest('p');
            stat.hidden = false;
            const count = buildTicker(
                field,
                formatCount(Math.max(0, Math.trunc(raw))),
            );
            count(TIMING.tickerDuration());
            enterStat(stat, entered);
            entered += 1;
        });
    }

    function initRepositoryWidgets() {
        onVisible(
            document.querySelectorAll(
                '.km-repository[data-km-repository]',
            ),
            loadRepository,
            { rootMargin: '0px 0px -10% 0px' },
        );
    }

    function initTickers() {
        const waiting = [];
        const build = () => {
            const batch = waiting.splice(0).map((field) => ({
                field,
                ...makeTicker(field, field.textContent),
            }));
            reserveTickerWidths(batch);
            batch.forEach(({ field, count }) => {
                const duration = parseFloat(
                    field.style.getPropertyValue('--km-ticker-duration'),
                );
                onVisible(
                    [field],
                    () => count(duration),
                    { rootMargin: '0px' },
                );
            });
        };
        onVisible(document.querySelectorAll('.km-ticker'), (field) => {
            waiting.push(field);
            if (waiting.length === 1) queueMicrotask(build);
        });
    }

    function rotateParts(text) {
        if (ROTATE_JOINED.test(text)) return [text];
        return Array.from(
            new Intl.Segmenter(undefined, { granularity: 'grapheme' })
                .segment(text),
            (part) => part.segment,
        );
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

    function rotateLefts(word, text) {
        const node = word.firstChild;
        const range = document.createRange();
        let offset = 0;
        return rotateParts(text).map((part) => {
            range.setStart(node, offset);
            range.setEnd(node, offset += part.length);
            return range.getBoundingClientRect().left;
        });
    }

    function kernLetters(letters, lefts) {
        const natural = letters.map(
            (letter) => letter.getBoundingClientRect().left,
        );
        let shifted = 0;
        letters.forEach((letter, index) => {
            const shift = (lefts[index] - lefts[0])
                - (natural[index] - natural[0]);
            letter.style.marginLeft = `${shift - shifted}px`;
            shifted = shift;
        });
        return letters;
    }

    function playLetters(letters, entering) {
        const rest = { opacity: 1, filter: 'none', transform: 'none' };
        const away = {
            opacity: 0,
            filter: ROTATE_BLUR,
            transform: `translateY(${entering ? '' : '-'}${ROTATE_SHIFT})`,
        };
        const step = Math.min(
            entering ? ROTATE_STEP_IN_MS : ROTATE_STEP_OUT_MS,
            ROTATE_STAGGER_MAX_MS / letters.length,
        );
        return letters.map((letter, index) => letter.animate(
            entering ? [away, rest] : [rest, away],
            {
                duration: TIMING.fast(),
                delay: entering
                    ? ROTATE_LAG_MS + index * step
                    : (letters.length - 1 - index) * step,
                easing: getCssVar(
                    entering ? '--km-ease-expo' : '--km-ease-standard',
                ),
                fill: 'both',
            },
        ));
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
        const leaving = document.createElement('span');
        leaving.className = 'km-rotate__leaving';
        const word = document.createElement('span');
        stage.append(leaving, word);
        field.replaceChildren(stage);
        word.textContent = next;
        const to = stage.getBoundingClientRect().width;
        const lefts = rotateLefts(word, next);
        stage.style.width = `${from}px`;
        const animations = [
            ...playLetters(rotateLetters(leaving, current), false),
            ...playLetters(
                kernLetters(rotateLetters(word, next), lefts),
                true,
            ),
            stage.animate(
                [{ width: `${from}px` }, { width: `${to}px` }],
                {
                    duration: TIMING.rotateResize(),
                    delay: ROTATE_RESIZE_LAG_MS,
                    easing: getCssVar('--km-ease-standard'),
                    fill: 'both',
                },
            ),
        ];
        await Promise.all(animations.map((animation) => animation.finished));
        leaving.replaceChildren(next);
        await leaving.animate(
            [{ opacity: 0 }, { opacity: 1 }],
            { duration: ROTATE_SETTLE_MS },
        ).finished;
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
            if (entries[entries.length - 1].isIntersecting) {
                timer = setInterval(advance, TIMING.rotateHold());
            }
        }).observe(field.parentElement);
    }

    function initRotators() {
        if (prefersReducedMotion()) return;
        document.querySelectorAll('.km-rotate[data-km-words]').forEach(
            (field) => {
                if (!field.closest('a')) buildRotator(field);
            },
        );
    }

    function initInkReveal() {
        ['km-sharpie', 'km-pencil'].forEach((block) => {
            onVisible(
                document.querySelectorAll(`.${block}`),
                (element) => element.classList.add(`${block}--visible`),
                { threshold: 0.1 },
            );
        });
    }

    function spokenForm(text) {
        return text.replace(/^\W+|\W+$/g, '').toLowerCase()
            .replace(/[\u2018\u2019]/g, "'");
    }

    function soundAlike(text) {
        const [, lead, core, trail] = text.match(/^(\W*)(.*?)(\W*)$/);
        const guess = SOUND_ALIKES.get(spokenForm(text));
        if (!guess) return null;
        const cased = core[0] === core[0].toUpperCase()
            ? guess[0].toUpperCase() + guess.slice(1)
            : guess;
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
                word.className = 'km-transcript__word';
                word.textContent = part;
                words.push(word);
                return word;
            }));
        });

        let elapsed = 0;
        const delays = words.map((word) => {
            const text = word.textContent;
            const start = elapsed;
            elapsed += SPEECH_WORD_MS + SPEECH_CHAR_MS * text.length;
            if (/[,;:]$/.test(text)) elapsed += SPEECH_COMMA_MS;
            else if (/[.!?\u2026\u2014]$/.test(text)) elapsed += SPEECH_STOP_MS;
            return start;
        });
        delays.push(elapsed);

        const guesses = words.map(() => null);
        const taken = [];
        const used = new Set();
        const order = Array.from(
            words.keys(),
            (index) => [Math.random(), index],
        ).sort((a, b) => a[0] - b[0]);
        for (const [, index] of order) {
            const word = words[index];
            const key = spokenForm(word.textContent);
            const guess = soundAlike(word.textContent);
            if (!guess || word.closest('a') || used.has(key)) continue;
            if (taken.some((other) => (
                Math.abs(other - index) < SPEECH_GAP_WORDS
            ))) continue;
            guesses[index] = guess;
            used.add(key);
            taken.push(index);
        }

        const scale = Math.min(1, SPEECH_MAX_MS / elapsed);
        const milliseconds = (value) => `${Math.round(value * scale)}ms`;
        words.forEach((word, index) => {
            if (!guesses[index]) {
                word.style.setProperty(
                    '--km-delay',
                    milliseconds(delays[index]),
                );
                return;
            }
            const fix = milliseconds(
                delays[Math.min(index + SPEECH_FIX_WORDS, words.length)],
            );
            const heard = document.createElement('span');
            const guess = document.createElement('span');
            heard.className = 'km-transcript__heard';
            guess.className = 'km-transcript__guess';
            guess.setAttribute('aria-hidden', 'true');
            guess.textContent = guesses[index];
            guess.style.setProperty('--km-delay', milliseconds(delays[index]));
            guess.style.setProperty('--km-fix', fix);
            word.style.setProperty('--km-delay', fix);
            guess.addEventListener('animationstart', (event) => {
                if (event.animationName !== 'km-guess-out') return;
                const from = heard.getBoundingClientRect().width;
                const to = word.getBoundingClientRect().width;
                const close = heard.animate(
                    [{ width: `${from}px` }, { width: `${to}px` }],
                    {
                        duration: TIMING.fast(),
                        easing: getCssVar('--km-spring-smooth'),
                        fill: 'forwards',
                    },
                );
                close.onfinish = () => {
                    guess.remove();
                    close.cancel();
                };
            });
            word.replaceWith(heard);
            heard.append(guess, word);
        });
        quote.style.setProperty('--km-transcript-total', milliseconds(elapsed));
        quote.classList.add('km-transcript');
    }

    function initTranscripts() {
        if (prefersReducedMotion()) return;
        const quotes = Array.from(
            document.querySelectorAll('blockquote.epigraph'),
        );
        quotes.forEach(transcribe);
        onVisible(
            quotes.filter((quote) => quote.classList.contains('km-transcript')),
            (quote) => quote.classList.add('km-transcript--visible'),
            { rootMargin: '0px 0px -15% 0px' },
        );
    }

    function revealBlocks(node) {
        return Array.from(node?.children ?? []).flatMap((child) => (
            child.tagName === 'SECTION' ? revealBlocks(child) : [child]
        ));
    }

    function markTitle() {
        const heading = document.querySelector('#km-content > section > h1');
        if (!heading) return [];
        const items = [
            document.querySelector('.km-header'),
            document.querySelector('.km-breadcrumbs'),
            heading,
            ...Array.from(heading.parentElement.children).filter((child) => (
                child.matches('.km-text--lead, .km-byline')
            )),
        ].filter(Boolean);
        items.forEach((item) => item.classList.add(TITLE_ITEM));
        return items;
    }

    function titleHold() {
        if (!document.querySelector(`.${TITLE_ITEM}`)) return 0;
        return TIMING.titleStep() * TITLE_STEPS;
    }

    function afterLoading(callback) {
        if (!root.classList.contains('km-document--loading')) {
            callback();
            return;
        }
        const watcher = new MutationObserver(() => {
            if (root.classList.contains('km-document--loading')) return;
            watcher.disconnect();
            callback();
        });
        watcher.observe(root, { attributes: true, attributeFilter: ['class'] });
    }

    function initPageReveal() {
        if (prefersReducedMotion()) return;
        const title = new Set(markTitle());
        const blocks = [
            document.querySelector('.km-header'),
            document.querySelector('.km-breadcrumbs'),
            ...revealBlocks(document.getElementById('km-content')),
            document.querySelector('.km-feedback-section'),
            document.querySelector('.km-page__updated'),
            document.querySelector('.km-page__more-button'),
            document.querySelector('.km-pagination'),
            document.querySelector('.km-related'),
            document.querySelector('.km-footer'),
        ].filter((block) => block && !title.has(block));

        const hold = titleHold() && titleHold() + TIMING.revealStep();
        const limit = TIMING.revealStep() * REVEAL_STEPS;
        const duration = TIMING.revealDuration();
        const hurried = new Set();
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
            waiting.forEach((block) => release(block, false));
            waiting = [];
            blocks.forEach((block) => (
                block.classList.remove(REVEAL_WAITING, REVEAL_SHOWN)
            ));
            hurried.forEach((block) => {
                block.style.removeProperty('animation-duration');
                if (!block.getAttribute('style')) {
                    block.removeAttribute('style');
                }
            });
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
            return (box.width > 0 || box.height > 0)
                && box.bottom >= top && box.top < bottom;
        };

        const tick = (now) => {
            if (done) return;
            try {
                if (root.classList.contains('km-document--loading')) {
                    requestAnimationFrame(tick);
                    return;
                }
                if (began === null) {
                    began = now;
                    screen = screenHeight();
                    const clip = edges(Math.max(window.innerHeight, screen));
                    waiting = waiting.filter((block) => {
                        if (inView(block, clip)) return true;
                        release(block, false);
                        return false;
                    });
                }
                if (now - began < hold) {
                    requestAnimationFrame(tick);
                    return;
                }
                const late = now - began - hold >= limit + duration;
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
                    const waitingIndex = waiting.indexOf(block);
                    waiting.slice(0, waitingIndex).forEach((passed) => {
                        const box = passed.getBoundingClientRect();
                        if (box.bottom > 0 && box.top < 2 * fold) {
                            play(passed, now, late);
                        } else release(passed, false);
                    });
                    waiting = waiting.slice(waitingIndex + 1);
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
        requestAnimationFrame(tick);
    }

    function shuffle(list) {
        for (let i = list.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [list[i], list[j]] = [list[j], list[i]];
        }
    }

    function createBackdrop(backdrop, urls) {
        const overlay = document.createElement('div');
        overlay.className = backdrop
            ? 'km-byline__bg'
            : 'km-byline__bg km-byline__bg--waves';
        overlay.setAttribute('aria-hidden', 'true');
        overlay.style.top = '0';
        if (!backdrop) {
            ['a', 'b', 'c'].forEach((name) => {
                const wave = document.createElement('span');
                wave.className = `km-byline__wave km-byline__wave--${name}`;
                overlay.appendChild(wave);
            });
        }
        if (backdrop) overlay.style.backgroundImage = `url("${urls[0]}")`;
        overlay.style.opacity = BYLINE_BG_HIDDEN;
        if (backdrop && urls.length === 1) {
            overlay.style.animationIterationCount = '1';
            overlay.style.animationFillMode = 'forwards';
        }
        return overlay;
    }

    function cycleBackdrop(overlay, urls, byline) {
        const every = Number(byline.getAttribute('data-km-interval'))
            || BYLINE_BG_INTERVAL_MS;
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
            }, TIMING.slow() + 50);
        }, every);
    }

    function initBylineBackground() {
        const byline = document.querySelector('.km-byline');
        const main = document.querySelector('.km-layout__content');
        const page = document.querySelector('.km-page__content');
        if (!main || !page) return;

        const backdrop = !!byline && byline.hasAttribute('data-km-backdrop');
        const urls = backdrop
            ? byline.getAttribute('data-km-backdrop')
                .trim().split(/\s+/).filter(Boolean)
            : [];
        if (backdrop && !urls.length) return;
        const anchor = byline
            || page.querySelector('.km-text--lead')
            || page.querySelector('h1');
        if (!anchor) return;

        shuffle(urls);
        main.style.isolation = 'isolate';
        const overlay = createBackdrop(backdrop, urls);
        main.appendChild(overlay);

        const measure = () => {
            const fontSize = parseFloat(getComputedStyle(root).fontSize) || 16;
            const bottom = anchor.getBoundingClientRect().bottom
                + fontSize * (byline ? -2 : 2);
            const height = bottom - main.getBoundingClientRect().top;
            overlay.style.height = `${Math.max(0, height)}px`;
        };

        measure();
        afterLoading(() => setTimeout(() => {
            requestAnimationFrame(() => requestAnimationFrame(() => {
                overlay.style.opacity = '';
            }));
        }, titleHold()));

        window.addEventListener(
            'resize',
            rafThrottle(measure),
            { passive: true },
        );
        new ResizeObserver(measure).observe(main);
        document.fonts.ready.then(measure);
        anchor.addEventListener('animationend', measure);

        if (!backdrop || urls.length === 1 || prefersReducedMotion()) return;
        cycleBackdrop(overlay, urls, byline);
    }

    function screenHeight() {
        const probe = document.createElement('div');
        probe.style.cssText = 'position: absolute; top: 0; width: 0; '
            + 'height: 100lvh; visibility: hidden;';
        document.body.append(probe);
        const height = probe.getBoundingClientRect().height;
        probe.remove();
        return height || window.innerHeight;
    }

    Object.assign(window.Kaamiki, {
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
    });
})();
