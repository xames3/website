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
        face.className = `km-swap__face km-swap__face--${kind}`;
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

    async function swapWord(field, current, next) {
        const was = measureRoll(field, current);
        const now = measureRoll(field, next);
        if (was.wrapped || now.wrapped || !(was.width || now.width)) return;
        const stage = document.createElement('span');
        stage.className = 'km-swap__stage';
        stage.setAttribute('aria-hidden', 'true');
        const ghost = document.createElement('span');
        ghost.className = 'km-swap__ghost';
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
        stage.style.setProperty('--km-swap-edge', `${edge}px`);
        const settle = engine.ms('state', field);
        const count = Math.max(was.letters.length, now.letters.length);
        const together = was.whole || now.whole;
        const step = count > 1 && !together
            ? Math.min(
                engine.ms('stagger', field),
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
            slot.className = 'km-swap__slot';
            slot.style.left = `${left}px`;
            slot.style.width = `${right - left}px`;
            const cube = document.createElement('span');
            cube.className = 'km-swap__cube';
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
        const front = stage.querySelector('.km-swap__face--front');
        const reference = document.createRange();
        reference.selectNodeContents(front);
        const drift = was.origin - reference.getBoundingClientRect().left;
        if (Math.abs(drift) > 0.001) {
            stage.style.setProperty('--km-swap-drift', `${drift}px`);
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
        const sweep = { duration, easing: 'linear', fill: 'both' };
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

    function buildSwap(field) {
        const words = field.dataset.kmWords.split('|');
        const sweeping = field.classList.contains('km-sweep');
        const swap = sweeping ? sweepPhrase : swapWord;
        const hold = sweeping ? TIMING.sweepHold : TIMING.swapHold;
        let index = 0;
        let busy = false;
        let timer;
        let round = 0;
        const advance = async () => {
            if (busy || document.hidden) return;
            busy = true;
            const current = words[index];
            index = (index + 1) % words.length;
            try {
                await swap(field, current, words[index]);
            } catch {
                field.textContent = words[index];
            }
            busy = false;
        };
        const turn = async (mine) => {
            await advance();
            if (mine === round) timer = setTimeout(() => turn(mine), hold());
        };
        new IntersectionObserver((entries) => {
            clearTimeout(timer);
            round += 1;
            if (entries[entries.length - 1].isIntersecting) {
                const mine = round;
                timer = setTimeout(() => turn(mine), hold());
            }
        }).observe(field.parentElement);
    }

    function initSwaps() {
        if (prefersReducedMotion()) return;
        document.querySelectorAll('.km-swap[data-km-words]').forEach(
            (field) => {
                if (!field.closest('a') && !prefersStill(field)) {
                    buildSwap(field);
                }
            },
        );
    }

