(function() {
    const root = document.documentElement;
    const classes = root.classList;
    const held = () => root.hasAttribute('data-km-handing');
    const entry = performance.getEntriesByType('navigation')[0];
    const local = document.referrer.startsWith(location.origin + '/');
    const arrival = entry?.type === 'back_forward' ? 'history'
        : entry?.type === 'navigate' && local ? 'link' : '';
    if (arrival) root.setAttribute('data-km-arrival', arrival);
    let fonts = false;
    let timer = window.setTimeout(show, held() ? 5000 : 2000);
    classes.add(
        'km-document--scripted',
        'km-document--loading',
        'km-document--no-transitions'
    );

    function show() {
        window.clearTimeout(timer);
        classes.remove(
            'km-document--loading',
            'km-document--no-transitions'
        );
    }

    function settle() {
        if (fonts && !held()) show();
    }

    function ready() {
        const loaded = arrival ? Promise.resolve() : document.fonts.ready;
        requestAnimationFrame(() => loaded.then(() => {
            fonts = true;
            settle();
        }));
    }

    function folded() {
        if (classes.contains('km-document--fold-ready')) return;
        if (!document.querySelector('.km-page--clamped')) return;
        classes.add('km-document--fold-failed');
    }

    function loaded() {
        window.setTimeout(folded, 1000);
    }

    new MutationObserver(() => {
        if (held()) return;
        window.clearTimeout(timer);
        timer = window.setTimeout(show, 2000);
        settle();
    }).observe(root, {
        attributes: true,
        attributeFilter: ['data-km-handing']
    });
    document.addEventListener('DOMContentLoaded', ready, {
        once: true
    });
    window.addEventListener('load', loaded);
})();
