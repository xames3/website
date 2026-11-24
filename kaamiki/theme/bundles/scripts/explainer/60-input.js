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
        onPage(window, 'wheel', (event) => {
            if (event.ctrlKey
                || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
            hand(HAND_WINDOW_MS);
            if (!held || taken(event, event.deltaY)) return;
            const unit = event.deltaMode === 1
                ? 16
                : event.deltaMode === 2 ? window.innerHeight : 1;
            held.nudge(event.deltaY * unit, true);
        });
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
        onPage(window, 'touchstart', (event) => {
            touchY = event.touches[0].clientY;
            hand(HAND_WINDOW_MS);
        });
        onPage(window, 'touchmove', (event) => {
            hand(HAND_WINDOW_MS);
            const y = event.touches[0].clientY;
            const delta = touchY - y;
            touchY = y;
            if (held && !taken(event, delta)) held.nudge(delta);
        });
        ['touchend', 'touchcancel'].forEach((name) => {
            onPage(window, name, () => hand(TOUCH_GLIDE_MS));
        });
    }

