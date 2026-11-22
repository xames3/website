    function initCarousels() {
        const carousels = document.querySelectorAll('[data-km-carousel]');
        const placing = new Set();
        let placeFrame = 0;
        const placeAll = () => {
            placeFrame = 0;
            const parts = Array.from(placing);
            placing.clear();
            parts.forEach((part) => part.open());
            const sizes = parts.map((part) => part.read());
            parts.forEach((part, index) => part.close(sizes[index]));
        };
        carousels.forEach((carousel) => {
            const track = carousel.querySelector('.km-carousel__track');
            const [back, forward] = carousel.querySelectorAll(
                '[data-km-carousel-step]',
            );
            const items = () => Array.from(track.children)
                .filter((item) => item.offsetWidth > 0);
            const room = () => track.scrollWidth - track.clientWidth;
            let aim = null;
            let moved = () => {};
            const goTo = (left) => {
                if (prefersStill(carousel)) {
                    track.scrollTo({ left });
                    return Promise.resolve();
                }
                aim = left;
                return glideAcross(track, left).then(() => {
                    if (aim === left) aim = null;
                });
            };
            const step = (way) => {
                const at = aim ?? track.scrollLeft;
                const stops = items().map((item) => Math.min(
                    item.offsetLeft,
                    room(),
                ));
                return way > 0
                    ? goTo(stops.find((stop) => stop > at + 1) ?? room())
                    : goTo(stops.findLast((stop) => stop < at - 1) ?? 0);
            };
            const name = () => carousel.getAttribute('aria-label')
                || document.getElementById(
                    carousel.getAttribute('aria-labelledby'),
                )?.textContent.trim() || '';
            const update = () => {
                const left = room();
                const at = track.scrollLeft;
                const still = left <= 1;
                carousel.classList.toggle('km-carousel--still', still);
                if (still) {
                    track.removeAttribute('tabindex');
                    track.removeAttribute('role');
                    track.removeAttribute('aria-label');
                } else {
                    track.setAttribute('tabindex', '0');
                    track.setAttribute('role', 'group');
                    track.setAttribute('aria-label', name());
                }
                back?.setAttribute('aria-disabled', String(at <= 1));
                forward?.setAttribute('aria-disabled', String(at >= left - 1));
            };
            [back, forward].forEach((button) => {
                button?.addEventListener('click', () => {
                    if (button.getAttribute('aria-disabled') === 'true') {
                        return;
                    }
                    moved(step(Number(button.dataset.kmCarouselStep)));
                });
            });
            track.addEventListener('keydown', (event) => {
                if (event.target !== track || event.altKey || event.ctrlKey
                    || event.metaKey || event.shiftKey) return;
                if (event.key === 'ArrowRight') moved(step(1));
                else if (event.key === 'ArrowLeft') moved(step(-1));
                else return;
                event.preventDefault();
            });
            track.addEventListener('focusin', (event) => {
                const item = items().find(
                    (each) => each.contains(event.target),
                );
                if (!item) return;
                const at = track.scrollLeft;
                if (item.offsetLeft < at - 1
                    || item.offsetLeft + item.offsetWidth
                        > at + track.clientWidth + 1) {
                    track.scrollTo({
                        left: Math.min(item.offsetLeft, room()),
                        behavior: 'instant',
                    });
                }
            });
            const title = carousel.querySelector('.km-carousel__title');
            const nav = carousel.querySelector('.km-carousel__nav');
            const part = {
                open: () => {
                    carousel.classList.add('km-carousel--measuring');
                    nav.style.display = 'flex';
                },
                read: () => ({
                    wide: title.getBoundingClientRect().width
                        + nav.getBoundingClientRect().width
                        + parseFloat(getComputedStyle(root).fontSize),
                    line: title.offsetTop + title.offsetHeight
                        - parseFloat(getComputedStyle(title).lineHeight) / 2
                        - nav.offsetHeight / 2,
                    room: carousel.clientWidth,
                }),
                close: ({ wide, line, room: width }) => {
                    nav.style.display = '';
                    carousel.classList.remove('km-carousel--measuring');
                    const inline = wide <= width;
                    carousel.classList.toggle('km-carousel--inline', inline);
                    nav.style.insetBlockStart = inline ? `${line}px` : '';
                },
            };
            const place = () => {
                if (!title || !nav) return;
                placing.add(part);
                placeFrame ||= requestAnimationFrame(placeAll);
            };
            // With `:dots:` a dot stands for each card under the row, in place
            // of the arrows, and a pill stretches from the dot it was on to
            // the one it reaches: the edge on the way leaves first and the
            // other follows, so it elongates, then settles. They're for the
            // eye and a tap, the keys and a swipe are what's for the rest.
            const dots = carousel.querySelector('.km-carousel__dots');
            const pill = document.createElement('span');
            pill.className = 'km-carousel__pill';
            let marked = -1;
            const dotsFor = () => {
                const cards = items();
                if (dots.children.length === cards.length + 1) return;
                dots.replaceChildren(pill);
                marked = -1;
                cards.forEach((card) => {
                    const dot = document.createElement('button');
                    dot.type = 'button';
                    dot.tabIndex = -1;
                    dot.className = 'km-carousel__dot';
                    dot.addEventListener('click', () => moved(goTo(
                        Math.min(card.offsetLeft, room()),
                    )));
                    dots.append(dot);
                });
            };
            const nearest = () => {
                const at = track.scrollLeft;
                let index = 0;
                let best = Infinity;
                items().forEach((card, position) => {
                    const start = Math.min(card.offsetLeft, room());
                    const gap = Math.abs(start - at);
                    if (gap < best) {
                        best = gap;
                        index = position;
                    }
                });
                return index;
            };
            const mark = () => {
                if (!dots) return;
                dotsFor();
                const index = nearest();
                const dot = dots.children[index + 1];
                if (!dot) return;
                const left = dot.offsetLeft;
                const right = dots.clientWidth - left - dot.offsetWidth;
                if (index === marked) {
                    if (!pill.getAnimations().length) {
                        pill.style.left = `${left}px`;
                        pill.style.right = `${right}px`;
                    }
                    return;
                }
                const style = getComputedStyle(pill);
                const from = {
                    left: parseFloat(style.left),
                    right: parseFloat(style.right),
                };
                const first = marked < 0;
                const forward = index > marked;
                marked = index;
                pill.getAnimations().forEach((move) => move.cancel());
                pill.style.left = `${left}px`;
                pill.style.right = `${right}px`;
                if (first || prefersStill(carousel)) return;
                const duration = engine.ms('surface', carousel);
                const easing = engine.ease(duration);
                const edge = (name, start, end, leads) => pill.animate(
                    [{ [name]: `${start}px` }, { [name]: `${end}px` }],
                    {
                        duration: leads
                            ? duration
                            : duration * (1 - DOTS_TRAIL_SHARE),
                        delay: leads ? 0 : duration * DOTS_TRAIL_SHARE,
                        easing,
                        fill: 'backwards',
                    },
                );
                edge('right', from.right, right, forward);
                edge('left', from.left, left, !forward);
            };
            const refresh = () => {
                update();
                place();
                mark();
            };
            const soon = rafThrottle(refresh);
            track.addEventListener('scroll', soon, { passive: true });
            const watch = new ResizeObserver(soon);
            watch.observe(carousel);
            if (title) watch.observe(title);
            watch.observe(track);
            Array.from(track.children).forEach((item) => watch.observe(item));
            document.fonts.ready.then(refresh);
            refresh();
            carousel.setAttribute('data-km-ready', '');

            const wait = engine.paced(
                Number(carousel.dataset.kmCarouselInterval),
                carousel,
            );
            if (!wait || prefersStill(carousel)) return;
            const way = carousel.dataset.kmCarouselDirection === 'left'
                ? -1
                : 1;
            const holds = new Set();
            let timer = 0;
            const later = () => {
                window.clearTimeout(timer);
                timer = window.setTimeout(turn, wait * 1000);
            };
            const turn = () => {
                later();
                if (document.hidden || room() <= 1) return;
                const at = track.scrollLeft;
                if (way > 0 && at >= room() - 1) goTo(0);
                else if (way < 0 && at <= 1) goTo(room());
                else step(way);
            };
            const hold = (reason, on) => {
                const was = holds.size;
                if (on) holds.add(reason);
                else holds.delete(reason);
                if (holds.size) window.clearTimeout(timer);
                else if (was) later();
            };
            carousel.addEventListener(
                'pointerenter',
                (event) => event.pointerType === 'mouse' && hold('hover', 1),
            );
            carousel.addEventListener('pointerleave', () => hold('hover', 0));
            carousel.addEventListener('focusin', (event) => hold(
                'focus',
                event.target.matches(':focus-visible'),
            ));
            carousel.addEventListener('focusout', () => hold('focus', 0));
            carousel.addEventListener('touchstart', () => hold('touch', 1), {
                passive: true,
            });
            carousel.addEventListener('touchend', () => hold('touch', 0));
            carousel.addEventListener('touchcancel', () => hold('touch', 0));
            moved = (run) => {
                window.clearTimeout(timer);
                run.then(() => {
                    if (!holds.size) later();
                });
            };
            new IntersectionObserver((entries) => {
                hold('away', !entries.at(-1).isIntersecting);
            }).observe(carousel);
            later();
        });
    }

