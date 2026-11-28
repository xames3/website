(function() {
    const root = document.documentElement;
    const classes = root.classList;
    let revealed = false;
    let timer = 0;
    let teardown = null;

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
    const { body } = window.Kaamiki;
    const HOLD_MS = 600;
    const STEADY_MS = 20;
    const STEADY_FRAMES = 3;
    const PEAK_IN_GLIDE = 22 / 38;
    let started = false;
    document.addEventListener('DOMContentLoaded', () => {
        started = true;
    }, { once: true });
    const PARTS = {
        banner: ['.km-related__banner', null],
        stamp: ['.km-related__meta', '.km-page__stamp'],
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
            height: box.height,
            x: text.left - box.left,
            y: text.top - box.top,
        };
    }

    function handover() {
        const bounce = document.getAnimations().find(
            (animation) => animation.animationName === 'km-body-full'
        );
        if (bounce) body.handover(bounce).then(release, () => {});
    }

    function corner(node) {
        const { left, top } = node.getBoundingClientRect();
        return { left, top };
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
                selectors[side] && scope.querySelector(selectors[side]),
            ]
        ));
    }

    const arrived = performance.getEntriesByType('navigation')[0]
        ?.type === 'navigate' ? take() : null;
    const morph = arrived?.url === location.href ? arrived : null;
    if (morph) root.setAttribute('data-km-morph', 'arrive');

    function arrive(change) {
        const to = parts(document, 1);
        const tokens = {};
        const shape = {};
        const frames = {};
        named(to, true);
        if (to.title) {
            const end = letters(to.title);
            const grow = end.size / morph.size;
            const start = 1 / grow;
            const shift = (a, b, scale) => `translate(${a.x - b.x * scale}px, `
                + `${a.y - b.y * scale}px) scale(${scale})`;
            frames['km-morph-shrink'] = `from { transform: ${
                shift(morph, end, start)} }`;
            frames['km-morph-fly-title'] = `from { transform: translate(${
                morph.left}px, ${morph.top}px) }`;
            tokens.from = `${morph.width}px`;
            tokens.to = `${end.width}px`;
            shape.height = `${end.height}px`;
            shape.peak = `${body.peak(start, body.glided(
                getComputedStyle(root)
                    .getPropertyValue('--km-ease-morph-glide').trim(),
                PEAK_IN_GLIDE,
            ))}`;
            tokens['title-fly'] = 'km-morph-fly-title';
        }
        if (to.stamp && morph.stamp) {
            const { left, top } = morph.stamp;
            frames['km-morph-fly-stamp'] = `from { transform: translate(${
                left}px, ${top}px) }`;
            tokens['stamp-fly'] = 'km-morph-fly-stamp';
        }
        const target = to.stamp ?? to.title;
        if (target && morph.banner) {
            const { left, top } = morph.banner;
            const end = corner(target);
            frames['km-morph-fly-banner'] = `from { transform: translate(${
                left}px, ${top}px) } to { transform: translate(${end.left}px, ${
                end.top}px) scale(0) }`;
            tokens['banner-fly'] = 'km-morph-fly-banner';
        }
        Object.entries(tokens).forEach(([token, value]) => {
            root.style.setProperty(`--km-morph-${token}`, value);
        });
        const sheet = document.createElement('style');
        sheet.textContent = [
            ...Object.entries(frames).map(
                ([name, steps]) => `@keyframes ${name} { ${steps} }`
            ),
            `::view-transition-group(${MORPH}-title), `
                + `::view-transition-group(${MORPH}-stamp) { ${
                    Object.entries(shape).map(([token, value]) => (
                        `--km-body-${token}: ${value};`
                    )).join(' ')} }`,
        ].join('\n');
        document.head.append(sheet);
        const fly = () => {
            if (root.getAttribute('data-km-morph') !== 'arrive') return;
            root.setAttribute('data-km-morph', 'fly');
            requestAnimationFrame(handover);
        };
        let last = 0;
        let steady = 0;
        const watch = (now) => {
            if (root.getAttribute('data-km-morph') !== 'arrive') return;
            steady = last && now - last < STEADY_MS ? steady + 1 : 0;
            last = now;
            if (started && steady >= STEADY_FRAMES) fly();
            else requestAnimationFrame(watch);
        };
        change.ready.then(() => requestAnimationFrame(watch))
            .catch(() => {});
        window.setTimeout(fly, HOLD_MS);
        teardown = () => {
            teardown = null;
            named(to, false);
            Object.keys(tokens).forEach((token) => {
                root.style.removeProperty(`--km-morph-${token}`);
            });
            sheet.remove();
            root.removeAttribute('data-km-morph');
        };
        change.finished.catch(() => {})
            .then(() => window.Kaamiki?.entrance?.done)
            .then(() => teardown?.());
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
        const view = track.clientWidth;
        const left = card.offsetLeft - track.scrollLeft;
        const right = left + card.offsetWidth;
        if (left >= -1 && right <= view + 1) return;
        event.preventDefault();
        const go = () => {
            track.style.scrollSnapType = 'none';
            location.assign(card.href);
        };
        kaamiki.glideAcross(track, left < 0
            ? card.offsetLeft
            : card.offsetLeft + card.offsetWidth - view).then(go, go);
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
        teardown?.();
        if (document.querySelector('.km-sidebar--visible')) return;
        const card = picked;
        picked = null;
        if (card && card.href === event.activation?.entry?.url) {
            const from = parts(card, 0);
            card.classList.add('km-related__card--picked');
            named(from, true);
            root.setAttribute('data-km-morph', 'leave');
            save({
                url: card.href,
                banner: corner(from.banner),
                stamp: from.stamp && corner(from.stamp),
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
            card.classList.remove('km-related__card--picked');
            card.parentElement.style.removeProperty('scroll-snap-type');
        });
        root.removeAttribute('data-km-morph');
    });

    // Fires before the first frame, often before deferred
    // scripts have run, and has a transition when the reader
    // came from another page of the site.
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
        if (morph) arrive(change);
        change.finished.catch(() => {}).then(release);
    });
})();
