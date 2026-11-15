    function shuffle(list) {
        for (let i = list.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [list[i], list[j]] = [list[j], list[i]];
        }
    }

    function createBackdrop(backdrop, urls, byline) {
        const overlay = document.createElement('div');
        overlay.className = backdrop
            ? 'km-byline__bg'
            : 'km-byline__bg km-byline__bg--waves';
        // The byline's own speed and stillness, if it asked for any, are the
        // picture's and the waves' too.
        byline?.classList.forEach((name) => {
            if (name.startsWith('km-speed--')) overlay.classList.add(name);
        });
        if (prefersStill(byline)) overlay.classList.add('km-byline__bg--still');
        overlay.setAttribute('aria-hidden', 'true');
        if (!backdrop) {
            ['a', 'b', 'c'].forEach((name) => {
                const wave = document.createElement('span');
                wave.className = `km-byline__wave km-byline__wave--${name}`;
                overlay.appendChild(wave);
            });
        }
        if (backdrop) {
            overlay.style.setProperty('--km-byline-image', `url("${urls[0]}")`);
        }
        overlay.style.opacity = BYLINE_BG_HIDDEN;
        if (backdrop && urls.length === 1) {
            overlay.classList.add('km-byline__bg--once');
        }
        return overlay;
    }

    function cycleBackdrop(overlay, urls, byline) {
        const every = (Number(byline.getAttribute('data-km-interval'))
            || BYLINE_BG_INTERVAL_MS) / engine.speedOf(byline);
        let index = 0;
        setInterval(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                index = (index + 1) % urls.length;
                overlay.style.setProperty(
                    '--km-byline-image',
                    `url("${urls[index]}")`,
                );
                // The zoom of the picture starts over with each one.
                overlay.classList.toggle('km-byline__bg--again');
                requestAnimationFrame(() => requestAnimationFrame(() => {
                    overlay.style.opacity = '';
                }));
            }, TIMING.slow() + 50);
        }, every);
    }

    function initBylineBackground() {
        const byline = document.querySelector('.km-byline');
        const main = document.querySelector('.km-layout__content');
        const page = document.querySelector('.km-page__content');
        if (!main || !page) return;

        const backdrop = !!byline && byline.hasAttribute('data-km-backdrop');
        const urls = backdrop
            ? byline.getAttribute('data-km-backdrop')
                .trim().split(/\s+/).filter(Boolean)
            : [];
        if (backdrop && !urls.length) return;
        const anchor = byline
            || page.querySelector('.km-text--lead')
            || page.querySelector('h1');
        if (!anchor) return;

        shuffle(urls);
        main.style.isolation = 'isolate';
        const overlay = createBackdrop(backdrop, urls, byline);
        main.appendChild(overlay);

        const measure = () => {
            const fontSize = parseFloat(getComputedStyle(root).fontSize) || 16;
            const bottom = anchor.getBoundingClientRect().bottom
                + fontSize * ((byline ? -2 : 2) + BYLINE_BG_GROW_REM);
            const height = bottom - main.getBoundingClientRect().top;
            overlay.style.height = `${Math.max(0, height)}px`;
        };

        measure();
        afterLoading(() => setTimeout(() => {
            requestAnimationFrame(() => requestAnimationFrame(() => {
                overlay.style.opacity = '';
            }));
        }, titleHold()));

        window.addEventListener(
            'resize',
            rafThrottle(measure),
            { passive: true },
        );
        new ResizeObserver(measure).observe(main);
        document.fonts.ready.then(measure);
        anchor.addEventListener('animationend', measure);

        if (!backdrop || urls.length === 1 || prefersStill(byline)) return;
        cycleBackdrop(overlay, urls, byline);
    }

