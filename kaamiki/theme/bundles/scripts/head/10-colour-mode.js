(function() {
    try {
        const saved = window.localStorage
            .getItem('km-colour-mode');
        if (['dark', 'light', 'system'].includes(saved)) {
            document.documentElement
                .setAttribute('data-km-mode', saved);
        }
    } catch (error) {}
})();
