    function initHeaderHeight() {
        const header = document.querySelector('.km-header');
        if (!header) return;
        const fit = () => root.style.setProperty(
            '--km-header-height',
            `${headerHeight()}px`,
        );
        fit();
        new ResizeObserver(rafThrottle(fit)).observe(header);
    }
    function initHeaderLine() {
        const header = document.querySelector('.km-header');
        if (!header) return;
        let last = '';
        const fit = () => {
            const share = prefersReducedMotion()
                ? Number(window.scrollY > 0)
                : clamp(window.scrollY / HEADER_LINE_REACH_PX, 0, 1);
            const next = String(Math.round(share * 1000) / 1000);
            if (next === last) return;
            last = next;
            header.style.setProperty('--km-header-line', next);
        };
        fit();
        window.addEventListener('scroll', fit, { passive: true });
        window.addEventListener('resize', fit, { passive: true });
    }
    function initKeyboardModality() {
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Tab'
                || event.key?.startsWith('Arrow')) {
                root.setAttribute('data-km-keyboard', '');
            }
        }, true);
        document.addEventListener(
            'pointerdown',
            () => root.removeAttribute('data-km-keyboard'),
            true,
        );
    }

