    function initSearchHighlights() {
        if (!new URLSearchParams(location.search).get('highlight')) return;
        const shown = (mark) => (
            !mark.closest(HIDDEN_PARTS) && mark.getClientRects().length > 0
        );
        const watch = new MutationObserver(() => {
            const marks = Array.from(document.querySelectorAll(
                '.km-page__content span.highlighted',
            ));
            if (!marks.length) return;
            watch.disconnect();
            const first = marks.find(shown)
                || marks.find((mark) => revealHidden(mark));
            if (!first) return;
            first.dispatchEvent(new Event('km:match', { bubbles: true }));
            const center = () => first.scrollIntoView({
                block: 'center',
                behavior: 'instant',
            });
            center();
            const at = window.scrollY;
            document.fonts.ready.then(() => {
                if (window.scrollY === at) center();
            });
        });
        watch.observe(document.body, { childList: true, subtree: true });
        window.setTimeout(() => watch.disconnect(), HIGHLIGHT_WAIT_MS);
    }

