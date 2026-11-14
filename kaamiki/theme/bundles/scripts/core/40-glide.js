    let glideStop = null;

    // Runs `step(now)` every frame until it says it's done or a reader takes
    // over, and says which of the two it was.
    function everyFrame(step) {
        glideStop?.();
        return new Promise((resolve) => {
            let frame = 0;
            const finish = (arrived) => {
                cancelAnimationFrame(frame);
                GLIDE_STOPS.forEach((type) => (
                    window.removeEventListener(type, stop, true)
                ));
                glideStop = null;
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
            glideStop = stop;
            GLIDE_STOPS.forEach((type) => window.addEventListener(
                type,
                stop,
                { capture: true, passive: true },
            ));
            frame = requestAnimationFrame(tick);
        });
    }

    // Scroll from `startY` to `endY`, `shareOf(now)` saying how much of the
    // way it should have gone (0 to 1) at each frame, until it says 1 or a
    // reader takes over. It's how a glide and a fold share one motion.
    function driveScroll(startY, endY, shareOf) {
        return everyFrame((now) => {
            const share = clamp(shareOf(now), 0, 1);
            window.scrollTo({
                top: startY + (endY - startY) * share,
                behavior: 'instant',
            });
            return share === 1;
        });
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

    function glideTo(targetY) {
        const startY = window.scrollY;
        const endY = clamp(
            targetY,
            0,
            Math.max(0, root.scrollHeight - window.innerHeight),
        );
        if (Math.abs(endY - startY) < 1) return Promise.resolve(true);
        if (prefersReducedMotion()) {
            window.scrollTo(0, endY);
            return Promise.resolve(true);
        }
        const distance = endY - startY;
        const duration = clamp(
            GLIDE_BASE_MS + Math.abs(distance) * GLIDE_PX_FACTOR,
            GLIDE_MIN_MS,
            GLIDE_MAX_MS,
        );
        const spring = springProgress();
        const began = performance.now();
        return driveScroll(startY, endY, (now) => (
            spring(clamp((now - began) / duration, 0, 1))
        ));
    }

    function stopGlide() {
        glideStop?.();
    }

    function headerHeight() {
        const header = document.querySelector('.km-header');
        return header ? Math.ceil(header.getBoundingClientRect().height) : 0;
    }

