    const tooltipTimers = new WeakMap();

    function flashTooltip(link, message, transient = false) {
        announce(message);
        window.clearTimeout(tooltipTimers.get(link));
        link.setAttribute('data-tooltip', message);
        void link.offsetWidth;
        link.classList.add('km-tooltip', 'km-tooltip--visible');
        tooltipTimers.set(link, window.setTimeout(() => {
            link.classList.remove('km-tooltip--visible');
            if (!transient) return;
            tooltipTimers.set(link, window.setTimeout(
                () => link.removeAttribute('data-tooltip'),
                TIMING.normal(),
            ));
        }, TIMING.tooltipHold()));
    }

    function canonicalUrl(href) {
        const base = document.querySelector('link[rel="canonical"]')?.href
            || window.location.href;
        return href === undefined ? base : new URL(href, base).href;
    }

    function initCopyUrl() {
        document.querySelectorAll('[data-km-copy-url]').forEach((link) => {
            link.addEventListener('click', async (event) => {
                event.preventDefault();
                event.stopPropagation();
                const copied = await copyText(canonicalUrl());
                flashTooltip(link, copied ? say('copied') : say('failed'));
            });
        });
    }

    function measureHeaderLink(link, x) {
        const frame = link.parentElement.getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(link.parentElement);
        const text = range.getBoundingClientRect();
        link.classList.toggle(
            'km-tooltip--below',
            text.top - frame.top < TOOLTIP_ROOM_PX,
        );
        link.style.setProperty(
            '--km-headerlink-top',
            `${text.top - frame.top}px`,
        );
        link.style.setProperty(
            '--km-headerlink-x',
            `${(x ?? text.left) - frame.left}px`,
        );
        return text;
    }

    function headingLink(event) {
        const heading = event.target.closest('h1, h2, h3, h4, h5, h6');
        const link = heading?.querySelector(':scope > a.headerlink');
        if (!link) return null;
        const other = event.target.closest(FOCUSABLE);
        if (other && other !== heading
            && (heading.contains(other)
                || !other.matches('[tabindex]'))) return null;
        if (String(window.getSelection())) return null;
        const text = measureHeaderLink(link, event.clientX);
        return event.clientY >= text.top && event.clientY <= text.bottom
            ? link
            : null;
    }

    function initHeaderLinks() {
        const copying = root.hasAttribute('data-km-copy-links');
        document.querySelectorAll('a.headerlink').forEach((link) => {
            link.parentElement.classList.add('km-page__heading--linked');
        });
        document.addEventListener('focusin', (event) => {
            if (event.target.matches?.('a.headerlink')) {
                measureHeaderLink(event.target);
            }
        });
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a.headerlink');
            if (!link) {
                headingLink(event)?.click();
                return;
            }
            if (event.isTrusted) {
                measureHeaderLink(
                    link,
                    event.detail ? event.clientX : undefined,
                );
            }
            if (!copying) return;
            copyText(canonicalUrl(link.getAttribute('href') || ''))
                .then((copied) => {
                    flashTooltip(
                        link,
                        copied ? say('copied') : say('failed'),
                        true,
                    );
                });
        });
    }

    function dressCopyButton(button) {
        if ('kmDressed' in button.dataset) return;
        button.dataset.kmDressed = '';
        const put = () => {
            if (button.querySelector('.km-copy__icon')) return;
            button.append(...[
                makeIcon('copy', 'km-copy__icon', 'km-copy__icon--copy'),
                makeIcon('copied', 'km-copy__icon', 'km-copy__icon--done'),
            ].filter(Boolean));
        };
        put();
        let release = 0;
        const block = button.closest('div.highlight, .literal-block-wrapper')
            || button;
        const using = () => block.matches(':hover')
            || block.matches(':focus-within')
            || !window.matchMedia('(hover: hover)').matches;
        const follow = () => {
            window.clearTimeout(release);
            if (button.querySelector('.icon-tabler-check')) {
                button.setAttribute('data-km-copied', '');
                return;
            }
            if (!button.hasAttribute('data-km-copied')) return;
            let polls = 0;
            const wait = () => {
                polls += 1;
                if (using() || polls > COPY_HOLD_POLLS
                    || Number(getComputedStyle(button).opacity) <= 0.01) {
                    button.removeAttribute('data-km-copied');
                    return;
                }
                release = window.setTimeout(wait, COPY_HOLD_POLL_MS);
            };
            wait();
        };
        new MutationObserver(() => {
            put();
            follow();
        }).observe(button, { childList: true });
    }

    function initCopyButtonNames() {
        const cells = document.querySelectorAll('div.highlight > pre').length;
        if (!cells) return;
        const name = () => {
            const buttons = document.querySelectorAll('button.copybtn');
            buttons.forEach((button) => {
                dressCopyButton(button);
                if (button.hasAttribute('aria-label')) return;
                const title = button.querySelector('svg title')
                    ?.textContent.trim();
                button.setAttribute(
                    'aria-label',
                    title || button.dataset.tooltip || say('copy'),
                );
            });
            return buttons.length >= cells;
        };
        if (name()) return;
        const watch = new MutationObserver(() => {
            if (name()) watch.disconnect();
        });
        watch.observe(document.body, { childList: true, subtree: true });
        window.addEventListener(
            'load',
            () => setTimeout(() => watch.disconnect(), 5000),
            { once: true },
        );
    }

    function initHighlightedLines() {
        const blocks = [...document.querySelectorAll('.highlight pre')]
            .filter((pre) => pre.querySelector('.hll, .gi, .gd'));
        if (!blocks.length) return;
        const measure = () => {
            blocks.forEach((pre) => (
                pre.style.removeProperty('--km-code-width')
            ));
            const widths = blocks.map((pre) => {
                const { paddingLeft, paddingRight } = getComputedStyle(pre);
                return Math.max(
                    0,
                    pre.scrollWidth
                        - parseFloat(paddingLeft) - parseFloat(paddingRight),
                );
            });
            blocks.forEach((pre, blockIndex) => pre.style.setProperty(
                '--km-code-width',
                `${widths[blockIndex]}px`,
            ));
        };
        const soon = rafThrottle(measure);
        measure();
        document.fonts.ready.then(measure);
        window.addEventListener('resize', soon, { passive: true });
        const watch = new ResizeObserver(soon);
        blocks.forEach((pre) => watch.observe(pre));
    }

