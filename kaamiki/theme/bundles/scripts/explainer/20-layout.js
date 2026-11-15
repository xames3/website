    function snapPixel(value) {
        const ratio = window.devicePixelRatio || 1;
        return Math.round(value * ratio) / ratio;
    }

    // The width a walkthrough needs to scroll its notes past its code. It
    // can't need more than it's given, `--km-layout-explainer`, or a site that
    // narrowed that would never get the scrolling view.
    function stageMinWidth() {
        const given = parseFloat(
            getComputedStyle(root).getPropertyValue('--km-layout-explainer'),
        );
        return given > 0
            ? Math.min(STAGE_MIN_WIDTH_PX, given)
            : STAGE_MIN_WIDTH_PX;
    }

    function updateAll() {
        codeExplains.forEach((explainer) => explainer.update());
    }

    const updateSoon = rafThrottle(() => updateAll());

    function measureAll() {
        codeExplains.forEach((explainer) => explainer.measure());
        updateAll();
    }

    function refitAll() {
        codeExplains.forEach((explainer) => {
            if (explainer.shape() !== explainer.shaped) explainer.measure();
        });
        updateAll();
    }

    let settleTimer = 0;

    function settleSoon() {
        window.clearTimeout(settleTimer);
        settleTimer = window.setTimeout(refitAll, RESIZE_SETTLE_MS);
    }

