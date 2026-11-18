    function initNavFit() {
        const tree = document.querySelector('.km-header__nav-tree');
        if (!tree || !document.querySelector('.km-layout--nav-in-header')) {
            return;
        }
        const wraps = () => {
            const tops = new Set(Array.from(tree.querySelectorAll(
                '.km-header__nav-group, .km-header__nav-links > li',
            )).map((item) => Math.round(item.getBoundingClientRect().top)));
            return tops.size > 1;
        };
        const fit = () => {
            root.classList.remove(NAV_WRAPPED);
            if (window.innerWidth >= NAV_WIDE_PX && wraps()) {
                root.classList.add(NAV_WRAPPED);
            }
        };
        let frame = 0;
        const later = () => {
            cancelAnimationFrame(frame);
            frame = requestAnimationFrame(fit);
        };
        fit();
        window.addEventListener('resize', later, { passive: true });
        window.addEventListener('load', later, { once: true });
        document.fonts.ready.then(later);
    }

    function initSidebar() {
        const sidebar = document.getElementById('km-sidebar');
        const toggle = document.querySelector('.km-header__menu-toggle');
        const backdrop = document.querySelector('.km-sidebar__backdrop');
        if (!sidebar || !toggle) return;
        let open = false;
        const stops = () => Array.from(sidebar.querySelectorAll(FOCUSABLE))
            .filter((element) => (
                element.tabIndex >= 0 && element.getClientRects().length
            ));
        const enter = (frames = 0) => {
            if (!open) return;
            if (getComputedStyle(sidebar).visibility !== 'visible'
                && frames < 30) {
                requestAnimationFrame(() => enter(frames + 1));
                return;
            }
            stops()[0]?.focus({ preventScroll: true });
        };
        const show = (next, restore = true, keyed = false) => {
            const inside = sidebar.contains(document.activeElement);
            open = next;
            document.body.classList.toggle('km-body--locked', next);
            sidebar.classList.toggle('km-sidebar--visible', next);
            toggle.setAttribute('aria-expanded', String(next));
            if (backdrop) backdrop.hidden = !next;
            if (next && keyed) requestAnimationFrame(() => enter());
            else if (!next && restore && inside) {
                toggle.focus({ preventScroll: true });
            }
        };
        toggle.addEventListener('click', (event) => (
            show(!open, true, event.detail === 0)
        ));
        backdrop?.addEventListener('click', () => show(false));
        sidebar.addEventListener('click', (event) => {
            const spot = toggle.getBoundingClientRect();
            if (
                open
                && !event.target.closest?.('a, button, input')
                && event.clientX >= spot.left && event.clientX <= spot.right
                && event.clientY >= spot.top && event.clientY <= spot.bottom
            ) {
                show(false);
                return;
            }
            const link = event.target.closest?.('a[href^="#"]');
            if (!open || !link || isModifiedClick(event)) return;
            show(false);
            if (link.getAttribute('href') !== '#') return;
            event.preventDefault();
            glideTo(0);
        });
        window.addEventListener('keydown', (event) => {
            if (!open) return;
            if (event.key === 'Escape') {
                show(false);
                return;
            }
            if (event.key !== 'Tab') return;
            const items = stops();
            if (!items.length) return;
            const focusedIndex = items.indexOf(document.activeElement);
            const next = focusedIndex < 0
                ? 0
                : focusedIndex + (event.shiftKey ? -1 : 1);
            event.preventDefault();
            items[(next + items.length) % items.length].focus();
        });
        window.addEventListener('resize', () => {
            const nested = document.querySelector('.km-layout--nav-in-header');
            const wide = nested ? NAV_WIDE_PX : SIDEBAR_WIDE_PX;
            if (open && window.innerWidth >= wide
                && !(nested && root.classList.contains(NAV_WRAPPED))) {
                show(false, false);
            }
        }, { passive: true });

        // The drawer follows a finger (or a pointer) pulling it shut, 1:1
        // once it's clear that's what's meant and not a scroll, and lets go
        // by where it would come to rest, not where it is: a quick flick
        // shuts it from a short way, a slow drag has to go far.
        let drag = null;
        const finishDrag = (close, from, width) => {
            const target = close ? width : 0;
            const duration = Math.max(
                120,
                engine.ms('surface') * (Math.abs(target - from) / width),
            );
            const easing = engine.ease(duration);
            sidebar.style.visibility = 'visible';
            const frames = (key, a, b) => [
                { [key]: key === 'transform' ? `translateX(${a}px)` : a },
                { [key]: key === 'transform' ? `translateX(${b}px)` : b },
            ];
            const move = sidebar.animate(
                frames('transform', from, target),
                { duration, easing, fill: 'forwards' },
            );
            const fade = backdrop?.animate(
                frames('opacity', 1 - Math.min(1, from / width), close ? 0 : 1),
                { duration, easing, fill: 'forwards' },
            );
            move.finished.then(() => {
                sidebar.style.transition = 'none';
                if (close) show(false);
                sidebar.style.visibility = '';
                sidebar.classList.remove('km-sidebar--dragging');
                if (backdrop) backdrop.style.opacity = '';
                move.cancel();
                fade?.cancel();
                requestAnimationFrame(() => {
                    sidebar.style.transition = '';
                });
            }).catch(() => {});
        };
        sidebar.addEventListener('pointerdown', (event) => {
            const secondary = event.pointerType === 'mouse'
                && event.button !== 0;
            if (!open || secondary) return;
            if (event.target.closest?.('input, textarea')) return;
            drag = {
                id: event.pointerId,
                x: event.clientX,
                y: event.clientY,
                live: false,
                offset: 0,
                samples: [[event.clientX, performance.now()]],
            };
        }, { passive: true });
        sidebar.addEventListener('pointermove', (event) => {
            if (!drag || event.pointerId !== drag.id) return;
            const across = event.clientX - drag.x;
            const down = event.clientY - drag.y;
            if (!drag.live) {
                if (Math.abs(down) > DRAWER_DRAG_START_PX
                    && Math.abs(down) > Math.abs(across)) {
                    drag = null;
                    return;
                }
                if (across < DRAWER_DRAG_START_PX
                    || across < Math.abs(down) * 1.2) return;
                drag.live = true;
                sidebar.setPointerCapture(event.pointerId);
                sidebar.classList.add('km-sidebar--dragging');
            }
            drag.offset = Math.max(0, across - DRAWER_DRAG_START_PX);
            sidebar.style.transform = `translateX(${drag.offset}px)`;
            if (backdrop) {
                backdrop.style.opacity = String(
                    1 - Math.min(1, drag.offset / sidebar.offsetWidth),
                );
            }
            const now = performance.now();
            drag.samples.push([event.clientX, now]);
            while (drag.samples.length > 2
                && now - drag.samples[0][1] > DRAWER_VELOCITY_WINDOW_MS) {
                drag.samples.shift();
            }
        });
        const letGo = (event) => {
            if (!drag || event.pointerId !== drag.id) return;
            const held = drag;
            drag = null;
            if (!held.live) return;
            const [from, began] = held.samples[0];
            const [to, ended] = held.samples[held.samples.length - 1];
            const speed = ended > began ? (to - from) / (ended - began) : 0;
            const width = sidebar.offsetWidth;
            const rest = held.offset + speed * DRAWER_COAST_MS;
            sidebar.style.transform = '';
            finishDrag(
                event.type !== 'pointercancel'
                    && (rest > width * DRAWER_CLOSE_SHARE
                        || speed > DRAWER_FLICK_PX_PER_MS),
                held.offset,
                width,
            );
        };
        sidebar.addEventListener('pointerup', letGo);
        sidebar.addEventListener('pointercancel', letGo);
    }

