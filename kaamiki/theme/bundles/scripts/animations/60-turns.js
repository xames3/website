    function rollParts(word) {
        if (!ROLL_PARTS || ROLL_WHOLE.test(word)) return [word];
        return Array.from(ROLL_PARTS.segment(word), (part) => part.segment);
    }

    // The word in the plain text: where each letter starts, counted from
    // the first, and how wide the word is. A word is as wide as it's laid
    // out, which in WebKit isn't the distance between two letters the way
    // it's reported (those are set on whole pixels, the width isn't).
    function measureRoll(field, text) {
        const parts = rollParts(text);
        field.textContent = text;
        const range = document.createRange();
        const rectOf = (start, end) => {
            range.setStart(field.firstChild, start);
            range.setEnd(field.firstChild, end);
            return range.getBoundingClientRect();
        };
        const first = rectOf(0, parts[0].length);
        let at = 0;
        const letters = parts.map((part) => {
            const rect = rectOf(at, at + part.length);
            at += part.length;
            return { x: rect.left - first.left, width: rect.width };
        });
        range.selectNodeContents(field);
        const tops = Array.from(range.getClientRects(), (rect) => rect.top);
        const rows = Math.max(...tops) - Math.min(...tops);
        return {
            parts,
            letters,
            width: range.getBoundingClientRect().width,
            origin: first.left,
            height: first.height,
            wrapped: rows > first.height / 2,
            whole: !ROLL_PARTS || ROLL_WHOLE.test(text),
        };
    }

    function rollFace(kind, text, letter, left) {
        const face = document.createElement('span');
        face.className = `km-roll__face km-roll__face--${kind}`;
        face.textContent = text;
        face.style.left = `${letter.x - left}px`;
        return face;
    }

    // A spring for the box that ends moving about a pixel and a half a
    // frame whatever the distance, as the engine's own do for a tall fold.
    // Its tail is cut where it still has that speed; left to run to the
    // engine's 1% it would crawl through a short move at a fraction of a
    // pixel a frame, which a screen that places text on whole pixels shows
    // as shimmer.
    function glideEasing(distance, settle) {
        if (!CSS.supports('animation-timing-function', 'linear(0, 1)')) {
            return engine.ease(settle);
        }
        let reach = engine.spring(settle).omega * settle;
        const speed = (x) => (
            (Math.abs(distance) * x * x * Math.exp(-x))
            / (settle * (1 - (1 + x) * Math.exp(-x)))
        ) * ROLL_FRAME_MS;
        while (reach > ROLL_GLIDE_MIN_X && speed(reach) < ROLL_GLIDE_END_PX) {
            reach -= 0.1;
        }
        return engine.easing(
            { settleMs: settle, zeta: 1, omega: reach / settle },
        );
    }

    function ownMs(field, name, token) {
        return name in field.dataset
            ? engine.paced(Number(field.dataset[name]), field)
            : token;
    }

    async function rollWord(field, current, next) {
        const was = measureRoll(field, current);
        const now = measureRoll(field, next);
        if (was.wrapped || now.wrapped || !(was.width || now.width)) return;
        const stage = document.createElement('span');
        stage.className = 'km-roll__stage';
        stage.setAttribute('aria-hidden', 'true');
        const ghost = document.createElement('span');
        ghost.className = 'km-roll__ghost';
        ghost.textContent = current;
        stage.append(ghost);
        const spoken = document.createElement('span');
        spoken.className = 'km-sr-only';
        spoken.textContent = next;
        field.replaceChildren(spoken, stage);
        const edge = was.height;
        stage.style.marginRight = '1px';
        const held = ghost.getBoundingClientRect().width;
        stage.style.marginRight = '';
        stage.style.setProperty('--km-roll-edge', `${edge}px`);
        const settle = ownMs(field, 'kmDuration', engine.ms('state', field));
        const count = Math.max(was.letters.length, now.letters.length);
        const together = was.whole || now.whole;
        const step = count > 1 && !together
            ? Math.min(
                ownMs(field, 'kmStagger', engine.ms('stagger', field)),
                (settle * ROLL_SPREAD_SHARE) / (count - 1),
            )
            : 0;
        const reach = ROLL_OVERLAP_EM * parseFloat(
            getComputedStyle(field).fontSize,
        );
        const easing = getCssVar('--km-ease-smooth');
        const turn = (angle) => (
            `translateZ(${-edge / 2}px) rotateX(${angle}deg)`
        );
        const rolls = [];
        let clear = 0;
        let room = Infinity;
        const slots = document.createDocumentFragment();
        for (let i = 0; i < count; i += 1) {
            const old = was.letters[i];
            const fresh = now.letters[i];
            const both = [old, fresh].filter(Boolean);
            const left = Math.min(...both.map((letter) => letter.x));
            const right = Math.max(
                ...both.map((letter) => letter.x + letter.width),
            );
            const slot = document.createElement('span');
            slot.className = 'km-roll__slot';
            slot.style.left = `${left}px`;
            slot.style.width = `${right - left}px`;
            const cube = document.createElement('span');
            cube.className = 'km-roll__cube';
            const timing = {
                duration: settle,
                delay: i * step,
                easing,
                fill: 'both',
            };
            if (old) {
                const front = rollFace('front', was.parts[i], old, left);
                cube.append(front);
                if (old.x + old.width > now.width + reach) {
                    clear = Math.max(
                        clear,
                        timing.delay + settle * ROLL_CLEAR_SHARE,
                    );
                }
            }
            if (fresh) {
                const back = rollFace('back', now.parts[i], fresh, left);
                cube.append(back);
                if (fresh.x + fresh.width > was.width + reach) {
                    room = Math.min(
                        room,
                        timing.delay + settle * ROLL_APPEAR_SHARE,
                    );
                }
            }
            slot.append(cube);
            slots.append(slot);
            rolls.push(cube.animate(
                [{ transform: turn(0) }, { transform: turn(90) }],
                timing,
            ));
        }
        stage.prepend(slots);
        const front = stage.querySelector('.km-roll__face--front');
        const reference = document.createRange();
        reference.selectNodeContents(front);
        const drift = was.origin - reference.getBoundingClientRect().left;
        if (Math.abs(drift) > 0.001) {
            stage.style.setProperty('--km-roll-drift', `${drift}px`);
        }
        const travel = Math.min(
            settle * ROLL_GLIDE_SHARE,
            Math.max(room, settle * ROLL_QUICK_SHARE),
        );
        const glide = stage.animate(
            [
                { marginRight: `${was.width - held}px` },
                { marginRight: `${now.width - held}px` },
            ],
            {
                duration: travel,
                delay: clear,
                easing: glideEasing(now.width - was.width, travel),
                fill: 'both',
            },
        );
        rolls.push(glide);
        const finish = () => rolls.forEach((roll) => roll.finish());
        window.addEventListener('resize', finish, { once: true });
        try {
            await Promise.all(rolls.map((roll) => roll.finished));
        } finally {
            window.removeEventListener('resize', finish);
        }
        field.textContent = next;
    }

    async function sweepPhrase(field, current, next) {
        const stage = document.createElement('span');
        stage.className = 'km-sweep__stage';
        stage.setAttribute('aria-hidden', 'true');
        const leaving = document.createElement('span');
        leaving.className = 'km-sweep__leaving';
        leaving.textContent = current;
        stage.append(leaving);
        field.replaceChildren(stage);
        const from = stage.getBoundingClientRect();
        const word = document.createElement('span');
        word.className = 'km-sweep__word';
        word.textContent = next;
        stage.append(word);
        leaving.style.position = 'absolute';
        const to = stage.getBoundingClientRect();
        leaving.style.width = `${from.width}px`;
        word.style.width = `${to.width}px`;
        stage.style.width = `${from.width}px`;
        stage.style.height = `${from.height}px`;
        const duration = engine.ms('sweep', field);
        const sweep = {
            duration,
            easing: engine.ease(duration),
            fill: 'both',
        };
        const gone = { backgroundPosition: '0% 0' };
        const here = { backgroundPosition: '100% 0' };
        const animations = [
            leaving.animate(
                [here, { ...gone, offset: SWEEP_OUT_END }, gone],
                sweep,
            ),
            word.animate(
                [here, { ...here, offset: SWEEP_IN_START }, gone],
                sweep,
            ),
        ];
        const glide = (lag, share) => ({
            duration: duration * share,
            delay: duration * lag,
            easing: engine.ease(duration * share),
            fill: 'both',
        });
        const size = (name, start, end, lag, share) => stage.animate(
            [{ [name]: `${start}px` }, { [name]: `${end}px` }],
            glide(lag, share),
        );
        animations.push(
            size(
                'width',
                from.width,
                to.width,
                SWEEP_RESIZE_LAG_SHARE,
                SWEEP_RESIZE_SHARE,
            ),
        );
        if (Math.abs(to.height - from.height) > 1) {
            // Room is made before the new text comes in and given back once
            // the old text has gone.
            const growing = to.height > from.height;
            const lag = growing ? 0 : SWEEP_OUT_END;
            const share = growing ? SWEEP_IN_START : 1 - SWEEP_OUT_END;
            animations.push(
                size('height', from.height, to.height, lag, share),
            );
        }
        await Promise.all(animations.map((animation) => animation.finished));
        field.textContent = next;
    }

    function buildTurns(field) {
        const words = field.dataset.kmWords.split('|');
        const sweeping = field.classList.contains('km-sweep');
        const change = sweeping ? sweepPhrase : rollWord;
        const hold = sweeping
            ? TIMING.sweepHold
            : () => ownMs(field, 'kmInterval', TIMING.rollHold());
        let index = 0;
        let busy = false;
        let stopped = false;
        let timer;
        let round = 0;
        const advance = async () => {
            if (busy || document.hidden) return;
            busy = true;
            const current = words[index];
            index = (index + 1) % words.length;
            try {
                await change(field, current, words[index]);
            } catch {
                field.textContent = words[index];
            }
            if (stopped) field.textContent = words[0];
            busy = false;
        };
        const turn = async (mine) => {
            await advance();
            if (mine === round) timer = setTimeout(() => turn(mine), hold());
        };
        const seen = new IntersectionObserver((entries) => {
            clearTimeout(timer);
            round += 1;
            if (entries[entries.length - 1].isIntersecting) {
                const mine = round;
                timer = setTimeout(() => turn(mine), hold());
            }
        });
        seen.observe(field.parentElement);
        return () => {
            stopped = true;
            seen.disconnect();
            clearTimeout(timer);
            round += 1;
            field.textContent = words[0];
        };
    }

    function typeNoise() {
        return (Math.random() + Math.random() + Math.random() - 1.5) / 0.5;
    }

    function typeSlip(char) {
        const lower = char.toLowerCase();
        const near = [];
        TYPEWRITE_ROWS.forEach((row, y) => {
            const x = row.indexOf(lower);
            if (x === -1) return;
            near.push(row.charAt(x - 1), row.charAt(x + 1));
            [y - 1, y + 1].forEach((other) => {
                if (TYPEWRITE_ROWS[other]) {
                    near.push(TYPEWRITE_ROWS[other].charAt(x));
                }
            });
        });
        const keys = near.filter(Boolean);
        if (!keys.length) return '';
        const key = keys[Math.floor(Math.random() * keys.length)];
        return char === lower ? key : key.toUpperCase();
    }

    function typeGap(previous, key, drift) {
        let wait = key * drift * Math.exp(typeNoise() * 0.3);
        if (previous === ' ') {
            wait += key * (0.3 + Math.random() * 0.7);
        } else if (previous === ',' || previous === '-') {
            wait += key * (0.8 + Math.random() * 1.2);
        }
        if (Math.random() < 0.05) wait += key * (2 + Math.random() * 3);
        return Math.round(wait);
    }

    function typeSteps(word, key, back) {
        const steps = [];
        let shown = '';
        let drift = 1;
        let careful = false;
        const put = (text, wait) => {
            steps.push({ text, wait });
            shown = text;
        };
        while (shown !== word) {
            const at = shown.length;
            const char = word.charAt(at);
            const wrong = at > 0 && !careful && Math.random() < TYPEWRITE_SLIP
                ? typeSlip(char)
                : '';
            drift = clamp(drift + (Math.random() - 0.5) * 0.2, 0.8, 1.25);
            careful = false;
            if (!wrong) {
                put(shown + char, typeGap(word.charAt(at - 1), key, drift));
                continue;
            }
            const run = Math.min(
                word.length - at - 1,
                Math.floor(Math.random() * 3),
            );
            put(shown + wrong, typeGap(word.charAt(at - 1), key, drift));
            for (let i = 1; i <= run; i += 1) {
                put(
                    shown + word.charAt(at + i),
                    typeGap(word.charAt(at + i - 1), key, drift),
                );
            }
            for (let j = 0; j <= run; j += 1) {
                put(
                    shown.slice(0, -1),
                    j
                        ? Math.round(back * (0.8 + Math.random() * 0.4))
                        : Math.round(key * (2 + Math.random() * 2)),
                );
            }
            careful = true;
        }
        return steps;
    }

    function deleteSteps(word, back) {
        const steps = [];
        for (let i = word.length - 1; i >= 0; i -= 1) {
            const held = word.length - 1 - i;
            const wait = held === 0
                ? back * 1.5
                : held === 1 ? back * 4 : back * (0.85 + Math.random() * 0.3);
            steps.push({ text: word.slice(0, i), wait: Math.round(wait) });
        }
        return steps;
    }

    function buildTypewrite(field) {
        const words = field.dataset.kmWords.split('|');
        const still = field.textContent;
        const spoken = document.createElement('span');
        spoken.className = 'km-sr-only';
        spoken.textContent = still;
        const typed = document.createElement('span');
        typed.setAttribute('aria-hidden', 'true');
        const cursor = document.createElement('span');
        cursor.className = 'km-typewrite__cursor';
        cursor.setAttribute('aria-hidden', 'true');
        field.replaceChildren(spoken, typed, cursor);
        const key = () => ownMs(
            field,
            'kmKey',
            engine.ms('typewrite-key', field),
        );
        const back = () => ownMs(
            field,
            'kmDelete',
            engine.ms('typewrite-delete', field),
        );
        let index = 0;
        let timer = 0;
        let solid = 0;
        let round = 0;
        const show = (text) => {
            typed.textContent = text;
            cursor.classList.add('km-typewrite__cursor--typing');
            clearTimeout(solid);
            solid = setTimeout(
                () => cursor.classList.remove('km-typewrite__cursor--typing'),
                TYPEWRITE_SOLID_MS,
            );
        };
        const play = (steps, lead, mine, done) => {
            let at = 0;
            const step = () => {
                if (mine !== round) return;
                show(steps[at].text);
                at += 1;
                if (at < steps.length) timer = setTimeout(step, steps[at].wait);
                else done();
            };
            timer = setTimeout(step, lead + steps[0].wait);
        };
        const cycle = (mine) => {
            if (document.hidden) {
                const later = ownMs(field, 'kmRest', TIMING.typewriteRest());
                timer = setTimeout(() => cycle(mine), later);
                return;
            }
            const word = words[index];
            index = (index + 1) % words.length;
            play(
                typeSteps(word, key(), back()),
                ownMs(field, 'kmRest', TIMING.typewriteRest()),
                mine,
                () => play(
                    deleteSteps(word, back()),
                    ownMs(field, 'kmInterval', TIMING.typewriteHold()),
                    mine,
                    () => cycle(mine),
                ),
            );
        };
        const seen = new IntersectionObserver((entries) => {
            clearTimeout(timer);
            round += 1;
            const shown = entries[entries.length - 1].isIntersecting;
            cursor.classList.toggle('km-typewrite__cursor--still', !shown);
            if (shown) {
                typed.textContent = '';
                cycle(round);
            }
        });
        seen.observe(field.parentElement);
        return () => {
            seen.disconnect();
            clearTimeout(timer);
            clearTimeout(solid);
            round += 1;
            field.textContent = still;
        };
    }

    function initTurns() {
        const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
        let stops = [];
        const start = () => {
            stops = [...document.querySelectorAll('[data-km-words]')]
                .filter((field) => !field.closest('a') && !prefersStill(field))
                .map((field) => (
                    field.classList.contains('km-typewrite')
                        ? buildTypewrite(field)
                        : buildTurns(field)
                ));
        };
        reduced.addEventListener('change', () => {
            stops.forEach((stop) => stop());
            stops = [];
            if (!reduced.matches) start();
        });
        if (!reduced.matches) start();
    }

