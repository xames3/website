(function() {
    const root = document.documentElement;
    const classes = root.classList;
    const gate = ['km-document--loading', 'km-document--no-transitions'];
    const held = root.hasAttribute('data-km-handing');
    const entry = performance.getEntriesByType('navigation')[0];
    const local = document.referrer.startsWith(location.origin + '/');
    const arrival = entry?.type === 'back_forward' ? 'history'
        : entry?.type === 'navigate' && local ? 'link' : '';
    if (arrival) root.setAttribute('data-km-arrival', arrival);
    classes.add('km-document--scripted', ...gate);

    function lift() {
        if (classes.contains(gate[0])) classes.remove(...gate);
    }

    function folded() {
        if (classes.contains('km-document--fold-ready')) return;
        if (!document.querySelector('.km-page--clamped')) return;
        classes.add('km-document--fold-failed');
    }

    function loaded() {
        window.setTimeout(folded, 1000);
    }

    window.setTimeout(lift, held ? 5000 : 2000);
    window.addEventListener('load', loaded);
})();
