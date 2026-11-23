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

    const MORPH = 'km-morph';
    const LIFT_MS = 200;
    const PARTS = {
        banner: ['.km-related__banner', '.km-page > .km-banner'],
        title: ['.km-related__title', '#km-content > section > h1'],
    };
    let picked = null;

    function save(value) {
        try {
            sessionStorage.setItem(MORPH, JSON.stringify(value));
        } catch {}
    }

    function take() {
        try {
            const found = JSON.parse(sessionStorage.getItem(MORPH));
            sessionStorage.removeItem(MORPH);
            return found;
        } catch {
            return null;
        }
    }

    function letters(node) {
        const box = node.getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(node);
        const text = range.getClientRects()[0] ?? box;
        return {
            size: Number.parseFloat(getComputedStyle(node).fontSize),
            left: box.left,
            top: box.top,
            width: box.width,
            x: text.left - box.left,
            y: text.top - box.top,
        };
    }

    function named(nodes, on) {
        Object.entries(nodes).forEach(([part, node]) => {
            if (!node) return;
            if (on) node.style.viewTransitionName = `${MORPH}-${part}`;
            else node.style.removeProperty('view-transition-name');
        });
    }

    function parts(scope, side) {
        return Object.fromEntries(Object.entries(PARTS).map(
            ([part, selectors]) => [
                part,
                scope.querySelector(selectors[side]),
            ]
        ));
    }

    const arrived = performance.getEntriesByType('navigation')[0]
        ?.type === 'navigate' ? take() : null;
    const morph = arrived?.url === location.href ? arrived : null;
    if (morph) root.setAttribute('data-km-morph', 'lift');

    function land(change) {
        const to = parts(document, 1);
        const tokens = {};
        named(to, true);
        if (to.title) {
            const end = letters(to.title);
            const grow = end.size / morph.size;
            const shift = (a, b, scale) => `translate(${a.x - b.x * scale}px, `
                + `${a.y - b.y * scale}px) scale(${scale})`;
            tokens.grow = shift(end, morph, grow);
            tokens.shrink = shift(morph, end, 1 / grow);
            tokens.from = `${morph.width}px`;
            tokens.to = `${end.width}px`;
            tokens['title-from'] = `translate(${morph.left}px, `
                + `${morph.top}px)`;
            tokens['title-fly'] = 'km-morph-fly-title';
        }
        if (to.banner && morph.banner) {
            const { left, top, width } = morph.banner;
            const scale = width / to.banner.getBoundingClientRect().width;
            tokens['banner-from'] = `translate(${left}px, ${top}px)`;
            tokens['banner-scale'] = `${scale}`;
            tokens['banner-fly'] = 'km-morph-fly-banner';
        }
        Object.entries(tokens).forEach(([token, value]) => {
            root.style.setProperty(`--km-morph-${token}`, value);
        });
        const fly = () => {
            if (root.hasAttribute('data-km-morph')) {
                root.setAttribute('data-km-morph', 'fly');
            }
        };
        const settled = () => requestAnimationFrame(fly);
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', settled, {
                once: true,
            });
        } else settled();
        window.setTimeout(fly, LIFT_MS);
        change.finished.catch(() => {}).then(() => {
            named(to, false);
            Object.keys(tokens).forEach((token) => {
                root.style.removeProperty(`--km-morph-${token}`);
            });
            root.removeAttribute('data-km-morph');
        });
    }

    document.addEventListener('click', (event) => {
        const kaamiki = window.Kaamiki;
        const card = event.target.closest?.('.km-related__card');
        picked = null;
        if (!card || !kaamiki || event.defaultPrevented
            || !('PageRevealEvent' in window)
            || kaamiki.isModifiedClick(event)
            || kaamiki.prefersStill(card)) return;
        picked = card;
        const track = card.parentElement;
        const left = card.offsetLeft - track.scrollLeft;
        if (left >= -1
            && left + card.offsetWidth <= track.clientWidth + 1) return;
        event.preventDefault();
        const go = () => location.assign(card.href);
        kaamiki.glideAcross(track, Math.min(
            card.offsetLeft,
            track.scrollWidth - track.clientWidth
        )).then(go, go);
    });

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
        const card = picked;
        picked = null;
        if (card && card.href === event.activation?.entry?.url) {
            const from = parts(card, 0);
            named(from, true);
            root.setAttribute('data-km-morph', 'leave');
            const { left, top, width } = from.banner
                .getBoundingClientRect();
            save({
                url: card.href,
                banner: { left, top, width },
                ...letters(from.title),
            });
        }
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
        document.querySelectorAll('.km-related__card').forEach((card) => {
            named(parts(card, 0), false);
        });
        root.removeAttribute('data-km-morph');
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
        if (history || !change) {
            root.removeAttribute('data-km-morph');
            return release();
        }
        revealed = true;
        hold();
        if (morph) land(change);
        change.finished.catch(() => {}).then(release);
    });
})();
