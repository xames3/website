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

    // Only the explainers near the screen are measured at once; the rest
    // wait until they come near or the page is quiet, so a change of the
    // page's size doesn't hold it while all of them are.
    const stale = new Set();

    function nearScreen(explainer) {
        const box = explainer.host.getBoundingClientRect();
        return box.bottom > -window.innerHeight
            && box.top < 2 * window.innerHeight;
    }

    function keepStill(list) {
        const line = window.innerHeight / 2;
        const spot = document.elementFromPoint(window.innerWidth / 2, line);
        const anchor = spot?.closest('[data-km-code-explain]') || spot;
        const box = anchor?.getBoundingClientRect();
        const share = box?.height ? (line - box.top) / box.height : 0;
        list.forEach((explainer) => explainer.measure());
        if (!anchor || list.includes(held)) return;
        const after = anchor.getBoundingClientRect();
        const drift = after.top + share * after.height - line;
        if (Math.abs(drift) > 0.5) {
            window.scrollBy({ top: drift, behavior: 'instant' });
        }
    }

    let later = false;

    function measureLater() {
        if (later) return;
        later = true;
        engine.calm(function next() {
            const explainer = codeExplains.find((each) => stale.has(each));
            if (!explainer) {
                later = false;
                return;
            }
            stale.delete(explainer);
            keepStill([explainer]);
            updateAll();
            engine.calm(next);
        });
    }

    function measureSome(list) {
        const now = list.filter((explainer) => {
            if (nearScreen(explainer)) {
                explainer.color();
                stale.delete(explainer);
                return true;
            }
            stale.add(explainer);
            return false;
        });
        keepStill(now);
        updateAll();
        if (stale.size) measureLater();
    }

    function refitAll() {
        measureSome(codeExplains.filter((explainer) => (
            explainer.shape() !== explainer.shaped
        )));
    }

    let settleTimer = 0;

    function settleSoon() {
        window.clearTimeout(settleTimer);
        settleTimer = window.setTimeout(refitAll, RESIZE_SETTLE_MS);
    }

