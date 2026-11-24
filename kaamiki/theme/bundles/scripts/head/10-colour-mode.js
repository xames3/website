(function() {
    const root = document.documentElement;

    function paintColourMode(mode) {
        const { head } = document;
        head.querySelectorAll('meta[name="theme-color"]')
            .forEach((node) => node.remove());
        const add = (content, media) => {
            const node = document.createElement('meta');
            node.name = 'theme-color';
            node.content = content;
            if (media) node.media = media;
            head.append(node);
        };
        if (mode === 'system') {
            add('#ffffff', '(prefers-color-scheme: light)');
            add('#000000', '(prefers-color-scheme: dark)');
        } else {
            add(mode === 'light' ? '#ffffff' : '#000000');
        }
        const scheme = head.querySelector('meta[name="color-scheme"]');
        if (scheme) {
            scheme.content = mode === 'system' ? 'light dark' : mode;
        }
    }

    window.Kaamiki = { paintColourMode };
    try {
        const saved = window.localStorage
            .getItem('km-colour-mode');
        if (['dark', 'light', 'system'].includes(saved)) {
            root.setAttribute('data-km-mode', saved);
            paintColourMode(saved);
        }
    } catch (error) {}
})();
