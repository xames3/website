    function initCodeExplains() {
        document.querySelectorAll('[data-km-code-explain]').forEach((host) => {
            codeExplains.push(createCodeExplain(host));
        });
        if (!codeExplains.length) return;
        measureAll();
        onScroll(updateSoon);

        const panes = new ResizeObserver(settleSoon);
        codeExplains.forEach((explainer) => {
            panes.observe(explainer.pane);
            panes.observe(explainer.track);
        });
        new ResizeObserver(settleSoon).observe(document.body);

        const restage = () => {
            const again = codeExplains.filter((explainer) => (
                explainer.host.getAttribute('data-km-mode') === 'stack'
                && explainer.host.closest('.km-page--clamped') === null
                && window.innerWidth >= stageMinWidth()
                && !prefersStill(explainer.host)
            ));
            if (!again.length) return;
            again.forEach((explainer) => explainer.measure());
            updateAll();
        };
        document.addEventListener('km:fold', () => {
            measureAll();
            requestAnimationFrame(() => requestAnimationFrame(restage));
        });
        window.addEventListener('beforeprint', () => {
            codeExplains.forEach((explainer) => explainer.fillAll());
        });

        let width = window.innerWidth;
        let height = window.innerHeight;
        let resizing = 0;
        window.addEventListener('resize', () => {
            window.clearTimeout(resizing);
            resizing = window.setTimeout(() => {
                const moved = Math.abs(window.innerHeight - height);
                if (window.innerWidth === width && moved < RESIZE_JITTER_PX) {
                    held?.recenter();
                    return;
                }
                width = window.innerWidth;
                height = window.innerHeight;
                measureAll();
            }, RESIZE_SETTLE_MS);
        }, { passive: true });

        window.matchMedia('(prefers-reduced-motion: reduce)')
            .addEventListener('change', measureAll);
        document.fonts.ready.then(measureAll);
        window.addEventListener('load', measureAll, { once: true });
    }

