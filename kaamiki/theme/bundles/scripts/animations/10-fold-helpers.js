    function toPx(value) {
        const number = parseFloat(value);
        return value.endsWith('rem')
            ? number * parseFloat(getComputedStyle(root).fontSize)
            : number;
    }

    function viewportHeight() {
        return window.visualViewport?.height || window.innerHeight;
    }

    let stableProbe = null;

    function stableHeight() {
        if (!stableProbe) {
            stableProbe = document.createElement('div');
            stableProbe.style.cssText = 'position: absolute; top: 0; '
                + 'width: 0; height: 100svh; visibility: hidden; '
                + 'pointer-events: none;';
            stableProbe.setAttribute('aria-hidden', 'true');
            document.body.append(stableProbe);
        }
        return stableProbe.offsetHeight || window.innerHeight;
    }

    function showMoreDock() {
        return toPx(getCssVar('--km-show-more-dock'));
    }

    function keepInView(content, collapsed, tail) {
        const top = window.scrollY + content.getBoundingClientRect().top;
        const targetY = Math.max(0, top + collapsed + tail - viewportHeight());
        const distance = window.scrollY - targetY;
        if (distance <= 0) return Promise.resolve();
        return glideTo(targetY);
    }

    function foldMotion(host, content, clamped, clamping, settled) {
        let timer = 0;
        const settle = (next) => {
            window.clearTimeout(timer);
            host.classList.remove(clamping);
            settled(!next);
            content.style.maxHeight = '';
        };
        const resize = (next, from, to) => {
            host.classList.toggle(clamped, !next);
            host.classList.add(clamping);
            content.style.maxHeight = `${from}px`;
            void content.offsetHeight;
            content.style.maxHeight = `${to}px`;
            window.clearTimeout(timer);
            timer = window.setTimeout(
                () => settle(next),
                TIMING.clamp() + CLAMP_SETTLE_MS,
            );
        };
        const stop = () => window.clearTimeout(timer);
        return { settle, resize, stop };
    }

    const idleStirs = new Set();
    let idleWired = false;

    function wireIdle() {
        if (idleWired) return;
        idleWired = true;
        for (const type of [
            'pointermove', 'pointerdown', 'keydown', 'touchstart', 'focusin',
        ]) {
            window.addEventListener(
                type,
                () => idleStirs.forEach((stir) => stir()),
                { passive: true },
            );
        }
    }

    function idleShell(shell, button, name, awake) {
        let timer = 0;
        let stirred = 0;

        const riding = () => (
            shell.getBoundingClientRect().bottom
                > viewportHeight() - showMoreDock() - 1
        );

        const rest = () => {
            window.clearTimeout(timer);
            timer = 0;
            shell.classList.remove(name);
        };

        const idle = () => {
            timer = 0;
            if (!awake()) return;
            const hold = TIMING.showMoreHold();
            const quiet = performance.now() - stirred;
            if (quiet < hold) {
                timer = window.setTimeout(idle, hold - quiet);
                return;
            }
            if (button.matches(':hover, :focus-visible')) {
                timer = window.setTimeout(idle, hold);
                return;
            }
            if (riding()) shell.classList.add(name);
        };

        const stir = () => {
            if (!awake()) return;
            stirred = performance.now();
            shell.classList.remove(name);
            if (!timer) timer = window.setTimeout(idle, TIMING.showMoreHold());
        };

        idleStirs.add(stir);
        wireIdle();
        onScroll(stir);
        return { stir, rest };
    }

