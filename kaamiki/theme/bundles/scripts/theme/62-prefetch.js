    // The page a reader is about to open is fetched as they reach for it: a
    // pointer resting on a link, focus on it or a finger on it. When the page
    // is quiet, so are the pages it leads on to (the next and the previous),
    // so following either is instant. It does nothing on a connection set to
    // save data, and `kaamiki.conf.motion.prefetch` turns it off.
    function initPrefetch() {
        if (!root.hasAttribute('data-km-prefetch')) return;
        const link = navigator.connection;
        if (link?.saveData || /(^|-)2g$/.test(link?.effectiveType || '')) {
            return;
        }
        const fetched = new Set();
        const prefetch = (href) => {
            let url;
            try {
                url = new URL(href, window.location.href);
            } catch {
                return;
            }
            const page = url.origin + url.pathname + url.search;
            const here = window.location.origin + window.location.pathname
                + window.location.search;
            if (url.origin !== window.location.origin || page === here
                || fetched.has(page) || !/^https?:$/.test(url.protocol)) return;
            if (/\.[a-z0-9]+$/i.test(url.pathname)
                && !/\.html?$/i.test(url.pathname)) return;
            fetched.add(page);
            const hint = document.createElement('link');
            hint.rel = 'prefetch';
            hint.as = 'document';
            hint.href = url.origin + url.pathname + url.search;
            document.head.append(hint);
        };
        let waiting = 0;
        const reach = (event) => {
            const anchor = event.target.closest?.('a[href]');
            if (!anchor || anchor.target === '_blank') return;
            window.clearTimeout(waiting);
            waiting = window.setTimeout(
                () => prefetch(anchor.href),
                event.type === 'pointerover' ? PREFETCH_HOVER_MS : 0,
            );
        };
        document.addEventListener('pointerover', reach, { passive: true });
        document.addEventListener('focusin', reach, { passive: true });
        document.addEventListener('touchstart', reach, { passive: true });
        document.addEventListener('pointerout', () => {
            window.clearTimeout(waiting);
        }, { passive: true });
        engine.calm(() => {
            document.querySelectorAll(
                'link[rel="next"], link[rel="prev"], '
                + 'a[rel="next"], a[rel="prev"], .km-pagination__link[href]',
            ).forEach((anchor) => prefetch(anchor.href));
        }, PREFETCH_QUIET_MS);
    }

