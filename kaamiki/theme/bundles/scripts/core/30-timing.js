    const durationCache = new Map();

    function getCssVar(name) {
        return getComputedStyle(root).getPropertyValue(name).trim();
    }

    let timeProbe = null;

    // A time is a `calc()` of the speed dial, which the browser only turns
    // into a number on a property that takes a time, so ask one that does.
    function getDurationMs(name) {
        if (durationCache.has(name)) return durationCache.get(name);
        if (!timeProbe) {
            timeProbe = document.createElement('div');
            timeProbe.setAttribute('aria-hidden', 'true');
            timeProbe.style.cssText = 'position: absolute; width: 0; '
                + 'height: 0; visibility: hidden; pointer-events: none;';
            root.append(timeProbe);
        }
        timeProbe.style.setProperty(
            'transition-duration',
            `var(${name}, 0ms)`,
            'important',
        );
        const raw = getComputedStyle(timeProbe).transitionDuration;
        const value = raw.endsWith('ms')
            ? parseFloat(raw)
            : parseFloat(raw) * 1000;
        durationCache.set(name, value);
        return value;
    }

    // https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/cubic-bezier
    const SMOOTH_CURVE = [0.32, 0.72, 0, 1];

    // The progress (0 to 1) of an easing, `cubic-bezier(x1, y1, x2, y2)`,
    // `time` (0 to 1) of the way through it.
    function cubicBezier(x1, y1, x2, y2) {
        const axis = (a, b, t) => (
            3 * a * (1 - t) ** 2 * t + 3 * b * (1 - t) * t ** 2 + t ** 3
        );
        return (time) => {
            if (time <= 0) return 0;
            if (time >= 1) return 1;
            let low = 0;
            let high = 1;
            for (let i = 0; i < 32; i += 1) {
                const middle = (low + high) / 2;
                if (axis(x1, x2, middle) < time) low = middle;
                else high = middle;
            }
            return axis(y1, y2, (low + high) / 2);
        };
    }

    function springProgress() {
        return cubicBezier(...SMOOTH_CURVE);
    }

    const TIMING = {
        titleStep: () => getDurationMs('--km-title-step'),
        titleSkip: () => getDurationMs('--km-title-skip'),
        tooltipHold: () => getDurationMs('--km-tooltip-hold'),
        showMoreHold: () => getDurationMs('--km-show-more-hold'),
        swapHold: () => getDurationMs('--km-swap-hold'),
        sweepHold: () => getDurationMs('--km-sweep-hold'),
    };

