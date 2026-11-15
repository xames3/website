    // Motion that has to be stopped, reversed or handed on in the middle. A
    // motion that only plays should stay in the stylesheet; this is for the
    // ones a reader can interrupt. It animates only what the browser can do
    // off the main thread (transform, opacity) and takes its pace from the
    // `--km-motion-*` tokens, so the speed dial and reduced motion reach it.
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
    const MOTION_SLOW_FRAME_MS = 34;
    const MOTION_SLOW_SHARE = 0.25;
    const MOTION_GUARD_RUNS = 2;
    const MOTION_STEADY = 1e-3;
    const MOTION_PX_STEADY = 0.5;
    const MOTION_CALM_POLL_MS = 400;
    const motionOriginal = new Map();
    const motionGuard = { slow: 0 };

    // A spring as a function of how far through it is (0 to 1), for motion a
    // script drives itself: 0 at the start and 1 at the end, exactly.
    function motionCurve(settleMs, zeta = 1) {
        const spring = makeSpring(Math.max(1, settleMs), zeta);
        const settled = springProgressAt(spring, spring.settleMs);
        return (share) => {
            if (share <= 0) return 0;
            if (share >= 1) return 1;
            return springProgressAt(spring, share * spring.settleMs) / settled;
        };
    }

    // The same as an easing for the Web Animations API, or a plain one
    // where `linear()` isn't known.
    function motionEasing(settleMs, zeta = 1) {
        if (!CSS.supports('animation-timing-function', 'linear(0, 1)')) {
            return 'cubic-bezier(0.22, 1, 0.36, 1)';
        }
        return springEasing(makeSpring(Math.max(1, settleMs), zeta));
    }

    // The speed a directive asked for (`:speed: 2` is 2) and 1 for one that
    // didn't. Every time in the theme is its own over the site's speed, so
    // what a directive of its own speed takes is that over its speed.
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

    // The dial itself (1 is calm, 2 is twice as quick), for the few things
    // that budget a whole run of motion rather than one.
    function motionSpeed() {
        return parseFloat(getCssVar('--km-motion-speed')) || 1;
    }

    function resetMotion() {
        durationCache.clear();
    }

    function quietMotion() {
        root.setAttribute('data-km-motion', 'quiet');
        attempt(() => window.sessionStorage.setItem('km-motion', 'quiet'));
    }

    function isQuiet() {
        return root.getAttribute('data-km-motion') === 'quiet';
    }

    // A screen found slow stays quiet for the rest of the visit.
    if (attempt(() => window.sessionStorage.getItem('km-motion')) === 'quiet') {
        root.setAttribute('data-km-motion', 'quiet');
    }

    // A screen that can't keep up gets quieter motion, not a stuttering one.
    function watchFrames(animation) {
        let last = performance.now();
        let slow = 0;
        let count = 0;
        const frame = (now) => {
            count += 1;
            if (now - last > MOTION_SLOW_FRAME_MS) slow += 1;
            last = now;
            if (animation.playState === 'running') {
                requestAnimationFrame(frame);
                return;
            }
            if (count > 6 && slow / count > MOTION_SLOW_SHARE) {
                motionGuard.slow += 1;
                if (motionGuard.slow >= MOTION_GUARD_RUNS) quietMotion();
            }
        };
        requestAnimationFrame(frame);
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

    // Start a spring between the pairs in `frames`, closing at `speed`
    // (fractions of the whole way per ms) from the first.
    function startMotion(element, frames, spring, speed, options) {
        const easing = springEasing(spring, 0, speed);
        const animation = element.animate(
            [motionKeyframes(frames, 0), motionKeyframes(frames, 1)],
            { duration: spring.settleMs, easing, fill: 'both' },
        );
        if (!prefersReducedMotion()) watchFrames(animation);
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
            // Go back to where it started, from wherever it has got to and
            // at the speed it's going, so it brakes and turns and doesn't snap.
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
            // Head for somewhere else from where it is, at no speed.
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

    // A length in px that eases from one value to another and, sent
    // somewhere else on the way, carries the speed it had into the new
    // spring. It's how a fold goes from opening to closing without a jolt.
    // `options.rate` is a speed (px per ms, towards `to`) to start at, for a
    // motion that takes over from one that was stopped to measure.
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

    // `frames` is `{ transform: ['translateY(0.75rem)', 'none'], opacity:
    // [0, 1] }`; `role` names a pace (`content`, `surface`...) and `zeta` how
    // bouncy: 1 is none, below 1 overshoots a little.
    function animateMotion(element, frames, options = {}) {
        const settle = prefersReducedMotion()
            ? 1
            : options.duration ?? motionMs(options.role || 'content');
        const spring = makeSpring(Math.max(1, settle), options.zeta ?? 1);
        return startMotion(element, frames, spring, 0, options);
    }

    // Run `task` the first time a reader shows they're about to use `element`:
    // a pointer over it, focus in it or a finger down on it. It's how the
    // heavy work for a click is done before the click.
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

    // The same, once the page has stopped entering, so work done ahead of
    // a reader's click never lands on the page's own entrance.
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

    // What a tuning panel needs, so one can be built without reading the
    // rest: the tokens, a way to change one live, to slow everything down,
    // to replay what's on the page and to freeze it.
    const motionLab = {
        tokens: () => [...MOTION_TOKENS],
        get: (name) => getCssVar(name),
        set: (name, value) => {
            // A site may have set the token itself (the speed is written
            // on `<html>` when a build sets it), so keep that to go back to.
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
        speedOf: scopeSpeed,
        speed: motionSpeed,
        quiet: isQuiet,
        watch: watchFrames,
        animate: animateMotion,
        length: animateLength,
        intent: onIntent,
        idle: whenIdle,
        calm: whenCalm,
        spring: makeSpring,
        easing: springEasing,
        curve: motionCurve,
        ease: motionEasing,
        lab: motionLab,
    };

