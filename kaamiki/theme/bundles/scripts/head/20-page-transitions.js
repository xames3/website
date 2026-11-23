(function() {
    const root = document.documentElement;
    const classes = root.classList;
    let revealed = false;
    let timer = 0;

    function release() {
        revealed = true;
        window.clearTimeout(timer);
        root.removeAttribute('data-km-handing');
    }

    function hold() {
        window.clearTimeout(timer);
        timer = window.setTimeout(release, 4500);
    }

    if ('PageRevealEvent' in window) {
        root.setAttribute('data-km-handing', '');
        hold();
    }

    // The old page names its content and an open dropdown so
    // they can be pictured as they were, and gives the names
    // up if it's shown again from the back and forward cache.
    // With the sidebar open, nothing is named and the old page
    // stays whole, sidebar on top, until the new one takes over.
    const menus = () => document.querySelectorAll(
        '.km-header__nav-group > ul'
    );
    window.addEventListener('pageswap', (event) => {
        if (!event.viewTransition) return;
        if (event.activation?.navigationType === 'traverse') {
            event.viewTransition.skipTransition();
            return;
        }
        if (document.querySelector('.km-sidebar--visible')) return;
        Array.from(menus()).find((menu) => (
            getComputedStyle(menu).visibility !== 'hidden'
        ))?.style.setProperty(
            'view-transition-name',
            'km-dropdown'
        );
        const content = document.querySelector(
            '.km-layout__content'
        );
        const header = document.querySelector('.km-header');
        if (content && header) {
            const box = content.getBoundingClientRect();
            const top = header.getBoundingClientRect()
                .bottom - box.top;
            const bottom = box.bottom - window.innerHeight;
            content.style.clipPath = 'inset(' +
                `${Math.max(0, top)}px -100vmax ` +
                `${Math.max(0, bottom)}px -100vmax)`;
        }
        classes.add('km-document--leaving');
    });

    window.addEventListener('pageshow', (event) => {
        if (!event.persisted) return;
        classes.remove('km-document--leaving');
        document.querySelector('.km-layout__content')
            ?.style.removeProperty('clip-path');
        menus().forEach((menu) => {
            menu.style.removeProperty('view-transition-name');
        });
    });

    // Fires with the first frame, after deferred scripts
    // have run, and has a transition when the reader came
    // from another page of the site.
    window.addEventListener('pagereveal', (event) => {
        const change = event.viewTransition;
        // A page shown again from the back and forward
        // cache, or reached from the history, is whole
        // already, with no content to show in once the old
        // one has left.
        const history = revealed || root.getAttribute(
            'data-km-arrival'
        ) === 'history';
        if (history && change) change.skipTransition();
        if (history || !change) return release();
        revealed = true;
        hold();
        change.finished.catch(() => {}).then(release);
    });
})();
