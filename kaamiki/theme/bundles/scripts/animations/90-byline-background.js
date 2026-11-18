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

    const pictures = new Map();

    function preload(url) {
        if (!pictures.has(url)) {
            const picture = new Image();
            picture.src = url;
            pictures.set(url, picture.decode().catch(() => {}));
        }
        return pictures.get(url);
    }

    function showBackdrop(overlay) {
        requestAnimationFrame(() => requestAnimationFrame(() => {
            overlay.style.opacity = '';
        }));
    }

    function cycleBackdrop(overlay, urls, byline) {
        const every = (Number(byline.getAttribute('data-km-interval'))
            || BYLINE_BG_INTERVAL_MS) / engine.speedOf(byline);
        let index = 0;
        let busy = false;
        preload(urls[1]);
        setInterval(async () => {
            if (busy) return;
            busy = true;
            const next = (index + 1) % urls.length;
            await preload(urls[next]);
            overlay.style.opacity = '0';
            setTimeout(() => {
                index = next;
                overlay.style.setProperty(
                    '--km-byline-image',
                    `url("${urls[index]}")`,
                );
                // The zoom of the picture starts over with each one.
                overlay.classList.toggle('km-byline__bg--again');
                showBackdrop(overlay);
                preload(urls[(index + 1) % urls.length]);
                busy = false;
            }, engine.ms('enter') + 50);
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

        // The layout, not the reveal that still moves the title, sets the
        // height, so the picture doesn't jump when the reveal ends.
        const measure = () => {
            const fontSize = parseFloat(getComputedStyle(root).fontSize) || 16;
            let end = anchor.offsetHeight;
            for (let at = anchor; at && at !== main; at = at.offsetParent) {
                end += at.offsetTop;
            }
            // The pictures end where the meta group of the byline ends.
            const height = backdrop
                ? end - parseFloat(getComputedStyle(byline).paddingBottom)
                    - overlay.offsetTop
                : end + fontSize * ((byline ? -2 : 2) + BYLINE_BG_GROW_REM);
            overlay.style.height = `${Math.max(0, height)}px`;
        };

        measure();
        const cycles = backdrop && urls.length > 1 && !prefersStill(byline);
        const ready = backdrop ? preload(urls[0]) : Promise.resolve();
        afterLoading(() => setTimeout(() => ready.then(() => {
            // The zoom and the cycle start when the picture comes in.
            if (backdrop) overlay.classList.toggle('km-byline__bg--again');
            showBackdrop(overlay);
            if (cycles) cycleBackdrop(overlay, urls, byline);
        }), titleHold()));

        window.addEventListener(
            'resize',
            rafThrottle(measure),
            { passive: true },
        );
        new ResizeObserver(measure).observe(main);
        document.fonts.ready.then(measure);
    }

