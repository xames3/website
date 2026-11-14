    function initScrollable() {
        const blocks = Array.from(document.querySelectorAll(
            '.highlight pre, .km-page__content table, .km-table',
        ));
        if (!blocks.length) return;
        const mark = () => {
            blocks.forEach((pre) => {
                const scrolls = pre.scrollWidth > pre.clientWidth + 1
                    || pre.scrollHeight > pre.clientHeight + 1;
                if (scrolls) {
                    pre.setAttribute('tabindex', '0');
                    pre.setAttribute('role', 'region');
                    pre.setAttribute(
                        'aria-label',
                        say(pre.matches('pre') ? 'code' : 'table'),
                    );
                } else {
                    pre.removeAttribute('tabindex');
                    pre.removeAttribute('role');
                    pre.removeAttribute('aria-label');
                }
            });
        };
        const soon = rafThrottle(mark);
        mark();
        document.fonts.ready.then(mark);
        window.addEventListener('resize', soon, { passive: true });
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }

    function initBreadcrumbs() {
        const nav = document.querySelector('.km-breadcrumbs');
        if (!nav) return;
        const links = Array.from(nav.querySelectorAll('.km-breadcrumbs__link'));
        if (links.length < 2) return;

        const separators = links.map((link) => link.previousElementSibling);
        const order = [...links.keys()]
            .slice(1, -1).concat(0, links.length - 1);
        const more = document.createElement('a');
        more.className = 'km-breadcrumbs__link km-breadcrumbs__link--more';
        more.textContent = '...';
        more.hidden = true;
        let gap = null;

        const show = (count) => {
            const out = order.slice(0, count);
            links.forEach((link, index) => {
                link.hidden = out.includes(index);
                if (separators[index]) separators[index].hidden = link.hidden;
            });
            gap?.remove();
            gap = null;
            more.hidden = count === 0;
            if (!count) return;
            const first = Math.min(...out);
            if (separators[first]) {
                gap = separators[first].cloneNode(true);
                gap.hidden = false;
                nav.insertBefore(gap, separators[first]);
                nav.insertBefore(more, separators[first]);
            } else {
                nav.insertBefore(more, links[first]);
            }
            more.href = links[Math.max(...out)].href;
            const names = links
                .flatMap((link, index) => (
                    out.includes(index) ? [link.textContent.trim()] : []
                ))
                .join(', ');
            more.setAttribute('aria-label', names);
            more.title = names;
        };
        const fit = () => {
            nav.classList.add('km-breadcrumbs--measuring');
            let count = 0;
            show(count);
            while (nav.scrollWidth > nav.clientWidth + 1
                && count < order.length) {
                count += 1;
                show(count);
            }
            nav.classList.remove('km-breadcrumbs--measuring');
        };
        const soon = rafThrottle(fit);
        fit();
        document.fonts.ready.then(fit);
        new ResizeObserver(soon).observe(nav.parentElement);
    }

    function initBylineFit() {
        const byline = document.querySelector('.km-byline--align-left');
        if (!byline || !byline.querySelector('.km-byline__language')) return;

        const parts = '.km-byline__profile, .km-byline__reading-time, '
            + '.km-byline__language, .km-byline__copy, .km-byline__source';
        const wraps = () => {
            const centers = Array.from(byline.querySelectorAll(parts))
                .filter((part) => part.getClientRects().length)
                .map((part) => {
                    const box = part.getBoundingClientRect();
                    return box.top + box.height / 2;
                });
            return Math.max(...centers) - Math.min(...centers) > 12;
        };
        const fit = () => {
            byline.classList.remove('km-byline--tight');
            if (wraps()) byline.classList.add('km-byline--tight');
        };
        const soon = rafThrottle(fit);
        fit();
        document.fonts.ready.then(fit);
        new ResizeObserver(soon).observe(byline.parentElement);
    }

    function initColumnFit() {
        const block = ':is([class*="highlight-"], .literal-block-wrapper)';
        const code = `:scope > .km-columns__column > ${block}`;
        const grids = Array.from(document.querySelectorAll('.km-columns'))
            .filter((grid) => grid.querySelector(code));
        if (!grids.length) return;

        const widths = new Map();
        const fit = (grid) => {
            grid.style.removeProperty('--km-columns-count');
            const declared = Number(
                getComputedStyle(grid).getPropertyValue('--km-columns-count'),
            );
            const cells = Array.from(grid.children).filter((cell) => (
                cell.classList.contains('km-columns__column')
            ));
            const room = grid.getBoundingClientRect().width;
            widths.set(grid, room);
            if (declared < 2 || !room || cells.some((cell) => (
                !cell.classList.contains('km-columns__column--span-1')
            ))) return;
            const widest = Math.max(...cells.map((cell) => {
                const saved = cell.getAttribute('style');
                const scrolling = Array.from(
                    cell.querySelectorAll(`:scope > ${block}`),
                );
                cell.style.cssText = 'flex: none; width: max-content; '
                    + 'max-width: none;';
                scrolling.forEach((each) => (
                    each.style.setProperty('contain', 'inline-size')
                ));
                const width = cell.getBoundingClientRect().width;
                scrolling.forEach((each) => {
                    each.style.removeProperty('contain');
                    if (!each.getAttribute('style')) {
                        each.removeAttribute('style');
                    }
                });
                if (saved === null) cell.removeAttribute('style');
                else cell.setAttribute('style', saved);
                return width;
            }));
            const gap = parseFloat(getComputedStyle(grid).columnGap) || 0;
            const count = Math.max(
                1,
                Math.min(declared, Math.floor((room + gap) / (widest + gap))),
            );
            if (count < declared) {
                grid.style.setProperty('--km-columns-count', count);
            }
        };
        const all = () => grids.forEach(fit);
        const watch = new ResizeObserver((entries) => entries.forEach(
            ({ target }) => {
                if (Math.abs(
                    target.getBoundingClientRect().width - widths.get(target),
                ) > 0.5) fit(target);
            },
        ));
        all();
        document.fonts.ready.then(all);
        grids.forEach((grid) => watch.observe(grid));
    }

    function initScrollFades() {
        const kinds = [
            { selector: '.highlight pre', axis: 'x', code: true },
            {
                selector: '.km-page__content table, .km-table, .km-tabs__bar',
                axis: 'x',
            },
            { selector: '.km-sidebar__content', axis: 'y' },
        ];
        const items = [];
        kinds.forEach(({ selector, axis, code }) => {
            document.querySelectorAll(selector).forEach((scroller) => {
                const host = code
                    ? scroller.closest('.highlight') || scroller
                    : scroller;
                host.classList.add('km-fade', `km-fade--${axis}`);
                if (code) host.classList.add('km-fade--code');
                items.push({ scroller, host, axis });
            });
        });
        if (!items.length) return;

        const update = () => {
            items.forEach(({ scroller, host, axis }) => {
                const across = axis === 'x';
                const room = (across
                    ? scroller.scrollWidth - scroller.clientWidth
                    : scroller.scrollHeight - scroller.clientHeight);
                const at = Math.abs(
                    across ? scroller.scrollLeft : scroller.scrollTop,
                );
                host.classList.toggle('km-fade--start', room > 1 && at > 1);
                host.classList.toggle(
                    'km-fade--end',
                    room > 1 && at < room - 1,
                );
            });
        };
        const soon = rafThrottle(update);
        update();
        document.fonts.ready.then(update);
        window.addEventListener('resize', soon, { passive: true });
        document.addEventListener('km:fold', soon);
        const watch = new ResizeObserver(soon);
        items.forEach(({ scroller }) => {
            scroller.addEventListener('scroll', soon, { passive: true });
            watch.observe(scroller);
        });
    }

