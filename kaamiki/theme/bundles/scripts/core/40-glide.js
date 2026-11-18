    const glideStops = new Map();

    // Runs `step(now)` every frame until it says it's done or a reader takes
    // over `scroller`, and says which of the two it was.
    function everyFrame(step, scroller = window) {
        glideStops.get(scroller)?.();
        return new Promise((resolve) => {
            let frame = 0;
            const finish = (arrived) => {
                cancelAnimationFrame(frame);
                GLIDE_STOPS.forEach((type) => (
                    scroller.removeEventListener(type, stop, true)
                ));
                glideStops.delete(scroller);
                resolve(arrived);
            };
            const stop = (event) => {
                if (event?.type === 'keydown'
                    && !GLIDE_KEYS.has(event.key)) return;
                if (event?.type === 'wheel'
                    && !event.deltaX && !event.deltaY) return;
                finish(false);
            };
            const tick = (now) => {
                if (step(now)) finish(true);
                else frame = requestAnimationFrame(tick);
            };
            glideStops.set(scroller, stop);
            GLIDE_STOPS.forEach((type) => scroller.addEventListener(
                type,
                stop,
                { capture: true, passive: true },
            ));
            frame = requestAnimationFrame(tick);
        });
    }

    // Scroll `scroller` along `side` from `start` to `end`, `shareOf(now)`
    // saying how much of the way it should have gone (0 to 1) at each
    // frame, until it says 1 or a reader takes over. It's how a glide and
    // a fold share one motion.
    function driveScroll(start, end, shareOf, scroller = window, side = 'top') {
        return everyFrame((now) => {
            const share = clamp(shareOf(now), 0, 1);
            scroller.scrollTo({
                [side]: start + (end - start) * share,
                behavior: 'instant',
            });
            return share === 1;
        }, scroller);
    }

    // Keeps `anchor` where it is on the screen while something above it
    // changes size, by scrolling the page as far as it would have moved,
    // until `settled()` says the change is over or a reader takes over.
    function holdPlace(anchor, settled) {
        const top = anchor.getBoundingClientRect().top;
        return everyFrame(() => {
            const drift = anchor.getBoundingClientRect().top - top;
            if (Math.abs(drift) >= 0.5) {
                window.scrollBy({ top: drift, behavior: 'instant' });
            }
            return settled();
        });
    }

    function glide(scroller, side, start, far, target) {
        const end = clamp(target, 0, Math.max(0, far));
        if (Math.abs(end - start) < 1) return Promise.resolve(true);
        if (prefersReducedMotion()) {
            scroller.scrollTo({ [side]: end });
            return Promise.resolve(true);
        }
        const distance = end - start;
        const duration = clamp(
            GLIDE_BASE_MS + Math.abs(distance) * GLIDE_PX_FACTOR,
            GLIDE_MIN_MS,
            GLIDE_MAX_MS,
        ) / motionSpeed();
        const spring = motionCurve(duration);
        const began = performance.now();
        return driveScroll(start, end, (now) => (
            spring(clamp((now - began) / duration, 0, 1))
        ), scroller, side);
    }

    function glideTo(targetY) {
        return glide(
            window,
            'top',
            window.scrollY,
            root.scrollHeight - window.innerHeight,
            targetY,
        );
    }

    // The same across `element`, with its snap let go on the way, so the
    // snap doesn't pull at each frame.
    function glideAcross(element, left) {
        element.style.scrollSnapType = 'none';
        return glide(
            element,
            'left',
            element.scrollLeft,
            element.scrollWidth - element.clientWidth,
            left,
        ).finally(() => {
            if (!glideStops.has(element)) {
                element.style.removeProperty('scroll-snap-type');
            }
        });
    }

    function stopGlide() {
        glideStops.get(window)?.();
    }

    function headerHeight() {
        const header = document.querySelector('.km-header');
        return header ? Math.ceil(header.getBoundingClientRect().height) : 0;
    }

