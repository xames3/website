(function() {
    const TYPES = [
        'pointerdown',
        'pointerover',
        'pointerout',
        'pointermove',
        'pointerup',
        'pointercancel',
        'touchstart',
        'touchmove',
        'touchend',
        'touchcancel',
        'wheel',
    ];
    const PASSIVE = /^(touch|wheel)/;
    const handlers = new Map([[document, new Map()], [window, new Map()]]);

    handlers.forEach((types, target) => {
        TYPES.forEach((type) => [true, false].forEach((capture) => {
            const set = new Set();
            types.set(`${type} ${capture}`, set);
            target.addEventListener(type, (event) => {
                Array.from(set).forEach((fn) => {
                    if (!set.has(fn)) return;
                    try {
                        fn(event);
                    } catch (error) {
                        reportError(error);
                    }
                });
            }, { capture, passive: PASSIVE.test(type) });
        }));
    });

    function onPage(target, type, fn, capture = false) {
        const set = handlers.get(target).get(`${type} ${capture}`);
        set.add(fn);
        return () => set.delete(fn);
    }

    window.Kaamiki = { ...window.Kaamiki, onPage };
})();
