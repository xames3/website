    function initTickers() {
        const batch = Array.from(document.querySelectorAll('.km-ticker'))
            .map((field) => ({
                field,
                ...makeTicker(field, field.textContent),
            }));
        reserveTickerWidths(batch);
        batch.forEach(({ field, count }) => {
            // A ticker given a time keeps it as written, and one that
            // wasn't takes the theme's, which follows the speed dial.
            const duration = parseFloat(
                field.style.getPropertyValue('--km-motion-ticker'),
            ) || engine.ms('ticker', field);
            onVisible([field], () => count(duration), { rootMargin: '0px' });
        });
    }
