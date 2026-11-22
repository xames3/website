    const MOTION_TOKENS = [
        '--km-motion-speed',
        '--km-motion-press',
        '--km-motion-surface',
        '--km-motion-state',
        '--km-motion-content',
        '--km-motion-fade',
        '--km-motion-enter',
        '--km-motion-page',
        '--km-motion-stagger',
        '--km-motion-ambient',
        '--km-motion-rise',
        '--km-motion-rise-small',
    ];
    const MOTION_STEADY = 1e-3;
    const MOTION_PX_STEADY = 0.5;
    const MOTION_CALM_POLL_MS = 400;
    const motionOriginal = new Map();

    function motionCurve(settleMs, zeta = 1) {
        const spring = makeSpring(Math.max(1, settleMs), zeta);
        const settled = springProgressAt(spring, spring.settleMs);
        return (share) => {
            if (share <= 0) return 0;
            if (share >= 1) return 1;
            return springProgressAt(spring, share * spring.settleMs) / settled;
        };
    }

    function motionEasing(settleMs, zeta = 1, until = 1) {
        if (!CSS.supports('animation-timing-function', 'linear(0, 1)')) {
            return getCssVar('--km-ease-smooth');
        }
        return springEasing(
            makeSpring(Math.max(1, settleMs), zeta),
            0,
            0,
            SPRING_POINTS,
            until,
        );
    }

    function motionWhen(settleMs, progress, zeta = 1) {
        const curve = motionCurve(settleMs, zeta);
        let low = 0;
        let high = 1;
        for (let i = 0; i < 40; i += 1) {
            const middle = (low + high) / 2;
            if (curve(middle) < progress) low = middle;
            else high = middle;
        }
        return high;
    }

    function scopeSpeed(scope) {
        const timed = scope?.closest?.('[class*="km-speed--"]');
        if (!timed) return 1;
        return parseFloat(
            getComputedStyle(timed).getPropertyValue('--km-speed'),
        ) || 1;
    }

    function motionMs(name, scope) {
        return getDurationMs(`--km-motion-${name}`) / scopeSpeed(scope);
    }

    function motionSpeed() {
        return parseFloat(getCssVar('--km-motion-speed')) || 1;
    }

    function pacedMs(ms, scope) {
        return ms / motionSpeed() / scopeSpeed(scope);
    }

    function resetMotion() {
        durationCache.clear();
    }

    function motionKeyframes(frames, side) {
        return Object.fromEntries(
            Object.entries(frames).map(([name, pair]) => [name, pair[side]]),
        );
    }

    function currentValues(element, frames) {
        const style = getComputedStyle(element);
        const dashed = (name) => name.replace(
            /[A-Z]/g,
            (letter) => `-${letter.toLowerCase()}`,
        );
        return Object.fromEntries(Object.keys(frames).map((name) => [
            name,
            style.getPropertyValue(dashed(name)),
        ]));
    }

    function startMotion(element, frames, spring, speed, options) {
        const easing = springEasing(spring, 0, speed);
        const animation = element.animate(
            [motionKeyframes(frames, 0), motionKeyframes(frames, 1)],
            { duration: spring.settleMs, easing, fill: 'both' },
        );
        const state = (time) => {
            const here = springAt(spring, time, 1, -speed);
            return { value: 1 - here.left, rate: -here.speed };
        };
        const motion = {
            animation,
            frames,
            spring,
            finished: animation.finished.catch(() => {}),
            value: () => state(
                clamp(animation.currentTime ?? 0, 0, spring.settleMs),
            ),
            cancel: () => animation.cancel(),
            reverse: (more = {}) => {
                const now = motion.value();
                const here = currentValues(element, frames);
                const back = Object.fromEntries(Object.entries(frames).map(
                    ([name, pair]) => [name, [here[name], pair[0]]],
                ));
                animation.cancel();
                const closing = Math.abs(now.value) < MOTION_STEADY
                    ? 0
                    : -now.rate / now.value;
                return startMotion(
                    element,
                    back,
                    spring,
                    closing,
                    { ...options, ...more },
                );
            },
            retarget: (next, more = {}) => {
                const here = currentValues(element, next);
                const aimed = Object.fromEntries(Object.entries(next).map(
                    ([name, to]) => [name, [here[name], to]],
                ));
                animation.cancel();
                return startMotion(
                    element,
                    aimed,
                    spring,
                    0,
                    { ...options, ...more },
                );
            },
        };
        motion.finished.then(() => {
            if (animation.playState !== 'finished') return;
            if (options.commit) {
                animation.commitStyles();
                animation.cancel();
            }
            options.onDone?.(motion);
        });
        return motion;
    }

    function animateLength(element, property, from, to, options = {}) {
        const settle = prefersReducedMotion()
            ? 1
            : options.duration ?? motionMs(options.role || 'content');
        const spring = makeSpring(Math.max(1, settle), options.zeta ?? 1);
        const closing = (rate, start, end) => (
            Math.abs(end - start) < MOTION_PX_STEADY ? 0 : rate / (end - start)
        );
        const run = (start, end, rate, opts) => {
            const base = startMotion(
                element,
                { [property]: [`${start}px`, `${end}px`] },
                spring,
                closing(rate, start, end),
                opts,
            );
            const length = {
                ...base,
                from: start,
                to: end,
                now: () => start + (end - start) * base.value().value,
                rate: () => (end - start) * base.value().rate,
                retarget: (next, more = {}) => {
                    const here = length.now();
                    const speed = length.rate();
                    base.animation.cancel();
                    return run(here, next, speed, { ...opts, ...more });
                },
            };
            length.reverse = (more) => length.retarget(start, more);
            return length;
        };
        return run(from, to, options.rate ?? 0, options);
    }

    function animateMotion(element, frames, options = {}) {
        const settle = prefersReducedMotion()
            ? 1
            : options.duration ?? motionMs(options.role || 'content');
        const spring = makeSpring(Math.max(1, settle), options.zeta ?? 1);
        return startMotion(element, frames, spring, 0, options);
    }

    function onIntent(element, task) {
        let done = false;
        const events = ['pointerenter', 'focusin', 'touchstart'];
        const stop = () => events.forEach((name) => (
            element.removeEventListener(name, run)
        ));
        function run() {
            if (done) return;
            done = true;
            stop();
            task();
        }
        events.forEach((name) => element.addEventListener(
            name,
            run,
            { passive: true },
        ));
        return stop;
    }

    function whenIdle(task, timeout = 1500) {
        if ('requestIdleCallback' in window) {
            return window.requestIdleCallback(task, { timeout });
        }
        return window.setTimeout(task, 1);
    }

    function whenCalm(task, timeout = 1500) {
        const wait = () => {
            if (document.querySelector(`.${REVEAL_WAITING}`)) {
                window.setTimeout(wait, MOTION_CALM_POLL_MS);
                return;
            }
            whenIdle(task, timeout);
        };
        wait();
    }

    const motionLab = {
        tokens: () => [...MOTION_TOKENS],
        get: (name) => getCssVar(name),
        set: (name, value) => {
            if (!motionOriginal.has(name)) {
                motionOriginal.set(name, root.style.getPropertyValue(name));
            }
            root.style.setProperty(name, String(value));
            resetMotion();
            root.dispatchEvent(
                new CustomEvent('km:motion', { detail: { name, value } }),
            );
        },
        reset: (name) => {
            const original = motionOriginal.get(name) || '';
            motionOriginal.delete(name);
            if (original) root.style.setProperty(name, original);
            else root.style.removeProperty(name);
            resetMotion();
            root.dispatchEvent(
                new CustomEvent('km:motion', { detail: { name, value: null } }),
            );
        },
        speed: (factor) => motionLab.set('--km-motion-speed', factor),
        slow: (factor) => motionLab.speed(1 / factor),
        replay: (scope = document) => scope.getAnimations({ subtree: true })
            .forEach((animation) => {
                animation.cancel();
                animation.play();
            }),
        pause: () => document.getAnimations().forEach((a) => a.pause()),
        play: () => document.getAnimations().forEach((a) => a.play()),
        scrub: (share) => document.getAnimations().forEach((a) => {
            const total = a.effect?.getComputedTiming().endTime;
            if (Number.isFinite(total)) {
                a.pause();
                a.currentTime = total * clamp(share, 0, 1);
            }
        }),
    };

    const motion = {
        ms: motionMs,
        paced: pacedMs,
        speed: motionSpeed,
        animate: animateMotion,
        length: animateLength,
        intent: onIntent,
        idle: whenIdle,
        calm: whenCalm,
        spring: makeSpring,
        easing: springEasing,
        curve: motionCurve,
        ease: motionEasing,
        when: motionWhen,
        lab: motionLab,
    };

