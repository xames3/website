    function accordionFold(details, summary, content, index) {
        const CLAMPED = 'km-accordion--clamped';
        const CLAMPING = 'km-accordion--clamping';
        const LONG = 'km-accordion--long';
        let body = null;
        let shell = null;
        let button = null;
        let label = null;
        let motion = null;
        let idle = null;
        let expanded = false;
        let turn = 0;

        const tail = () => (button ? button.getBoundingClientRect().height : 0);

        const limit = () => {
            const style = getComputedStyle(content);
            const chrome = body
                ? details.getBoundingClientRect().height
                    - body.getBoundingClientRect().height
                : summary.getBoundingClientRect().height
                    + parseFloat(style.paddingTop)
                    + parseFloat(style.paddingBottom) + tail();
            return Math.max(
                CLAMP_ACCORDION_MIN_PX,
                Math.round(stableHeight() - headerHeight() - chrome),
            );
        };

        const full = () => {
            if (!body) {
                const style = getComputedStyle(content);
                return content.getBoundingClientRect().height
                    - parseFloat(style.paddingTop)
                    - parseFloat(style.paddingBottom);
            }
            const bottoms = Array.from(
                body.children,
                (_) => _.getBoundingClientRect().bottom,
            );
            return Math.max(0, ...bottoms) - body.getBoundingClientRect().top;
        };

        const name = (next) => {
            button.setAttribute('aria-expanded', String(next));
            label.textContent = next ? say('less') : say('more');
        };

        const toggle = (next, animate = true) => {
            if (next === expanded) return;
            expanded = next;
            name(next);
            if (next) idle.stir();
            else idle.rest();
            const start = body.getBoundingClientRect().height;
            const current = ++turn;
            motion.stop();
            if (next) {
                const height = full();
                if (!animate || prefersStill(details)) {
                    motion.settle(true);
                    return;
                }
                const room = viewportHeight()
                    - body.getBoundingClientRect().top;
                motion.resize(
                    true,
                    start,
                    Math.min(height, Math.max(start, room, viewportHeight())),
                );
                return;
            }
            const collapsed = Math.min(start, limit());
            const keep = () => (
                keepInView(body, collapsed, tail() + showMoreDock())
            );
            if (!animate || prefersStill(details)) {
                keep();
                motion.settle(false);
                return;
            }
            keep().then(() => {
                if (current !== turn) return;
                const shown = viewportHeight()
                    - body.getBoundingClientRect().top;
                motion.resize(
                    false,
                    Math.min(start, Math.max(collapsed, shown)),
                    collapsed,
                );
            });
        };

        const measure = () => {
            if (!details.open || details.dataset.kmWhole) return;
            if (details.classList.contains('km-accordion--animating')
                || details.classList.contains(CLAMPING)) return;
            const height = full();
            if (height < stableHeight() || height - limit() < CLAMP_SLACK_PX) {
                if (!body) return;
                expanded = false;
                name(false);
                idle.rest();
                details.classList.remove(LONG, CLAMPED);
                return;
            }
            build();
            details.classList.add(LONG);
            details.style.setProperty('--km-accordion-clamp', `${limit()}px`);
            if (!expanded) details.classList.add(CLAMPED);
        };

        const soon = rafThrottle(measure);

        const build = () => {
            if (body) return;
            body = document.createElement('div');
            body.className = 'km-accordion__fold';
            body.id = `km-accordion-fold-${index}`;
            body.append(...content.childNodes);
            shell = document.createElement('div');
            shell.className = 'km-accordion__more';
            button = document.createElement('button');
            button.type = 'button';
            button.className = 'km-accordion__more-button';
            button.setAttribute('aria-controls', body.id);
            label = document.createElement('span');
            label.className = 'km-accordion__more-label';
            const icon = document.createElement('i');
            icon.className = `${root.dataset.kmMoreIcon} `
                + 'km-accordion__more-icon';
            icon.setAttribute('aria-hidden', 'true');
            button.append(label, icon);
            shell.append(button);
            content.append(body, shell);
            name(false);
            motion = foldMotion(details, body, CLAMPED, CLAMPING, (next) => {
                details.classList.toggle(CLAMPED, next);
            });
            idle = idleShell(
                shell,
                button,
                'km-accordion__more--idle',
                () => expanded && details.open,
            );
            button.addEventListener('click', () => toggle(!expanded));
            const reach = (event) => {
                if (expanded || !details.classList.contains(CLAMPED)) return;
                if (event.target.getBoundingClientRect().bottom
                    > shell.getBoundingClientRect().top) {
                    toggle(true, false);
                }
            };
            body.addEventListener('focusin', reach);
            body.addEventListener('km:match', reach);
            const watch = new ResizeObserver(soon);
            Array.from(body.children).forEach((child) => watch.observe(child));
        };

        const reset = () => {
            if (!body || !expanded) return;
            expanded = false;
            name(false);
            idle.rest();
            motion.settle(false);
        };

        // The work a first open has to do (finding out whether the content
        // is long and, if it is, building its fold) done ahead of the click:
        // open it and shut it again inside one task, so nothing is painted.
        let warmed = false;
        const warm = () => {
            if (warmed || details.open || details.dataset.kmWhole) return;
            if (!details.getClientRects().length) return;
            warmed = true;
            const scrolled = window.scrollY;
            details.open = true;
            measure();
            details.open = false;
            if (window.scrollY !== scrolled) window.scrollTo(0, scrolled);
        };

        window.addEventListener('resize', soon, { passive: true });
        new ResizeObserver(soon).observe(content);
        document.fonts.ready.then(soon);
        return { measure, reset, warm };
    }

    function groupRivals(details) {
        const group = details.dataset.kmGroup;
        if (!group) return [];
        const open = document.querySelectorAll(
            `details.km-accordion[data-km-group="${CSS.escape(group)}"][open]`,
        );
        return Array.from(open).filter((other) => (
            !other.contains(details) && !details.contains(other)
        ));
    }

    const accordionFolds = new Map();

    function revealHidden(target) {
        let opened = false;
        for (let host = target; host; host = host.parentElement) {
            if (host.matches('.km-tabs__panel')) {
                const input = document.getElementById(host.dataset.kmTab);
                if (input && !input.checked) {
                    input.checked = true;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    opened = true;
                }
                continue;
            }
            if (!host.matches('details.km-accordion') || host.open) continue;
            groupRivals(host).forEach((other) => {
                other.open = false;
                accordionFolds.get(other)?.reset();
            });
            host.open = true;
            accordionFolds.get(host)?.measure();
            opened = true;
        }
        return opened;
    }

    function initAccordions() {
        // The ones within a screen of the reader are made ready when the
        // page is quiet, so a click on any of them is cheap.
        const ahead = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;
                ahead.unobserve(entry.target);
                const details = entry.target.closest('details.km-accordion');
                engine.calm(() => accordionFolds.get(details)?.warm());
            });
        }, { rootMargin: '100% 0px' });

        const accordions = document.querySelectorAll('details.km-accordion');
        accordions.forEach((details, index) => {
            const summary = details.querySelector(':scope > summary');
            const content = details
                .querySelector(':scope > .km-accordion__body');
            if (!summary || !content) return;
            const fold = accordionFold(details, summary, content, index);
            accordionFolds.set(details, fold);
            engine.intent(summary, fold.warm);
            ahead.observe(summary);

            let running = null;
            let wanted = details.open;

            const finish = (opening) => {
                details.classList.remove(
                    'km-accordion--animating',
                    'km-accordion--closing',
                );
                if (opening) {
                    // After the last frame has been painted, not in it.
                    requestAnimationFrame(() => engine.idle(
                        () => fold.measure(),
                        600,
                    ));
                    return;
                }
                details.open = false;
                fold.reset();
            };

            const frames = (from, to) => ({
                height: [`${from.height}px`, `${to.height}px`],
                paddingTop: [`${from.top}px`, `${to.top}px`],
                paddingBottom: [`${from.bottom}px`, `${to.bottom}px`],
                opacity: [from.opacity, to.opacity],
            });

            // Where an opening ends up has to be where the content really
            // ends (as far as the screen shows), whichever way it got here:
            // turned round twice, it comes back to the height it was left at,
            // and stopping there would snap the rest in. So it carries on.
            const landed = (opening) => (arrived) => {
                const held = parseFloat(arrived.frames.height?.[1]);
                arrived.animation.cancel();
                running = null;
                if (opening && Number.isFinite(held)) {
                    const natural = content.getBoundingClientRect().height;
                    const room = viewportHeight()
                        - content.getBoundingClientRect().top;
                    const reach = Math.min(natural, Math.max(room, held));
                    if (reach - held > 4) {
                        running = engine.length(
                            content,
                            'height',
                            held,
                            reach,
                            {
                                role: 'content',
                                onDone: (carried) => {
                                    carried.animation.cancel();
                                    running = null;
                                    finish(true);
                                },
                            },
                        );
                        return;
                    }
                }
                finish(opening);
            };

            summary.addEventListener('click', (event) => {
                if (isModifiedClick(event)) return;
                event.preventDefault();

                const opening = running ? !wanted : !details.open;
                wanted = opening;
                if (opening) {
                    const rivals = groupRivals(details);
                    // The one pressed stays where it is on the screen while
                    // the one open above it closes.
                    if (rivals.length) {
                        holdPlace(summary, () => !rivals.some((other) => (
                            other.classList.contains('km-accordion--animating')
                        )));
                    }
                    rivals.forEach((other) => {
                        if (other.classList.contains(
                            'km-accordion--closing',
                        )) return;
                        other.querySelector(':scope > summary')?.click();
                    });
                }
                details.classList.toggle('km-accordion--closing', !opening);
                // Clicked again on the way, it turns round from where it
                // is and at the speed it's going.
                if (running) {
                    running = running.reverse({ onDone: landed(opening) });
                    return;
                }
                if (opening && !details.open) {
                    details.open = true;
                    fold.measure();
                }
                if (prefersStill(details)) {
                    finish(opening);
                    if (opening) {
                        content.animate(
                            [{ opacity: 0 }, { opacity: 1 }],
                            { duration: 150, easing: 'ease-out' },
                        );
                    }
                    return;
                }

                details.classList.add('km-accordion--animating');
                const style = getComputedStyle(content);
                const top = parseFloat(style.paddingTop);
                const bottom = parseFloat(style.paddingBottom);
                const box = content.getBoundingClientRect();
                const room = Math.max(0, viewportHeight() - box.top);
                const shut = { height: 0, top: 0, bottom: 0, opacity: 0 };
                const open = {
                    height: Math.min(
                        box.height,
                        Math.max(room, viewportHeight()),
                    ),
                    top,
                    bottom,
                    opacity: 1,
                };
                if (!opening) {
                    open.height = Math.min(box.height, room);
                    open.top = top;
                    open.bottom = bottom;
                }
                // It closes quicker than it opens, so the gap the content
                // leaves behind doesn't take long to close.
                running = engine.animate(
                    content,
                    opening ? frames(shut, open) : frames(open, shut),
                    {
                        role: 'content',
                        duration: engine.ms('content', details)
                            * (opening ? 1 : 0.65),
                        onDone: landed(opening),
                    },
                );
            });

            if (details.open) fold.measure();
        });

        const fromHash = () => {
            const id = decodeId(location.hash.slice(1));
            const target = id ? document.getElementById(id) : null;
            if (revealHidden(target)) target.scrollIntoView();
        };

        fromHash();
        window.addEventListener('hashchange', fromHash);
        document.addEventListener('click', (event) => {
            if (isModifiedClick(event)) return;
            const link = event.target.closest?.('a[href^="#"]');
            const id = link
                ? decodeId((link.getAttribute('href') || '').slice(1))
                : '';
            if (id) revealHidden(document.getElementById(id));
        }, true);
    }

