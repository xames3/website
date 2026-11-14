    const repositories = new Map();

    function repositoryData(project) {
        if (!repositories.has(project)) {
            repositories.set(
                project,
                fetchJson(`https://api.github.com/repos/${project}`),
            );
        }
        return repositories.get(project);
    }

    function settleRepository(widget, fields, stats, data) {
        const numbers = fields.map((field) => {
            const value = data[field.getAttribute('data-km-repository-count')];
            return Number.isFinite(value)
                ? Math.max(0, Math.trunc(value))
                : null;
        });
        const counts = numbers.map((number, index) => {
            if (number === null) return null;
            stats[index].hidden = false;
            return buildTicker(fields[index], formatCount(number));
        });

        const still = prefersStill(widget);
        const duration = Math.max(
            1,
            engine.ms(still ? 'fade' : 'enter', widget),
        );
        const timing = { duration, easing: engine.ease(duration) };
        const stagger = engine.ms('stagger', widget);
        const rolling = TIMING.tickerDuration() / engine.speedOf(widget);
        let entered = 0;
        numbers.forEach((number, index) => {
            if (number === null) return;
            const delay = entered * stagger;
            entered += 1;
            stats[index].animate(
                { opacity: [0, 1] },
                { ...timing, delay, fill: 'backwards' },
            );
            const begin = () => counts[index](rolling);
            if (delay) window.setTimeout(begin, delay);
            else begin();
        });
    }

    async function loadRepository(widget) {
        const project = widget.getAttribute('data-km-repository');
        const fields = Array.from(
            widget.querySelectorAll('[data-km-repository-count]'),
        );
        if (!project || !fields.length) return;

        const stats = fields.map((field) => field.closest('p'));
        stats.forEach((stat) => stat.setAttribute('aria-busy', 'true'));
        const data = await repositoryData(project) || {};
        try {
            settleRepository(widget, fields, stats, data);
        } finally {
            stats.forEach((stat) => stat.removeAttribute('aria-busy'));
        }
    }

    function initRepositoryWidgets() {
        onVisible(
            document.querySelectorAll(
                '.km-repository[data-km-repository]',
            ),
            loadRepository,
            { rootMargin: '0px 0px -10% 0px' },
        );
    }
