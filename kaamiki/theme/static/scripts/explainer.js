(() => {
    'use strict';

    const {
        TIMING,
        announce,
        clamp,
        copyText,
        headerHeight,
        onScroll,
        prefersReducedMotion,
        rafThrottle,
        say,
        stopGlide,
        codeExplains,
    } = window.Kaamiki;
    const root = document.documentElement;

    const STAGE_MIN_LINES = 6;
    const RESIZE_JITTER_PX = 120;
    const RESIZE_SETTLE_MS = 120;
    const STAGE_MIN_WIDTH_PX = 880;
    const STAGE_PADDING_PX = 16;
    const STAGE_SPACE_SHARE = 0.6;
    const STAGE_MARGIN_PX = 24;
    const REARM_DISTANCE_PX = 120;
    const LOCK_GRACE_MS = 350;
    const HAND_WINDOW_MS = 500;
    const TOUCH_GLIDE_MS = 1500;
    const FOCUS_SCROLL_WINDOW_MS = 300;
    const TRACK_STIFFNESS = 16;
    const STACK_MAX_LINES = 12;
    const DIFF_VISIBLE_SWAPS = 3;
    const ANIMATE_WITHIN_STEPS = 2;
    let held = null;
    let handUntil = 0;
    let wired = false;

    function readPayload(host) {
        return JSON.parse(host.querySelector('[data-km-payload]').textContent);
    }

    function sourceOf(payload) {
        const code = payload.code || '';
        if (!payload.setup) return code;
        const { open = '#', close = '' } = payload.comment || {};
        const head = `${open} ${say('setup')}${close ? ` ${close}` : ''}`;
        return `${head}\n${payload.setup}\n\n${code}`;
    }

    function valueNode(item, opened) {
        const value = document.createElement('span');
        value.className = 'km-code-explain__value';
        if (!item.short) {
            value.textContent = item.full;
            return value;
        }
        const short = document.createElement('span');
        short.className = 'km-code-explain__short';
        short.textContent = item.short;
        const full = document.createElement('span');
        full.className = 'km-code-explain__full';
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

    function entryNode(item, opened) {
        const entry = document.createElement('span');
        entry.className = 'km-code-explain__variable';
        if (item.fresh) entry.setAttribute('data-km-fresh', '');
        if (item.kind) entry.dataset.kmKind = item.kind;
        entry.append(
            item.name ? `${item.name}: ` : `${item.mark} `,
            valueNode(item, opened),
        );
        return entry;
    }

    function diffLines(before, after) {
        const table = Array.from(
            { length: before.length + 1 },
            () => new Uint32Array(after.length + 1),
        );
        for (let row = before.length - 1; row >= 0; row -= 1) {
            for (let column = after.length - 1; column >= 0; column -= 1) {
                table[row][column] = before[row] === after[column]
                    ? table[row + 1][column + 1] + 1
                    : Math.max(table[row + 1][column], table[row][column + 1]);
            }
        }
        const script = [];
        let i = 0;
        let j = 0;
        while (i < before.length || j < after.length) {
            if (i < before.length && j < after.length
                && before[i] === after[j]) {
                script.push(['=', i, j]);
                i += 1;
                j += 1;
            } else if (j === after.length
                || (i < before.length && table[i + 1][j] >= table[i][j + 1])) {
                script.push(['-', i, -1]);
                i += 1;
            } else {
                script.push(['+', -1, j]);
                j += 1;
            }
        }
        return script;
    }

    function signLine(line, change) {
        const sign = document.createElement('span');
        sign.className = 'km-code-version__sign';
        sign.setAttribute('aria-hidden', 'true');
        sign.textContent = change === 'added' ? '+' : '-';
        line.dataset.kmDiff = change;
        line.prepend(sign);
    }

    function showVersion(view, rows) {
        view.marked = [];
        view.filled = [];
        view.current = null;
        view.lines.clear();
        view.code.replaceChildren(...rows.map((row) => {
            const line = row.cloneNode(true);
            view.lines.set(Number(line.dataset.kmLine), line);
            return line;
        }));
    }

    function snapPixel(value) {
        const ratio = window.devicePixelRatio || 1;
        return Math.round(value * ratio) / ratio;
    }

    function updateAll() {
        codeExplains.forEach((explainer) => explainer.update());
    }

    const updateSoon = rafThrottle(() => updateAll());

    function measureAll() {
        codeExplains.forEach((explainer) => explainer.measure());
        updateAll();
    }

    function refitAll() {
        codeExplains.forEach((explainer) => {
            if (explainer.shape() !== explainer.shaped) explainer.measure();
        });
        updateAll();
    }

    let settleTimer = 0;

    function settleSoon() {
        window.clearTimeout(settleTimer);
        settleTimer = window.setTimeout(refitAll, RESIZE_SETTLE_MS);
    }

    function initCodeExplains() {
        document.querySelectorAll('[data-km-code-explain]').forEach((host) => {
            codeExplains.push(createCodeExplain(host));
        });
        if (!codeExplains.length) return;
        measureAll();
        onScroll(updateSoon);

        const panes = new ResizeObserver(settleSoon);
        codeExplains.forEach((explainer) => {
            panes.observe(explainer.pane);
            panes.observe(explainer.track);
        });
        new ResizeObserver(settleSoon).observe(document.body);

        document.addEventListener('km:fold', measureAll);
        window.addEventListener('beforeprint', () => {
            codeExplains.forEach((explainer) => explainer.fillAll());
        });

        let width = window.innerWidth;
        let height = window.innerHeight;
        let resizing = 0;
        window.addEventListener('resize', () => {
            window.clearTimeout(resizing);
            resizing = window.setTimeout(() => {
                const moved = Math.abs(window.innerHeight - height);
                if (window.innerWidth === width && moved < RESIZE_JITTER_PX) {
                    held?.recentre();
                    return;
                }
                width = window.innerWidth;
                height = window.innerHeight;
                measureAll();
            }, RESIZE_SETTLE_MS);
        }, { passive: true });

        window.matchMedia('(prefers-reduced-motion: reduce)')
            .addEventListener('change', measureAll);
        document.fonts.ready.then(measureAll);
        window.addEventListener('load', measureAll, { once: true });
    }

    function focusLine() {
        const top = headerHeight();
        return top + (window.innerHeight - top) / 2;
    }

    function jumpTo(top) {
        stopGlide();
        window.scrollTo({ top, behavior: 'instant' });
    }

    function scrollsInside(element, deltaY) {
        for (
            let node = element;
            node instanceof Element && node !== document.body;
            node = node.parentElement
        ) {
            if (!/auto|scroll/.test(getComputedStyle(node).overflowY)) continue;
            const spare = deltaY > 0
                ? node.scrollHeight - node.clientHeight - node.scrollTop
                : node.scrollTop;
            if (spare > 1) return true;
        }
        return false;
    }

    function createView(frame) {
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
            out: frame.querySelector('[data-km-output]'),
            marked: [],
            filled: [],
            current: null,
        };
    }

    function markLines(view, step) {
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

    function annotateLines(view, step, comment, opened) {
        view.filled.forEach((slot) => slot.replaceChildren());
        view.filled = [];
        const groups = new Map();
        const add = (lineNumber, item) => {
            if (!view.lines.has(lineNumber)) return;
            if (!groups.has(lineNumber)) groups.set(lineNumber, []);
            groups.get(lineNumber).push(item);
        };
        (step.vars || []).forEach(([name, lineNumber, full, short, fresh]) => {
            add(lineNumber, { name, full, short, fresh, key: name });
        });
        if (step.ret) {
            add(step.line, {
                mark: say('returns'), full: step.ret[0], short: step.ret[1],
                key: 'returns:', kind: 'return', fresh: 1,
            });
        }
        if (step.error) {
            add(step.line, {
                mark: say('error'), full: step.error[0], short: step.error[1],
                key: 'error:', kind: 'error', fresh: 1,
            });
        }
        const { open = '#', close = '' } = comment || {};
        groups.forEach((items, lineNumber) => {
            const slot = view.lines.get(lineNumber)
                .querySelector('[data-km-annotation]');
            slot.append(`${open} `);
            items.forEach((item, n) => {
                if (n) slot.append(', ');
                slot.append(entryNode(item, opened));
            });
            if (close) slot.append(` ${close}`);
            view.filled.push(slot);
        });
    }

    function followLine(view, room, shift) {
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
        return clamp(
            Math.round(target),
            0,
            Math.max(0, view.code.offsetHeight - room),
        );
    }

    function hasMore({ stage }) {
        return stage.scrollWidth - stage.clientWidth - stage.scrollLeft > 2;
    }

    function markEdges(view, above, below, more = hasMore(view)) {
        const { stage } = view;
        stage.toggleAttribute('data-km-more', more);
        stage.toggleAttribute('data-km-above', above > 2);
        stage.toggleAttribute('data-km-below', below > 2);
    }

    function wireInput() {
        if (wired) return;
        wired = true;
        const steps = { ArrowDown: 60, ArrowUp: -60 };
        const pages = { PageDown: 1, PageUp: -1 };
        const hand = (wait) => {
            handUntil = Math.max(handUntil, performance.now() + wait);
            if (!held) updateSoon();
        };
        const keyDelta = (event) => {
            const step = steps[event.key];
            if (step !== undefined) return step;
            const space = event.key === ' '
                && !event.target.closest?.(
                    'button, a, summary, [role="button"]',
                );
            if (!(event.key in pages) && !space) return undefined;
            const direction = event.key in pages
                ? pages[event.key]
                : (event.shiftKey ? -1 : 1);
            return direction * window.innerHeight * 0.85;
        };
        const taken = (event, deltaY) => event.target.closest?.('.km-header')
            || scrollsInside(event.target, deltaY);
        window.addEventListener('wheel', (event) => {
            if (event.ctrlKey
                || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
            hand(HAND_WINDOW_MS);
            if (!held || taken(event, event.deltaY)) return;
            const unit = event.deltaMode === 1
                ? 16
                : event.deltaMode === 2 ? window.innerHeight : 1;
            held.nudge(event.deltaY * unit, true);
        }, { passive: true });
        window.addEventListener('keydown', (event) => {
            if (event.altKey || event.ctrlKey || event.metaKey) return;
            if (event.target.closest?.(
                'input, textarea, select, [contenteditable]',
            )) return;
            if (event.key === 'Escape') {
                held?.release();
                return;
            }
            const delta = keyDelta(event);
            if (delta === undefined) return;
            hand(HAND_WINDOW_MS);
            if (held) {
                event.preventDefault();
                held.nudge(delta, true);
            }
        });
        let touchY = 0;
        window.addEventListener('touchstart', (event) => {
            touchY = event.touches[0].clientY;
            hand(HAND_WINDOW_MS);
        }, { passive: true });
        window.addEventListener('touchmove', (event) => {
            hand(HAND_WINDOW_MS);
            const y = event.touches[0].clientY;
            const delta = touchY - y;
            touchY = y;
            if (held && !taken(event, delta)) held.nudge(delta);
        }, { passive: true });
        ['touchend', 'touchcancel'].forEach((name) => {
            window.addEventListener(
                name,
                () => hand(TOUCH_GLIDE_MS),
                { passive: true },
            );
        });
    }

    function createCodeExplain(host) {
        const payload = readPayload(host);
        const { steps } = payload;
        const pane = host.querySelector('[data-km-pane]');
        const frame = host.querySelector('[data-km-frame]');
        const box = host.querySelector('[data-km-notes]');
        const track = host.querySelector('[data-km-track]');
        const blocks = Array.from(track.querySelectorAll('[data-km-note]'));
        const main = createView(frame);
        const { stage, code, out } = main;
        const versions = payload.codes || null;
        const drafts = versions
            ? Array.from(host.querySelectorAll('[data-km-draft]'), (draft) => {
                return Array.from(draft.querySelectorAll('[data-km-line]'));
            })
            : [];
        const texts = drafts.map((rows) => {
            return rows.map((row) => (
                row.querySelector('.km-code-explain__source').textContent
            ));
        });
        host.querySelectorAll('img[loading="lazy"]').forEach((image) => {
            image.loading = 'eager';
        });
        let carry = 0;
        const owned = Array.from(blocks.keys(), (noteIndex) => {
            const own = [];
            steps.forEach((step, n) => {
                if (step.note === noteIndex) own.push(n);
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
        if (versions) {
            text = steps.reduce((most, step) => (
                (step.out || '').length > most.length ? step.out : most
            ), '');
        }
        const paced = (note) => owned[note].reduce(
            (sum, stepIndex) => sum + (steps[stepIndex].pace || payload.pace),
            0,
        );

        const opened = new Set();
        const explainer = {
            host,
            pane,
            track,
            shaped: '',
            update,
            measure,
            shape,
            nudge,
            release,
            recentre,
            fillAll,
        };
        let snaps = [];
        const holds = new Map();
        let watcher = null;
        let fit = null;
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
        let armed = true;
        let unseen = true;
        let atTop = false;
        let lastAway = null;
        let loose = false;
        let touched = false;
        let steady = false;
        let version = 0;
        let morphing = null;
        let trackY = 0;
        let trackSpeed = 0;
        let trackFrame = 0;

        function shape() {
            return [
                host.getClientRects().length > 0,
                host.closest('.km-page--clamped') !== null,
                pane.clientWidth,
                versions
                    ? getComputedStyle(code).lineHeight
                    : code.offsetHeight,
                headerHeight(),
                mode === 'stack'
                    ? ''
                    : blocks.map((block) => block.offsetHeight).join(','),
            ].join(' ');
        }

        function annotate(step) {
            const focused = stage.contains(document.activeElement)
                ? document.activeElement.closest('[data-km-long]')
                    ?.dataset.kmKey
                : undefined;
            annotateLines(main, step, payload.comment, opened);
            if (focused === undefined) return;
            const again = Array.from(stage.querySelectorAll('[data-km-long]'))
                .find((value) => value.dataset.kmKey === focused);
            steady = true;
            (again || stage).focus({ preventScroll: true });
            steady = false;
        }

        function follow() {
            shift = followLine(main, room, shift);
            host.style.setProperty('--km-code-explain-shift', `${shift}px`);
        }

        function edge() {
            const top = loose ? stage.scrollTop : shift;
            const below = loose
                ? stage.scrollHeight - stage.clientHeight - top
                : code.offsetHeight - room - shift;
            markEdges(
                main,
                mode === 'stage' ? top : 0,
                mode === 'stage' ? below : 0,
            );
        }

        function showOutput(view, step) {
            view.out.textContent = step.out || '';
            if (step.verdict) view.out.dataset.kmVerdict = step.verdict;
            else view.out.removeAttribute('data-km-verdict');
        }

        function print(stepIndex) {
            if (!out || !text) return;
            if (versions) {
                showOutput(main, steps[stepIndex]);
            } else {
                const end = printed[stepIndex];
                const start = end - (steps[stepIndex].out || '').length;
                out.replaceChildren();
                if (start > 0) out.append(text.slice(0, start));
                if (end > start) {
                    const fresh = document.createElement('span');
                    fresh.setAttribute('data-km-fresh', '');
                    fresh.textContent = text.slice(start, end);
                    out.append(fresh);
                }
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

        function renumber(staying, to) {
            staying.forEach(([line, rowIndex]) => {
                line.dataset.kmLine = String(rowIndex + 1);
                line.dataset.kmNumber = drafts[to][rowIndex].dataset.kmNumber;
            });
        }

        function land() {
            if (!morphing) return;
            const run = morphing;
            morphing = null;
            run.timers.forEach((timer) => window.clearTimeout(timer));
            run.going.forEach((line) => line.remove());
            run.coming.forEach((line) => {
                line.removeAttribute('data-km-diff');
                line.removeAttribute('data-km-settling');
                line.querySelector('.km-code-version__sign')?.remove();
            });
        }

        function swapNow(to) {
            land();
            showVersion(main, drafts[to]);
            version = to;
        }

        function morph(to, animate) {
            if (to === version || !drafts[to]) return null;
            land();
            const from = version;
            version = to;
            const before = Array.from(code.children);
            const rows = [];
            const run = {
                to, going: [], coming: [], staying: [], timers: [],
            };
            diffLines(texts[from], texts[to]).forEach(([change, was, now]) => {
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
            main.lines.clear();
            run.staying.forEach(([line, now]) => main.lines.set(now + 1, line));
            run.coming.forEach((line) => (
                main.lines.set(Number(line.dataset.kmLine), line)
            ));
            renumber(run.staying, to);
            const first = run.coming[0] || null;
            if (!animate || to < from) {
                run.going.forEach((line) => line.remove());
                return first;
            }
            morphing = run;
            run.going.forEach((line) => {
                line.setAttribute('aria-hidden', 'true');
                line.setAttribute('data-km-going', '');
                signLine(line, 'removed');
            });
            run.coming.forEach((line) => signLine(line, 'added'));
            const swap = TIMING.codeSwap();
            const scheduleSwap = (delay, then) => (
                run.timers.push(window.setTimeout(then, delay))
            );
            scheduleSwap(swap * DIFF_VISIBLE_SWAPS, () => {
                run.going.forEach((line) => line.remove());
                run.going = [];
                run.coming.forEach((line) => {
                    line.setAttribute('data-km-settling', '');
                    line.removeAttribute('data-km-diff');
                });
                follow();
                edge();
            });
            scheduleSwap(swap * (DIFF_VISIBLE_SWAPS + 1.2), () => {
                run.coming.forEach((line) => {
                    line.removeAttribute('data-km-settling');
                    line.querySelector('.km-code-version__sign')?.remove();
                });
                morphing = null;
            });
            return first;
        }

        function loosen() {
            if (loose || mode !== 'stage' || steady || touched) return;
            loose = true;
            stage.setAttribute('data-km-loose', '');
            host.style.setProperty('--km-code-explain-shift', '0px');
            stage.scrollTop = shift;
            edge();
        }

        function rejoin() {
            if (!loose) return;
            loose = false;
            shift = Math.round(stage.scrollTop);
            host.style.setProperty('--km-code-explain-shift', `${shift}px`);
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
            if (versions) swapNow(0);
            main.marked.forEach((line) => (
                line.removeAttribute('data-km-current')
            ));
            main.marked = [];
            main.filled.forEach((slot) => slot.replaceChildren());
            main.filled = [];
            main.current = null;
            blocks.forEach((block) => {
                block.removeAttribute('data-km-active');
                block.removeAttribute('aria-current');
            });
            out?.replaceChildren();
            out?.removeAttribute('data-km-verdict');
            out?.style.removeProperty('height');
            ['--km-code-explain-stage', '--km-code-explain-notes']
                .forEach((name) => host.style.removeProperty(name));
            host.style.setProperty('--km-code-explain-shift', '0px');
            track.style.removeProperty('translate');
            keys = [];
            index = -1;
            active = -1;
            shift = 0;
        }

        function mark(noteIndex) {
            if (noteIndex === active) return;
            blocks[active]?.removeAttribute('data-km-active');
            blocks[active]?.removeAttribute('aria-current');
            active = noteIndex;
            blocks[noteIndex].setAttribute('data-km-active', '');
            blocks[noteIndex].setAttribute('aria-current', 'step');
        }

        function paint(stepIndex) {
            const next = clamp(stepIndex, 0, steps.length - 1);
            if (next === index) return;
            const animate = index !== -1
                && Math.abs(next - index) <= ANIMATE_WITHIN_STEPS
                && !prefersReducedMotion();
            index = next;
            rejoin();
            const step = steps[index];
            const fresh = versions ? morph(step.version, animate) : null;
            markLines(main, step);
            if (morphing) {
                morphing.coming.forEach((line) => (
                    line.removeAttribute('data-km-current')
                ));
                main.marked = main.marked.filter(
                    (line) => !morphing.coming.includes(line),
                );
            }
            if (fresh && !main.current) main.current = fresh;
            annotate(step);
            print(index);
            follow();
            edge();
        }

        function locate(value) {
            const into = clamp(value, 0, total);
            const found = keys.findIndex((item) => into <= item.to);
            const keyIndex = found < 0 ? keys.length - 1 : found;
            const key = keys[keyIndex];
            return {
                keyIndex,
                through: clamp(
                    (into - key.from) / Math.max(1, key.to - key.from),
                    0,
                    1,
                ),
            };
        }

        function placeTrack(y) {
            trackY = y;
            track.style.translate = `0 ${-snapPixel(y)}px`;
        }

        function glideTrack(goal, smooth) {
            cancelAnimationFrame(trackFrame);
            trackFrame = 0;
            if (!smooth || prefersReducedMotion()) {
                trackSpeed = 0;
                placeTrack(goal);
                return;
            }
            let last = performance.now();
            const step = (now) => {
                const seconds = Math.min((now - last) / 1000, 0.05);
                last = now;
                const away = trackY - goal;
                const push = (trackSpeed + TRACK_STIFFNESS * away) * seconds;
                const decay = Math.exp(-TRACK_STIFFNESS * seconds);
                trackSpeed = (trackSpeed - TRACK_STIFFNESS * push) * decay;
                placeTrack(goal + (away + push) * decay);
                if (Math.abs(trackY - goal) < 0.25
                    && Math.abs(trackSpeed) < 2) {
                    trackSpeed = 0;
                    placeTrack(goal);
                    trackFrame = 0;
                    return;
                }
                trackFrame = requestAnimationFrame(step);
            };
            trackFrame = requestAnimationFrame(step);
        }

        function render(smooth) {
            if (mode !== 'stage' || !keys.length) return;
            const { keyIndex: slot, through } = locate(progress);
            const key = keys[slot];
            glideTrack(key.a + (key.b - key.a) * through, smooth);
            let note = key.note;
            const own = owned[note];
            const length = paced(note);
            let run = 0;
            let stepIndex = own[own.length - 1];
            for (const each of own) {
                run += steps[each].pace || payload.pace;
                if (through * length < run) {
                    stepIndex = each;
                    break;
                }
            }
            if (key.kind === 'move' && through >= 0.5) {
                note += 1;
                stepIndex = owned[note][0];
            } else if (key.kind === 'move') {
                stepIndex = own[own.length - 1];
            }
            mark(note);
            paint(stepIndex);
        }

        function centre() {
            return frame.getBoundingClientRect().top + height / 2;
        }

        function recentre() {
            jumpTo(window.scrollY + centre() - focusLine());
            heldY = window.scrollY;
        }

        function lock(side) {
            if (held) return;
            progress = side > 0 ? 0 : total;
            recentre();
            const bar = window.innerWidth - root.clientWidth;
            root.style.overflow = 'hidden';
            if (bar > 0) root.style.paddingRight = `${bar}px`;
            held = explainer;
            heldAt = performance.now();
            render();
        }

        function release() {
            if (held !== explainer) return;
            held = null;
            root.style.removeProperty('overflow');
            root.style.removeProperty('padding-right');
            armed = false;
            atTop = false;
        }

        function nudge(delta, smooth) {
            if (performance.now() - heldAt < LOCK_GRACE_MS) return;
            if ((delta > 0 && progress >= total)
                || (delta < 0 && progress <= 0)) {
                release();
                return;
            }
            progress = clamp(progress + delta, 0, total);
            render(smooth);
        }

        function keepHeld() {
            if (Math.abs(window.scrollY - heldY) <= 2) return;
            if (performance.now() - focusedAt < FOCUS_SCROLL_WINDOW_MS) {
                jumpTo(heldY);
            } else release();
        }

        function crossed(away) {
            const byHand = performance.now() < handUntil;
            if (!armed || !byHand || held || lastAway === null) return;
            if (lastAway > 0 && away <= 0) lock(1);
            else if (lastAway < 0 && away >= 0) lock(-1);
        }

        function update() {
            if (mode !== 'stage') return;
            if (held === explainer) {
                keepHeld();
                return;
            }
            const away = centre() - focusLine();
            if (unseen || Math.abs(away) > window.innerHeight) {
                atTop = unseen && window.scrollY + away < 0;
                unseen = false;
                progress = away > 0 || atTop ? 0 : total;
                render();
            }
            if (Math.abs(away) > REARM_DISTANCE_PX || atTop) armed = true;
            crossed(away);
            lastAway = atTop ? 1 : away;
        }

        function clearStack() {
            watcher?.disconnect();
            watcher = null;
            for (const hold of holds.keys()) hold.remove();
            holds.clear();
            snaps.forEach((view) => view.frame.remove());
            snaps = [];
        }

        function snapshot(block, hold) {
            const clone = frame.cloneNode(true);
            clone.removeAttribute('data-km-frame');
            clone.classList.add('km-code-explain__snap');
            if (hold) hold.replaceWith(clone);
            else block.prepend(clone);
            const view = createView(clone);
            snaps.push(view);
            return view;
        }

        function fill(batch) {
            const { most, whole, heights } = fit;
            const rooms = batch.map(({ blockIndex }) => {
                const step = steps[
                    owned[blockIndex][owned[blockIndex].length - 1]
                ];
                return versions ? Math.min(most, heights[step.version]) : most;
            });
            const totals = batch.map(({ blockIndex }) => {
                const step = steps[
                    owned[blockIndex][owned[blockIndex].length - 1]
                ];
                return versions ? heights[step.version] : whole;
            });
            batch.forEach(({ view, blockIndex }, n) => {
                const upto = owned[blockIndex][owned[blockIndex].length - 1];
                const step = steps[upto];
                if (versions) showVersion(view, drafts[step.version]);
                markLines(view, step);
                annotateLines(view, step, payload.comment, opened);
                if (view.out) {
                    if (versions) showOutput(view, step);
                    else view.out.textContent = text.slice(0, printed[upto]);
                    view.out.hidden = !view.out.textContent;
                }
                view.frame.style.setProperty(
                    '--km-code-explain-stage',
                    `${rooms[n]}px`,
                );
            });
            const shifts = batch.map(({ view }, n) => (
                followLine(view, rooms[n], 0)
            ));
            const reach = batch.map(({ view }) => hasMore(view));
            batch.forEach(({ view }, n) => {
                view.frame.style.setProperty(
                    '--km-code-explain-shift',
                    `${shifts[n]}px`,
                );
                markEdges(
                    view,
                    shifts[n],
                    totals[n] - rooms[n] - shifts[n],
                    reach[n],
                );
            });
        }

        function reveal(targets) {
            const batch = targets
                .filter((hold) => holds.has(hold))
                .map((hold) => ({ hold, blockIndex: holds.get(hold) }));
            if (!batch.length) return;
            host.setAttribute('data-km-measuring', '');
            const passed = batch.map(({ hold }) => (
                hold.getBoundingClientRect().bottom <= 0
            ));
            const sizes = batch.map(({ hold }) => hold.offsetHeight);
            batch.forEach((item) => {
                watcher.unobserve(item.hold);
                holds.delete(item.hold);
                item.view = snapshot(blocks[item.blockIndex], item.hold);
            });
            fill(batch);
            const drift = batch.reduce(
                (sum, { view }, n) => (
                    sum + (passed[n] ? view.frame.offsetHeight - sizes[n] : 0)
                ),
                0,
            );
            if (Math.abs(drift) > 0.5) window.scrollBy(0, drift);
            void host.offsetHeight;
            host.removeAttribute('data-km-measuring');
        }

        function stack() {
            const first = snapshot(blocks[0]);
            const line = first.lines.get(1)?.getBoundingClientRect().height
                || 20;
            let whole = first.code.offsetHeight;
            let count = first.lines.size;
            let heights = [];
            if (versions) {
                heights = drafts.map((rows) => {
                    showVersion(first, rows);
                    return first.code.offsetHeight;
                });
                whole = Math.max(...heights);
                count = Math.max(...drafts.map((rows) => rows.length));
            }
            const pad = Math.max(0, whole - line * count);
            const most = Math.min(whole, pad + line * STACK_MAX_LINES);
            fit = { most, whole, heights, size: 0 };
            fill([{ view: first, blockIndex: 0 }]);
            fit.size = first.frame.offsetHeight;
            if (blocks.length < 2) return;
            watcher = new IntersectionObserver((entries) => {
                reveal(entries
                    .filter((entry) => entry.isIntersecting)
                    .map((entry) => entry.target));
            }, { rootMargin: '150% 0px' });
            const roomOf = (blockIndex) => {
                const last = owned[blockIndex][owned[blockIndex].length - 1];
                return versions
                    ? Math.min(fit.most, fit.heights[steps[last].version])
                    : fit.most;
            };
            const look = first.out ? getComputedStyle(first.out) : null;
            const paneOf = (blockIndex) => {
                if (!look) return 0;
                const last = owned[blockIndex][owned[blockIndex].length - 1];
                const said = versions
                    ? steps[last].out || ''
                    : text.slice(0, printed[last]);
                if (!said) return 0;
                return Math.min(
                    said.split('\n').length * parseFloat(look.lineHeight)
                        + parseFloat(look.paddingTop)
                        + parseFloat(look.paddingBottom),
                    parseFloat(look.maxHeight),
                );
            };
            const paneFirst = first.out && !first.out.hidden
                ? first.out.offsetHeight : 0;
            blocks.forEach((block, blockIndex) => {
                if (!blockIndex) return;
                const hold = document.createElement('div');
                hold.className = 'km-code-explain__snap';
                const extra = roomOf(blockIndex) - roomOf(0)
                    + paneOf(blockIndex) - paneFirst;
                hold.style.height = `${fit.size + extra}px`;
                block.prepend(hold);
                holds.set(hold, blockIndex);
                watcher.observe(hold);
            });
            if (window.matchMedia('print').matches) fillAll();
        }

        function fillAll() {
            reveal(Array.from(holds.keys()));
        }

        function pickMode() {
            if (!host.getClientRects().length) return '';
            if (prefersReducedMotion()
                || host.closest('.km-page--clamped') !== null) {
                return 'stack';
            }
            host.setAttribute('data-km-mode', 'stage');
            return host.clientWidth >= STAGE_MIN_WIDTH_PX ? 'stage' : 'stack';
        }

        function sizeStage() {
            const top = headerHeight();
            const space = window.innerHeight - top;
            if (out && text) {
                out.textContent = text;
                out.style.height = 'auto';
            }
            const full = out && text ? out.offsetHeight : 0;
            let whole = code.offsetHeight;
            let count = main.lines.size;
            if (versions) {
                whole = Math.max(...Array.from(drafts.keys(), (n) => {
                    swapNow(n);
                    return code.offsetHeight;
                }));
                count = Math.max(...drafts.map((rows) => rows.length));
                swapNow(0);
            }
            const line = main.lines.get(1)?.getBoundingClientRect().height
                || 20;
            const pad = Math.max(0, whole - line * count);
            const least = Math.min(whole, pad + line * STAGE_MIN_LINES);
            const caption = frame.offsetHeight - stage.offsetHeight - full;
            const most = Math.min(
                whole,
                Math.max(
                    least,
                    Math.min(
                        space * STAGE_SPACE_SHARE,
                        space - 2 * (full + STAGE_MARGIN_PX),
                    ) - caption,
                ),
            );
            room = most < whole
                ? Math.max(least, pad + line * Math.floor((most - pad) / line))
                : most;
            host.style.setProperty('--km-code-explain-stage', `${room}px`);
            height = caption + room;
            host.style.setProperty('--km-code-explain-notes', `${height}px`);
            pane.style.minHeight = `${pane.offsetHeight}px`;
            if (out) {
                out.replaceChildren();
                out.style.removeProperty('height');
            }
        }

        function planNotes() {
            const starts = [];
            const ends = [];
            blocks.forEach((block) => {
                const size = block.offsetHeight;
                const tall = size > height - 2 * STAGE_PADDING_PX;
                const from = tall
                    ? block.offsetTop - STAGE_PADDING_PX
                    : block.offsetTop + size / 2 - height / 2;
                starts.push(from);
                ends.push(tall
                    ? block.offsetTop + size - height + STAGE_PADDING_PX
                    : from);
            });
            let travelled = 0;
            for (let note = 0; note < blocks.length; note += 1) {
                const hold = Math.max(
                    paced(note),
                    ends[note] - starts[note],
                );
                keys.push({
                    kind: 'hold',
                    note,
                    from: travelled,
                    to: travelled + hold,
                    a: starts[note],
                    b: ends[note],
                });
                travelled += hold;
                if (note === blocks.length - 1) continue;
                const move = Math.max(
                    1,
                    Math.abs(starts[note + 1] - ends[note]),
                );
                keys.push({
                    kind: 'move',
                    note,
                    from: travelled,
                    to: travelled + move,
                    a: ends[note],
                    b: starts[note + 1],
                });
                travelled += move;
            }
            total = travelled;
            progress = clamp(progress, 0, total);
        }

        function reachable() {
            const target = window.scrollY + centre() - focusLine();
            const spare = root.scrollHeight - window.innerHeight - target;
            return Math.min(target, spare) >= REARM_DISTANCE_PX;
        }

        function useStack() {
            mode = 'stack';
            rest();
            pane.style.removeProperty('min-height');
            host.setAttribute('data-km-mode', mode);
            if (out) out.hidden = true;
        }

        function measure() {
            const wasHeld = held === explainer;
            const where = wasHeld && keys.length ? locate(progress) : null;
            clearStack();
            rejoin();
            host.setAttribute('data-km-measuring', '');
            host.removeAttribute('data-km-mode');
            mode = '';
            rest();
            pane.style.removeProperty('min-height');
            mode = pickMode();
            if (mode) host.setAttribute('data-km-mode', mode);
            if (out) out.hidden = mode !== 'stage' || !text;
            if (mode === 'stage') {
                sizeStage();
                planNotes();
                if (!reachable()) useStack();
            }
            if (mode === 'stack') stack();
            void host.offsetHeight;
            host.removeAttribute('data-km-measuring');
            explainer.shaped = shape();
            unseen = true;
            lastAway = null;
            edge();
            if (!wasHeld) return;
            if (mode !== 'stage') {
                release();
                return;
            }
            if (where) {
                const key = keys[where.keyIndex];
                progress = key.from + (key.to - key.from) * where.through;
            }
            recentre();
            render();
        }

        function goToNote(noteIndex) {
            const key = keys.find((item) => (
                item.kind === 'hold' && item.note === noteIndex
            ));
            if (!key || held !== explainer) return;
            progress = key.from + 1;
            render();
        }

        let copiedTimer = 0;
        let copiedButton = null;
        const scheduleCopy = (wait, then) => {
            copiedTimer = window.setTimeout(then, wait);
        };
        const copied = (button, done) => {
            announce(say(done ? 'copied' : 'failed'));
            window.clearTimeout(copiedTimer);
            copiedButton?.classList.remove(
                'km-code-explain__copy--fading',
                'success',
            );
            copiedButton = button;
            button.classList.toggle('success', done);
            if (!done) return;
            scheduleCopy(TIMING.tooltipHold(), () => {
                button.classList.add('km-code-explain__copy--fading');
                scheduleCopy(TIMING.fast(), () => {
                    button.classList.remove('success');
                    scheduleCopy(TIMING.fast() * 2, () => (
                        button.classList.remove('km-code-explain__copy--fading')
                    ));
                });
            });
        };

        stage.addEventListener('scroll', rafThrottle(edge), { passive: true });

        host.addEventListener('click', (event) => {
            const value = event.target.closest?.('[data-km-long]');
            if (value) unfold(value);
            const button = event.target.closest?.('[data-km-copy]');
            if (button) {
                const source = versions
                    ? { ...payload, code: versions[version] }
                    : payload;
                copyText(sourceOf(source)).then((done) => copied(button, done));
            }
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
            if (!held) lock(centre() >= focusLine() ? 1 : -1);
            else if (held !== explainer) return;
            if (!block.hasAttribute('data-km-active')) {
                goToNote(Number(block.dataset.kmNote));
            }
        });

        host.addEventListener('load', () => {
            explainer.shaped = '';
            settleSoon();
        }, true);

        wireInput();
        return explainer;
    }

    try {
        initCodeExplains();
    } catch (error) {
        console.error(error);
    }
})();
