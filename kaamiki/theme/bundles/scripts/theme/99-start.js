    const {
        initShowMore,
        initAccordions,
        initSearchHighlights,
        initRepositoryWidgets,
        initTickers,
        initTurns,
        initInkReveal,
        initTranscripts,
        initPageReveal,
    } = window.Kaamiki;
    Object.freeze(window.Kaamiki);
    const start = (inits) => {
        for (const init of inits) {
            try {
                init();
            } catch (error) {
                console.error(error);
            }
        }
    };
    start([
        initHeaderHeight,
        initHeaderLine,
        initKeyboardModality,
        initColourModes,
        initLogoInvert,
        initNavFit,
    ]);
    start([
        initTabSets,
        initCarousels,
        initShowMore,
        initAnchorScrolling,
        initFuzzyBlur,
        initImageZoom,
        initPixelatedBlur,
        initAccordions,
        initHighlightedLines,
        initScrollFades,
        initBreadcrumbs,
        initBylineFit,
        initColumnFit,
        initVideoFlags,
        initTurns,
        initTranscripts,
    ]);
    afterLanding(() => start([
        initSidebar,
        initScrollTop,
        initHeaderSearch,
        initFocusInView,
        initCopyUrl,
        initPrefetch,
        initHeaderLinks,
        initTouchReveal,
        initImageEnlarge,
        initHeaderNavDropdowns,
        initCodeCopy,
        initScrollable,
        initYouTubeBlocks,
        initYouTubeFacades,
        initVideoAutoplay,
        initRepositoryWidgets,
        initTickers,
        initInkReveal,
        initSearchHighlights,
    ]));
    start([initPageReveal]);
})();
