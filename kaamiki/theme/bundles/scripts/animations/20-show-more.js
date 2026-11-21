    function initShowMore() {
        const page = document.querySelector('.km-page--clamped');
        if (!page) return;
        const content = page.querySelector('.km-page__content');
        const shell = page.querySelector('[data-km-show-more]');
        const button = shell?.querySelector('.km-page__more-button');
        const label = button?.querySelector('.km-page__more-label');
        if (!content || !shell || !button) return;
        if (getComputedStyle(shell).display === 'none') {
            page.classList.remove('km-page--clamped');
            return;
        }

        content.querySelectorAll('img[loading="lazy"]').forEach((image) => {
            image.loading = 'eager';
        });

        let expanded = false;
        let whole = false;

        const tail = () => (
            button.getBoundingClientRect().height + showMoreDock()
        );

        const fit = () => {
            const top = window.scrollY + content.getBoundingClientRect().top;
            const room = Math.round(
                Math.max(CLAMP_MIN_PX, stableHeight() - top - tail()),
            );
            page.style.setProperty('--km-show-more-clamp', `${room}px`);
            return { top, room };
        };

        let folded = true;
        const fold = (next) => {
            page.classList.toggle('km-page--clamped', next);
            if (next === folded) return;
            folded = next;
            document.dispatchEvent(new Event('km:fold'));
        };

        const measure = () => {
            content.style.maxHeight = '';
            page.classList.remove('km-page--clamped');
            const full = content.getBoundingClientRect().height;
            page.classList.add('km-page--clamped');
            return full;
        };

        const judge = (first = false) => {
            if (page.classList.contains('km-page--clamping')) return;
            shell.hidden = false;
            const { top, room } = fit();
            const full = page.classList.contains('km-page--clamped')
                ? measure()
                : content.getBoundingClientRect().height;
            const more = stableHeight() >= CLAMP_MIN_SCREEN_PX
                && full - room >= CLAMP_SLACK_PX;
            const reading = window.scrollY + viewportHeight()
                > top + room + tail() + 1;
            if (more && whole && !first && !expanded && reading) {
                shell.hidden = true;
                return;
            }
            whole = !more;
            shell.hidden = whole;
            fold(more && !expanded);
        };

        const refit = rafThrottle(() => judge());

        let deferred = false;
        const refitCalm = () => {
            if (!root.classList.contains('km-document--loading')
                && !document.querySelector(`.${REVEAL_WAITING}`)) {
                refit();
                return;
            }
            if (deferred) return;
            deferred = true;
            engine.calm(() => {
                deferred = false;
                refit();
            });
        };

        const motion = foldMotion(
            page,
            content,
            'km-page--clamped',
            'km-page--clamping',
            (next) => {
                fold(next);
                refit();
            },
        );

        judge(true);

        const { stir, rest } = idleShell(
            shell,
            button,
            'km-page__more--idle',
            () => expanded && !whole,
        );
        let turn = 0;

        const toggle = (next, animate = true) => {
            if (next === expanded || whole) return;
            expanded = next;
            attempt(() => {
                history.replaceState(
                    { ...history.state, kmExpanded: next },
                    '',
                );
                history.scrollRestoration = next ? 'manual' : 'auto';
            });
            button.setAttribute('aria-expanded', next ? 'true' : 'false');
            const relabel = () => {
                if (!label || current !== turn) return;
                label.textContent = next
                    ? button.dataset.kmLabelLess
                    : button.dataset.kmLabelMore;
            };
            if (next) stir();
            else rest();

            const start = content.getBoundingClientRect().height;
            const current = ++turn;
            motion.stop();
            if (next) {
                const full = measure();
                page.classList.remove('km-page--clamped');
                if (!animate || prefersReducedMotion()) {
                    motion.settle(true);
                    relabel();
                    return;
                }
                const roomPx = viewportHeight()
                    - content.getBoundingClientRect().top;
                motion.resize(
                    true,
                    start,
                    Math.min(full, Math.max(start, roomPx, viewportHeight())),
                ).then(relabel);
                return;
            }
            const clampValue = page.style
                .getPropertyValue('--km-show-more-clamp');
            const collapsed = Math.min(start, toPx(clampValue));
            if (!animate || prefersReducedMotion()) {
                keepInView(content, collapsed, tail());
                motion.settle(false);
                relabel();
                return;
            }
            motion.close(collapsed, shell).then(relabel);
        };

        const blocks = () => content.querySelectorAll(PLACE_BLOCKS);

        const mark = () => {
            const all = Array.from(blocks());
            const index = all.findIndex((block) => {
                const box = block.getBoundingClientRect();
                return box.bottom > 0 && box.height > 0;
            });
            if (index < 0) return null;
            const box = all[index].getBoundingClientRect();
            return { index, share: -box.top / box.height };
        };

        const keep = (place) => {
            const block = blocks()[place?.index];
            if (!block) return;
            const box = block.getBoundingClientRect();
            window.scrollBy({
                top: box.top + place.share * box.height,
                behavior: 'instant',
            });
            let height = 0;
            let still = 0;
            holdPlace(block, () => {
                const now = content.getBoundingClientRect().height;
                if (now !== height) {
                    height = now;
                    still = performance.now();
                }
                return document.readyState === 'complete'
                    && performance.now() - still > PLACE_SETTLE_MS;
            }, place.share);
        };

        const save = () => {
            if (!expanded) return;
            attempt(() => history.replaceState(
                { ...history.state, kmPlace: mark() },
                '',
            ));
        };
        let saving = 0;

        const holds = (href) => {
            if (!href.startsWith('#') || href.length < 2) return false;
            const target = document.getElementById(decodeId(href.slice(1)));
            return !!target && target !== content && content.contains(target);
        };

        button.addEventListener('click', () => toggle(!expanded));

        document.addEventListener('click', (event) => {
            if (expanded || whole) return;
            const link = event.target.closest?.('a[href]');
            if (!link || !holds(link.getAttribute('href') || '')) return;
            toggle(true, false);
        }, true);

        window.addEventListener('hashchange', () => {
            if (expanded || whole || !holds(location.hash)) return;
            toggle(true, false);
            settleHash();
        });

        const buried = (node) => {
            const element = node?.nodeType === Node.ELEMENT_NODE
                ? node
                : node?.parentElement;
            if (expanded || whole || !element
                || !content.contains(element)) return false;
            return element.getBoundingClientRect().bottom
                > shell.getBoundingClientRect().top;
        };

        document.addEventListener('focusin', (event) => {
            if (buried(event.target)) toggle(true, false);
        });

        document.addEventListener('selectionchange', () => {
            const selection = document.getSelection();
            if (selection && !selection.isCollapsed
                && buried(selection.focusNode)) {
                toggle(true, false);
            }
        });

        document.addEventListener('km:match', (event) => {
            if (buried(event.target)) toggle(true, false);
        });

        window.addEventListener('resize', refit, { passive: true });
        window.addEventListener('load', refitCalm, { once: true });
        new ResizeObserver(refitCalm).observe(document.body);
        document.fonts.ready.then(refitCalm);
        document.fonts.addEventListener?.('loadingdone', refitCalm);

        onScroll(() => {
            window.clearTimeout(saving);
            saving = window.setTimeout(save, PLACE_SAVE_MS);
        });
        window.addEventListener('pagehide', save);

        if (holds(location.hash)
            || history.state?.kmExpanded) toggle(true, false);
        if (expanded) keep(history.state?.kmPlace);
        root.classList.add('km-document--fold-ready');
    }

