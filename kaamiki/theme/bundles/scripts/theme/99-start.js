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
    afterLanding(() => start([
        initSidebar,
        initScrollTop,
        initTabSets,
        initCarousels,
        initShowMore,
        initHeaderSearch,
        initAnchorScrolling,
        initFocusInView,
        initCopyUrl,
        initPrefetch,
        initHeaderLinks,
        initFuzzyBlur,
        initImageZoom,
        initPixelatedBlur,
        initTouchReveal,
        initImageEnlarge,
        initHeaderNavDropdowns,
        initAccordions,
        initHighlightedLines,
        initCodeCopy,
        initScrollable,
        initScrollFades,
        initBreadcrumbs,
        initBylineFit,
        initColumnFit,
        initYouTubeBlocks,
        initYouTubeFacades,
        initVideoFlags,
        initVideoAutoplay,
        initRepositoryWidgets,
        initTickers,
        initTurns,
        initInkReveal,
        initTranscripts,
        initPageReveal,
        initSearchHighlights,
    ]));
})();
