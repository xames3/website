    // A picture shown smaller than it is, that would come out bigger on this
    // screen, opens in a dialog. It flies there from where it sits and flies
    // back to wherever it is by then. Only transform, border-radius and
    // opacity move, and the picture on the page is never taken out of the
    // flow, only hidden, so nothing around it shifts.
    function enlargeFit(natural, room, below) {
        const share = Math.min(
            1,
            room.width / natural.width,
            Math.max(1, room.height - below) / natural.height,
        );
        const width = natural.width * share;
        const height = natural.height * share;
        return {
            left: room.left + (room.width - width) / 2,
            top: room.top + (room.height - height - below) / 2,
            width,
            height,
        };
    }

    // The transform that puts a box, laid out as `box`, where `rect` is.
    function enlargeShift(rect, box) {
        return `translate(${rect.left - box.left}px, ${rect.top - box.top}px) `
            + `scale(${rect.width / box.width}, ${rect.height / box.height})`;
    }

    function initImageEnlarge() {
        if (!root.hasAttribute('data-km-media-enlarge')) return;
        const SKIP = 'button, summary, .km-no-enlarge, .km-code-explain';
        const MARK = 'km-image--enlargeable';
        const HELD = 'km-image--held';
        const RESTED = 'km-image--rested';
        const route = (url) => new URL(url, window.location.href).pathname;
        const entries = [];
        document.querySelectorAll('.km-page__content img.km-image')
            .forEach((image) => {
                if (image.closest(SKIP)) return;
                const anchor = image.closest('a');
                if (anchor && route(anchor.href)
                    !== route(image.currentSrc || image.src)) return;
                entries.push({ image, trigger: anchor ?? image });
            });
        if (!entries.length) return;
        const triggers = new Map(
            entries.map((entry) => [entry.trigger, entry.image]),
        );
        const touch = window.matchMedia('(pointer: coarse)');
        let dialog = null;
        let view = null;
        let pending = 0;

        const captionOf = (image) => (
            image.closest('figure')?.querySelector('figcaption')
                ?.textContent.trim().replace(/\s+/g, ' ') ?? ''
        );
        const worth = (image) => {
            if (image.checkVisibility
                && !image.checkVisibility({
                    visibilityProperty: true,
                    contentVisibilityAuto: true,
                })) {
                return false;
            }
            const shown = image.clientWidth;
            const natural = {
                width: image.naturalWidth,
                height: image.naturalHeight,
            };
            if (!image.complete || !natural.width || !natural.height
                || shown < 1 || shown >= natural.width * ENLARGE_SHRUNK) {
                return false;
            }
            const space = parseFloat(getComputedStyle(root).fontSize);
            const room = {
                left: space,
                top: space,
                width: root.clientWidth - space * 2,
                height: window.innerHeight - space * 2,
            };
            const box = enlargeFit(natural, room, 0);
            return box.width >= shown * ENLARGE_GAIN
                || image.clientHeight > room.height;
        };
        const mark = ({ image, trigger }, on) => {
            if (trigger.classList.contains(MARK) === on) return;
            trigger.classList.toggle(MARK, on);
            const alone = trigger === image;
            if (!on) {
                ['aria-haspopup', 'aria-label', ...alone
                    ? ['tabindex', 'role']
                    : []].forEach((name) => trigger.removeAttribute(name));
                return;
            }
            const words = image.alt || captionOf(image);
            trigger.setAttribute('aria-haspopup', 'dialog');
            if (alone) {
                trigger.tabIndex = 0;
                trigger.setAttribute('role', 'button');
                trigger.setAttribute(
                    'aria-label',
                    words ? `${words}. ${say('enlarge')}` : say('enlarge'),
                );
            }
        };
        const rest = (trigger) => {
            const timer = setTimeout(
                () => trigger.classList.add(RESTED),
                ENLARGE_RING_HOLD_MS,
            );
            trigger.addEventListener('blur', () => {
                clearTimeout(timer);
                trigger.classList.remove(RESTED);
            }, { once: true });
        };
        const refresh = rafThrottle(() => {
            if (view) return;
            const flags = entries.map((entry) => worth(entry.image));
            entries.forEach((entry, index) => mark(entry, flags[index]));
        });
        const watcher = new ResizeObserver(refresh);
        entries.forEach(({ image }) => {
            watcher.observe(image);
            if (!image.complete) image.addEventListener('load', refresh);
        });
        window.addEventListener('resize', refresh, { passive: true });
        document.addEventListener('toggle', refresh, true);
        refresh();

        const build = () => {
            const make = (tag, name, parent) => {
                const node = document.createElement(tag);
                node.className = `km-enlarge__${name}`;
                parent.append(node);
                return node;
            };
            const shell = document.createElement('div');
            shell.className = 'km-enlarge';
            shell.hidden = true;
            shell.tabIndex = -1;
            shell.setAttribute('role', 'dialog');
            shell.setAttribute('aria-modal', 'true');
            const backdrop = make('div', 'backdrop', shell);
            const picture = make('div', 'picture', shell);
            const image = make('img', 'image', picture);
            image.draggable = false;
            const caption = make('p', 'caption', shell);
            caption.id = 'km-enlarge-caption';
            const close = make('button', 'close', shell);
            close.type = 'button';
            close.setAttribute('aria-label', say('close'));
            close.append(makeIcon('close') ?? 'x');
            document.body.append(shell);
            return { shell, backdrop, picture, image, caption, close };
        };

        // The room the dialog leaves, as the padding it was given, and the
        // box a picture of this size takes in it with its caption under.
        const fit = () => {
            const { shell, picture, caption } = dialog;
            const style = getComputedStyle(shell);
            const room = {
                left: parseFloat(style.paddingLeft),
                top: parseFloat(style.paddingTop),
                width: shell.clientWidth - parseFloat(style.paddingLeft)
                    - parseFloat(style.paddingRight),
                height: shell.clientHeight - parseFloat(style.paddingTop)
                    - parseFloat(style.paddingBottom),
            };
            let box = enlargeFit(view.natural, room, 0);
            if (!caption.hidden) {
                let wide = 0;
                for (let pass = 0; pass < ENLARGE_CAPTION_PASSES; pass += 1) {
                    const next = Math.min(
                        room.width,
                        Math.max(box.width, ENLARGE_CAPTION_MIN_PX),
                    );
                    if (next === wide) break;
                    wide = next;
                    caption.style.width = `${wide}px`;
                    box = enlargeFit(
                        view.natural,
                        room,
                        caption.offsetHeight + ENLARGE_GAP_PX,
                    );
                }
                const under = box.top + box.height + ENLARGE_GAP_PX;
                caption.style.left = `${box.left + (box.width - wide) / 2}px`;
                caption.style.top = `${under}px`;
            }
            Object.assign(picture.style, {
                left: `${box.left}px`,
                top: `${box.top}px`,
                width: `${box.width}px`,
                height: `${box.height}px`,
            });
            return box;
        };

        // The picture drawn at `rect` as the frames that put it there. Its
        // corner is `layout` px in its own size, or the page picture's.
        const framed = (rect, layout, tone = ENLARGE_GREY) => ({
            transform: enlargeShift(rect, view.box),
            borderRadius: `${
                layout ?? view.radius / (rect.width / view.box.width)
            }px`,
            ...view.grey && { filter: tone },
        });
        const live = () => framed(
            dialog.picture.getBoundingClientRect(),
            parseFloat(getComputedStyle(dialog.picture).borderTopLeftRadius),
            getComputedStyle(dialog.picture).filter,
        );
        const at = () => ({
            transform: 'none',
            borderRadius: `${view.corner}px`,
            ...view.grey && { filter: 'none' },
        });
        const between = (from, to) => Object.fromEntries(
            Object.keys(from).map((name) => [name, [from[name], to[name]]]),
        );
        const flight = () => (
            engine.ms('surface', view.source) * ENLARGE_SETTLE_RATIO
        );
        const fly = (frames, done, speed = 0) => {
            const settle = flight();
            const motion = engine.animate(dialog.picture, frames, {
                duration: settle,
                commit: done === settled,
                onDone: done,
            });
            if (speed) {
                motion.animation.effect.updateTiming({
                    easing: engine.easing(engine.spring(settle), 0, speed),
                });
            }
            view.move = motion;
            return motion;
        };

        const visibleRect = (source) => (
            source.closest('.km-figure__scale')?.parentElement ?? source
        ).getBoundingClientRect();

        // Where the page's picture is now, if it's in sight to fly back to.
        const target = () => {
            const { source } = view;
            if (!source.isConnected || !source.getClientRects().length) {
                return null;
            }
            const rect = visibleRect(source);
            const across = Math.min(rect.right, window.innerWidth)
                - Math.max(rect.left, 0);
            const down = Math.min(rect.bottom, window.innerHeight)
                - Math.max(rect.top, 0);
            const seen = Math.max(0, across) * Math.max(0, down);
            return seen >= rect.width * rect.height * ENLARGE_SEEN_SHARE
                ? rect
                : null;
        };

        const pace = (ms, easing) => {
            Object.assign(dialog.backdrop.style, {
                transitionDuration: `${ms}ms`,
                transitionTimingFunction: easing,
            });
        };

        // Fade where the page's picture can't be flown to, or not at all.
        const dim = (done) => {
            view.fading = true;
            dialog.shell.classList.add('km-enlarge--still');
            view.move?.cancel();
            pace(view.fade, 'var(--km-ease-standard)');
            clearTimeout(view.timer);
            view.timer = setTimeout(done, view.fade + ENLARGE_FADE_SLACK_MS);
        };

        const calm = (still) => {
            dialog.shell.classList.toggle('km-enlarge--settled', still);
        };

        function settled() {
            if (!view || view.state === 'closing') return;
            view.state = 'open';
            dialog.backdrop.style.removeProperty('backdrop-filter');
            dialog.picture.style.removeProperty('filter');
            calm(true);
        }

        function finish() {
            if (!view) return;
            const { source, trigger, inert, pushed } = view;
            clearTimeout(view.timer);
            view.move?.cancel();
            const { shell, picture, image, caption, backdrop } = dialog;
            shell.hidden = true;
            shell.className = 'km-enlarge';
            [picture, caption, backdrop].forEach((node) => {
                node.removeAttribute('style');
            });
            picture.querySelector('.km-enlarge__placeholder')?.remove();
            image.removeAttribute('src');
            source.classList.remove(HELD);
            root.classList.remove('km-document--enlarged');
            root.style.removeProperty('--km-scrollbar');
            inert.forEach((node) => {
                node.inert = false;
            });
            window.removeEventListener('keydown', keys, true);
            window.removeEventListener('resize', refit);
            view = null;
            if (pushed) {
                pending += 1;
                history.back();
            }
            if (trigger.isConnected) {
                trigger.focus({ preventScroll: true });
                if (root.hasAttribute('data-km-keyboard')) rest(trigger);
                else trigger.blur();
            }
            refresh();
        }

        // Going away: back to the page's picture if it's in sight, a fade
        // if it isn't (a rotation can leave it anywhere), from where the
        // picture is now and as fast as it was thrown.
        function leave(from, speed = 0) {
            if (!view || view.state === 'closing') return;
            const rect = target();
            const turning = view.state === 'opening'
                && view.move === view.first;
            view.state = 'closing';
            calm(false);
            dialog.shell.classList.remove('km-enlarge--shown');
            if (view.still || !rect) {
                dim(finish);
                return;
            }
            const aim = framed(rect);
            if (from) {
                fly(between(from, aim), finish, speed);
            }
            else if (turning && view.start.transform === aim.transform) {
                view.move = view.move.reverse({
                    onDone: finish,
                    commit: false,
                });
            }
            else {
                view.move = view.move.retarget(aim, {
                    onDone: finish,
                    commit: false,
                });
            }
        }

        function again(from, speed = 0) {
            if (!view || view.state !== 'closing') return;
            view.state = 'opening';
            calm(false);
            dialog.shell.classList.add('km-enlarge--shown');
            if (view.fading) {
                clearTimeout(view.timer);
                view.timer = setTimeout(
                    settled,
                    view.fade + ENLARGE_FADE_SLACK_MS,
                );
            }
            else if (from) fly(between(from, at()), settled, speed);
            else {
                view.move = view.move.retarget(at(), {
                    onDone: settled,
                    commit: true,
                });
            }
        }

        function keys(event) {
            if (!view) return;
            if (event.key === 'Escape') {
                event.preventDefault();
                event.stopImmediatePropagation();
                leave();
            }
            else if (event.key === 'Tab') {
                event.preventDefault();
                dialog.close.focus({ preventScroll: true });
            }
        }

        // A resize or a turn of the screen: lay the picture out again and
        // carry it from where it is to where it goes, so it doesn't jump.
        const refit = rafThrottle(() => {
            if (!view || view.drag?.live) return;
            const here = dialog.picture.getBoundingClientRect();
            const corner = parseFloat(
                getComputedStyle(dialog.picture).borderTopLeftRadius,
            );
            const tone = getComputedStyle(dialog.picture).filter;
            view.box = fit();
            if (view.fading) return;
            calm(false);
            const closing = view.state === 'closing';
            const aim = closing ? target() : null;
            if (closing && !aim) {
                dim(finish);
                return;
            }
            view.move?.cancel();
            fly(
                between(
                    framed(here, corner, tone),
                    aim ? framed(aim) : at(),
                ),
                closing ? finish : settled,
            );
        });

        const open = (source, trigger) => {
            if (view) return;
            dialog ||= build();
            const { shell, picture, image, caption, close } = dialog;
            const still = prefersStill(source);
            const fade = still
                ? ENLARGE_STILL_FADE_MS / engine.speed()
                    / engine.speedOf(source)
                : engine.ms('fade', source);
            const rect = visibleRect(source);
            const figure = source.closest('.km-figure--greyscale');
            const tone = figure
                ? getComputedStyle(figure).filter
                : ENLARGE_GREY;
            const words = captionOf(source);
            view = {
                source,
                trigger,
                still,
                fade,
                state: 'opening',
                natural: {
                    width: source.naturalWidth,
                    height: source.naturalHeight,
                },
                radius: parseFloat(
                    getComputedStyle(source).borderTopLeftRadius,
                ) || 0,
                grey: !!figure,
                pushed: false,
                moved: false,
                fading: still,
                inert: [],
                drag: null,
                move: null,
                first: null,
                timer: 0,
            };
            shell.style.setProperty('--km-enlarge-fade', `${fade}ms`);
            shell.hidden = false;
            shell.classList.toggle('km-enlarge--still', still);
            image.className = 'km-enlarge__image km-enlarge__image--loading';
            image.alt = source.alt;
            image.src = source.currentSrc || source.src;
            caption.textContent = words;
            caption.hidden = !words;
            if (words) {
                shell.setAttribute('aria-labelledby', caption.id);
                shell.removeAttribute('aria-label');
            }
            else {
                shell.removeAttribute('aria-labelledby');
                shell.setAttribute('aria-label', source.alt || say('image'));
            }
            view.box = fit();
            view.corner = parseFloat(
                getComputedStyle(picture).borderTopLeftRadius,
            ) || 0;
            view.start = framed(rect, undefined, tone);
            if (!still) {
                const settle = flight();
                pace(settle, engine.ease(settle));
            }

            root.style.setProperty(
                '--km-scrollbar',
                `${window.innerWidth - root.clientWidth}px`,
            );
            root.classList.add('km-document--enlarged');
            requestAnimationFrame(() => requestAnimationFrame(() => {
                if (view?.source !== source) return;
                Array.from(document.body.children).forEach((node) => {
                    if (node === shell || node.inert) return;
                    node.inert = true;
                    view.inert.push(node);
                });
            }));
            source.classList.add(HELD);
            source.closest('figure')?.classList.remove('km-figure--revealed');
            window.addEventListener('keydown', keys, true);
            window.addEventListener('resize', refit, { passive: true });
            if (touch.matches) {
                history.pushState({ kmEnlarge: true }, '');
                view.pushed = true;
            }

            let decoded = false;
            const ready = image.decode
                ? image.decode().then(() => true, () => false)
                : Promise.resolve(true);
            ready.then(() => {
                decoded = true;
                if (view?.source !== source) return;
                image.classList.remove('km-enlarge__image--loading');
                const holder = picture.querySelector(
                    '.km-enlarge__placeholder',
                );
                if (holder) setTimeout(() => holder.remove(), view.fade);
            });
            requestAnimationFrame(() => {
                if (decoded || view?.source !== source) return;
                const holder = document.createElement('canvas');
                holder.className = 'km-enlarge__placeholder';
                holder.width = ENLARGE_PLACEHOLDER_PX;
                holder.height = Math.max(1, Math.round(
                    ENLARGE_PLACEHOLDER_PX * view.natural.height
                        / view.natural.width,
                ));
                attempt(() => holder.getContext('2d')
                    .drawImage(source, 0, 0, holder.width, holder.height));
                picture.prepend(holder);
            });

            shell.classList.add('km-enlarge--shown');
            if (still) {
                view.timer = setTimeout(
                    settled,
                    fade + ENLARGE_FADE_SLACK_MS,
                );
            }
            else view.first = fly(between(view.start, at()), settled);
            close.focus({ preventScroll: true });
        };

        const press = (event) => {
            if (!view || view.state !== 'open') return;
            if (event.pointerType === 'mouse' && event.button !== 0) return;
            if (event.target.closest('.km-enlarge__close')) return;
            view.moved = false;
            view.drag = {
                id: event.pointerId,
                x: event.clientX,
                y: event.clientY,
                live: false,
                offset: 0,
                samples: [[event.clientX, event.clientY, performance.now()]],
            };
        };

        const pull = (event) => {
            const held = view?.drag;
            if (!held || event.pointerId !== held.id) return;
            const across = event.clientX - held.x;
            const down = event.clientY - held.y;
            const { shell, picture, caption, backdrop } = dialog;
            if (!held.live) {
                if (Math.abs(across) > ENLARGE_DRAG_START_PX
                    && Math.abs(across) > Math.abs(down)) {
                    view.drag = null;
                    return;
                }
                if (down < ENLARGE_DRAG_START_PX
                    || down < Math.abs(across) * 1.2) return;
                held.live = true;
                view.moved = true;
                attempt(() => shell.setPointerCapture(event.pointerId));
                shell.classList.add('km-enlarge--dragging');
                backdrop.style.setProperty('backdrop-filter', 'none');
            }
            held.offset = Math.max(0, down - ENLARGE_DRAG_START_PX);
            const share = clamp(
                held.offset / (window.innerHeight * ENLARGE_DRAG_FADE_SHARE),
                0,
                1,
            );
            const grown = 1 - share * ENLARGE_DRAG_SHRINK;
            const { width, height } = view.box;
            picture.style.transform = 'translate('
                + `${across + (width * (1 - grown)) / 2}px, `
                + `${held.offset + (height * (1 - grown)) / 2}px) `
                + `scale(${grown})`;
            caption.style.transform = `translate(${across}px, `
                + `${held.offset}px)`;
            backdrop.style.opacity = String(1 - share);
            const now = performance.now();
            held.samples.push([event.clientX, event.clientY, now]);
            while (held.samples.length > 2
                && now - held.samples[0][2] > ENLARGE_VELOCITY_WINDOW_MS) {
                held.samples.shift();
            }
        };

        // Let go: the picture goes on from the speed it was let go at and,
        // like the phone's drawer, by where that would take it, not where
        // it is. A flick shuts it from a short way, a slow drag has to go far.
        const release = (event) => {
            const held = view?.drag;
            if (!held || event.pointerId !== held.id) return;
            view.drag = null;
            if (!held.live) return;
            const { shell, picture, caption, backdrop } = dialog;
            // A pointer that has stopped and been held there is going
            // nowhere, however fast it was going before.
            const now = performance.now();
            const recent = held.samples.filter((sample) => (
                now - sample[2] <= ENLARGE_VELOCITY_WINDOW_MS
            ));
            const first = recent[0];
            const last = recent[recent.length - 1];
            const span = recent.length > 1
                ? Math.max(1, last[2] - first[2])
                : 1;
            const velocity = recent.length > 1
                ? {
                    x: (last[0] - first[0]) / span,
                    y: (last[1] - first[1]) / span,
                }
                : { x: 0, y: 0 };
            const rest = held.offset + velocity.y * ENLARGE_COAST_MS;
            const far = Math.max(view.box.height, ENLARGE_DRAG_FLOOR_PX)
                * ENLARGE_CLOSE_SHARE;
            const shut = event.type !== 'pointercancel'
                && (rest > far || velocity.y > ENLARGE_FLICK_PX_PER_MS);
            const here = live();
            const aim = shut ? target() : null;
            const goal = aim ?? view.box;
            const rect = picture.getBoundingClientRect();
            const dx = goal.left + goal.width / 2
                - (rect.left + rect.width / 2);
            const dy = goal.top + goal.height / 2
                - (rect.top + rect.height / 2);
            const way = Math.hypot(dx, dy);
            const speed = way < 1
                ? 0
                : (velocity.x * dx + velocity.y * dy) / (way * way);
            shell.classList.remove('km-enlarge--dragging');
            picture.style.removeProperty('transform');
            caption.style.removeProperty('transform');
            backdrop.style.removeProperty('opacity');
            if (shut) leave(here, speed);
            else fly(between(here, at()), settled, speed);
        };

        document.addEventListener('click', (event) => {
            if (view || event.defaultPrevented || event.button !== 0
                || isModifiedClick(event)) return;
            const trigger = event.target.closest?.(`.${MARK}`);
            if (!trigger || !triggers.has(trigger)) return;
            event.preventDefault();
            open(triggers.get(trigger), trigger);
        });
        document.addEventListener('keydown', (event) => {
            if (view || event.repeat || event.defaultPrevented) return;
            if (event.key !== 'Enter' && event.key !== ' ') return;
            const { target } = event;
            if (target.tagName !== 'IMG' || !target.classList.contains(MARK)) {
                return;
            }
            event.preventDefault();
            open(target, target);
        });
        window.addEventListener('popstate', () => {
            if (pending) {
                pending -= 1;
                return;
            }
            if (!view?.pushed) return;
            view.pushed = false;
            leave();
        });

        // Made while the page is quiet, so the first picture opened doesn't
        // pay for it, and what it listens to is listened to on the page, once.
        engine.calm(() => {
            dialog ||= build();
        });
        document.addEventListener('pointerdown', (event) => {
            if (dialog?.shell.contains(event.target)) press(event);
        });
        document.addEventListener('pointermove', pull);
        document.addEventListener('pointerup', release);
        document.addEventListener('pointercancel', release);
        document.addEventListener('click', (event) => {
            if (!view || !dialog?.shell.contains(event.target)) return;
            if (view.moved) {
                view.moved = false;
                return;
            }
            if (view.state === 'opening') leave();
            else if (view.state === 'closing') again();
            else if (event.target.closest('.km-enlarge__close')
                || !event.target.closest(
                    '.km-enlarge__picture, .km-enlarge__caption',
                )) {
                leave();
            }
        });
    }
