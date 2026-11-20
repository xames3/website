    const COLOUR_KEY = 'km-colour-mode';
    const COLOUR_MODES = ['light', 'dark', 'system'];

    function colourMode() {
        const mode = root.getAttribute('data-km-mode');
        return COLOUR_MODES.includes(mode) ? mode : 'dark';
    }

    function isLightMode() {
        const mode = colourMode();
        return mode === 'light' || (
            mode === 'system'
            && window.matchMedia('(prefers-color-scheme: light)').matches
        );
    }

    function initColourModes() {
        const group = document.querySelector('[data-km-colour-modes]');
        if (!group) return;
        const button = group.querySelector('[data-km-colour-cycle]');
        const icons = Array.from(
            group.querySelectorAll('[data-km-colour-mode]'),
        );
        if (!button) return;

        const paint = (mode) => {
            const { head } = document;
            head.querySelectorAll('meta[name="theme-color"]')
                .forEach((node) => node.remove());
            const add = (content, media) => {
                const node = document.createElement('meta');
                node.name = 'theme-color';
                node.content = content;
                if (media) node.media = media;
                head.append(node);
            };
            if (mode === 'system') {
                add('#ffffff', '(prefers-color-scheme: light)');
                add('#000000', '(prefers-color-scheme: dark)');
            } else {
                add(mode === 'light' ? '#ffffff' : '#000000');
            }
            const scheme = head.querySelector('meta[name="color-scheme"]');
            if (scheme) {
                scheme.content = mode === 'system' ? 'light dark' : mode;
            }
        };

        const show = (mode) => {
            icons.forEach((icon) => {
                icon.hidden = icon.dataset.kmColourMode !== mode;
            });
            const shown = icons.find((icon) => !icon.hidden);
            const label = shown?.dataset.kmLabel ?? mode;
            const name = `${button.dataset.kmColourName}: ${label}`;
            button.setAttribute('aria-label', name);
            button.title = name;
            button.dataset.kmColourState = mode;
        };

        const apply = (mode) => {
            const held = !root.classList.contains('km-document--recolouring');
            if (held) root.classList.add('km-document--recolouring');
            root.setAttribute('data-km-mode', mode);
            paint(mode);
            show(mode);
            document.dispatchEvent(new Event('km:colourmode'));
            if (held) {
                requestAnimationFrame(() => requestAnimationFrame(() => (
                    root.classList.remove('km-document--recolouring')
                )));
            }
        };

        // The new colours spread out from the toggle, as far as the corner
        // furthest from it, with a soft edge, in a browser that can hold the
        // old page while it happens (a keyed press spreads from the middle
        // of the toggle).
        const feather = (reach) => Math.round(clamp(
            reach * REVEAL_FEATHER_SHARE,
            REVEAL_FEATHER_MIN_PX,
            REVEAL_FEATHER_MAX_PX,
        ));
        let reveals = 0;
        const reveal = (mode, event) => {
            if (!document.startViewTransition || prefersReducedMotion()) {
                apply(mode);
                return;
            }
            const turn = ++reveals;
            const spot = button.getBoundingClientRect();
            const keyed = event.detail === 0;
            const x = keyed ? spot.left + spot.width / 2 : event.clientX;
            const y = keyed ? spot.top + spot.height / 2 : event.clientY;
            const reach = Math.hypot(
                Math.max(x, window.innerWidth - x),
                Math.max(y, window.innerHeight - y),
            );
            // The hole in the old page is a soft-edged disc; growing it from
            // the toggle until only the faint rim of its soft edge is left
            // over the furthest corner shows the whole new page, and the
            // old page is let go of there. It starts as wide as its soft
            // edge, so the first frame already shows something, and it
            // keeps its last size until the old page is let go of.
            const soft = feather(reach);
            const across = 2 * (reach + soft);
            const total = engine.ms('content') * REVEAL_STRETCH;
            const cut = engine.when(
                total,
                1 - (soft * REVEAL_HIDDEN_SHARE) / (reach + soft / 2),
            );
            const end = soft + (across - soft) * engine.curve(total)(cut);
            root.style.setProperty('--km-reveal-feather', `${soft}px`);
            root.classList.add('km-document--revealing');
            const change = document.startViewTransition(() => apply(mode));
            change.ready.then(() => root.animate(
                {
                    maskSize: [
                        `100% 100%, ${soft}px ${soft}px`,
                        `100% 100%, ${end}px ${end}px`,
                    ],
                    maskPosition: [
                        `0px 0px, ${x - soft / 2}px ${y - soft / 2}px`,
                        `0px 0px, ${x - end / 2}px ${y - end / 2}px`,
                    ],
                },
                {
                    duration: total * cut,
                    easing: engine.ease(total, 1, cut),
                    fill: 'forwards',
                    pseudoElement: '::view-transition-old(root)',
                },
            )).catch(() => {});
            // A second press skips this one, so only the last one to start
            // lets go of the class.
            change.finished.catch(() => {}).finally(() => {
                if (turn === reveals) {
                    root.classList.remove('km-document--revealing');
                    root.style.removeProperty('--km-reveal-feather');
                }
            });
        };

        button.addEventListener('click', (event) => {
            const next = COLOUR_MODES[
                (COLOUR_MODES.indexOf(colourMode()) + 1) % COLOUR_MODES.length
            ];
            reveal(next, event);
            attempt(() => window.localStorage.setItem(COLOUR_KEY, next));
        });

        window.addEventListener('storage', (event) => {
            if (event.key === COLOUR_KEY
                && COLOUR_MODES.includes(event.newValue)) {
                apply(event.newValue);
            }
        });

        window.matchMedia('(prefers-color-scheme: light)')
            .addEventListener('change', () => {
                if (colourMode() !== 'system') return;
                document.dispatchEvent(new Event('km:colourmode'));
            });

        paint(colourMode());
        show(colourMode());
    }

