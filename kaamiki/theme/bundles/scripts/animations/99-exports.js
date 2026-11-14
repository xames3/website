    function screenHeight() {
        const probe = document.createElement('div');
        probe.style.cssText = 'position: absolute; top: 0; width: 0; '
            + 'height: 100lvh; visibility: hidden;';
        document.body.append(probe);
        const height = probe.getBoundingClientRect().height;
        probe.remove();
        return height || window.innerHeight;
    }

    Object.assign(window.Kaamiki, {
        initShowMore,
        initAccordions,
        initSearchHighlights,
        initRepositoryWidgets,
        initTickers,
        initSwaps,
        initInkReveal,
        initTranscripts,
        initPageReveal,
        initBylineBackground,
    });
})();
