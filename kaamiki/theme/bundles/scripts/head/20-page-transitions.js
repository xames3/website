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
    const menus = () => document.querySelectorAll(
        '.km-header__nav-group > ul'
    );
    window.addEventListener('pageswap', (event) => {
        if (!event.viewTransition) return;
        Array.from(menus()).find((menu) => (
            getComputedStyle(menu).display !== 'none'
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
        // cache is whole already, with no content to show
        // in once the old one has left.
        if (revealed && change) change.skipTransition();
        if (revealed || !change) return release();
        revealed = true;
        let back = false;
        try {
            const move = window.navigation.activation;
            back = move.navigationType === 'traverse' &&
                move.entry.index < move.from.index;
        } catch (error) {}
        root.setAttribute(
            'data-km-nav',
            back ? 'back' : 'forward'
        );
        hold();
        const loaded = new Promise((resolve) => {
            if (document.readyState === 'complete') {
                resolve();
            } else {
                window.addEventListener('load', resolve, {
                    once: true
                });
            }
        }).then(() => document.fonts.ready);
        const picture = (move, name) => (
            move.effect &&
            move.effect.pseudoElement === name
        );
        const nearly = (move) => new Promise((resolve) => {
            const check = () => {
                const length = move.effect
                    .getComputedTiming().duration;
                if (move.playState === 'finished' ||
                    move.currentTime >= length * 0.95) {
                    resolve();
                } else {
                    window.requestAnimationFrame(check);
                }
            };
            check();
        });
        change.ready.then(() => {
            const moving = document.getAnimations();
            return Promise.all([
                loaded,
                ...moving
                .filter((move) => picture(
                    move,
                    '::view-transition-old(km-content)'
                ))
                .map(nearly),
            ]).then(() => moving
                .filter((move) => [
                    '::view-transition-old(root)',
                    '::view-transition-old(km-dropdown)',
                ].some((name) => picture(move, name)))
                .forEach((move) => move.finish()));
        }).catch(() => {}).then(release);
        change.finished.catch(() => {}).then(release);
    });
})();
