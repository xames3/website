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

    const TIMING = {
        titleStep: () => getDurationMs('--km-title-step'),
        titleSkip: () => getDurationMs('--km-title-skip'),
        tooltipHold: () => getDurationMs('--km-tooltip-hold'),
        showMoreHold: () => getDurationMs('--km-show-more-hold'),
        swapHold: () => getDurationMs('--km-swap-hold'),
        sweepHold: () => getDurationMs('--km-sweep-hold'),
    };

