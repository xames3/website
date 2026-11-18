    function initHeaderNavDropdowns() {
        const nav = document.querySelector('.km-header__nav-tree');
        if (!nav) return;

        let current = null;
        let timer = 0;
        const trail = [];
        const track = (event) => {
            const now = performance.now();
            trail.push({ x: event.clientX, y: event.clientY, time: now });
            while (trail.length > 1
                && now - trail[0].time > DROPDOWN_AIM_WINDOW_MS) trail.shift();
        };
        const aimed = () => {
            const to = trail[trail.length - 1];
            if (!current || !to
                || performance.now() - to.time > DROPDOWN_AIM_WINDOW_MS) {
                return false;
            }
            const box = current.list.getBoundingClientRect();
            if (to.y >= box.top) return false;
            if (trail.length < 2) return to.x >= box.left && to.x <= box.right;
            const from = trail[0];
            if (to.y <= from.y) return false;
            const side = (a, b, c) => (
                (a.x - c.x) * (b.y - c.y) - (b.x - c.x) * (a.y - c.y)
            );
            const left = { x: box.left, y: box.top };
            const right = { x: box.right, y: box.top };
            const signs = [
                side(to, left, from),
                side(to, right, left),
                side(to, from, right),
            ];
            return signs.every((sign) => sign >= 0)
                || signs.every((sign) => sign <= 0);
        };

        let hovered = 0;
        const mouse = (event) => event.pointerType === 'mouse';
        const outside = (event) => {
            if (current && !current.group.contains(event.target)) hide();
        };

        const place = ({ group, list }) => {
            group.style.setProperty('--km-dropdown-shift', '0px');
            const box = list.getBoundingClientRect();
            const room = document.documentElement.clientWidth
                - DROPDOWN_EDGE_PX;
            const left = Math.max(
                DROPDOWN_EDGE_PX - box.left,
                Math.min(0, room - box.right),
            );
            group.style.setProperty('--km-dropdown-shift', `${left}px`);
        };
        const hide = () => {
            clearTimeout(timer);
            if (!current) return;
            current.group.classList.remove('km-header__nav-group--open');
            current.trigger.setAttribute('aria-expanded', 'false');
            current = null;
            document.removeEventListener('mousemove', track);
            document.removeEventListener('pointerdown', outside);
            trail.length = 0;
        };
        const show = (menu, hover = false) => {
            clearTimeout(timer);
            if (current === menu) return;
            hide();
            menu.group.classList.add('km-header__nav-group--open');
            place(menu);
            menu.trigger.setAttribute('aria-expanded', 'true');
            current = menu;
            hovered = hover ? performance.now() : 0;
            document.addEventListener('mousemove', track, { passive: true });
            document.addEventListener('pointerdown', outside, {
                passive: true,
            });
        };
        const toggle = (menu) => {
            if (current !== menu) show(menu);
            else if (performance.now() - hovered > DROPDOWN_PIN_MS) hide();
        };
        const later = (fn, delay) => {
            clearTimeout(timer);
            timer = setTimeout(fn, delay);
        };

        const dropdown = (group, trigger, list) => {
            const menu = { group, trigger, list };
            const isLink = trigger.tagName === 'A';

            group.addEventListener('pointerenter', (event) => {
                if (!mouse(event)) return;
                if (current === menu) {
                    clearTimeout(timer);
                } else if (!current) {
                    later(() => show(menu, true), DROPDOWN_OPEN_DELAY_MS);
                } else {
                    const until = performance.now()
                        + DROPDOWN_SWITCH_DELAY_MS + DROPDOWN_AIM_MS;
                    const attempt = () => {
                        if (aimed() && performance.now() < until) {
                            later(attempt, DROPDOWN_AIM_STEP_MS);
                        } else show(menu, true);
                    };
                    later(attempt, DROPDOWN_SWITCH_DELAY_MS);
                }
            }, { passive: true });
            group.addEventListener('pointerleave', (event) => {
                if (!mouse(event)) return;
                if (group.querySelector(':focus-visible')) return;
                const until = performance.now()
                    + DROPDOWN_CLOSE_DELAY_MS + DROPDOWN_AIM_MS;
                const attempt = () => {
                    if (aimed() && performance.now() < until) {
                        later(attempt, DROPDOWN_AIM_STEP_MS);
                    } else hide();
                };
                later(attempt, DROPDOWN_CLOSE_DELAY_MS);
            }, { passive: true });
            group.addEventListener('focusout', (event) => {
                if (current === menu
                    && !group.contains(event.relatedTarget)) hide();
            });
            if (!isLink) trigger.addEventListener('click', () => toggle(menu));
            trigger.addEventListener('keydown', (event) => {
                if (event.key === 'ArrowDown') {
                    event.preventDefault();
                    show(menu);
                    list.querySelector('a[href]')?.focus();
                }
            });
            group.addEventListener('keydown', (event) => {
                if (event.key !== 'Escape' || current !== menu) return;
                hide();
                trigger.focus();
            });
        };
        window.addEventListener('resize', hide, { passive: true });

        nav.querySelectorAll('.km-header__nav-group').forEach((group) => {
            dropdown(
                group,
                group.querySelector(':scope > .caption, :scope > a'),
                group.querySelector(':scope > ul'),
            );
        });
    }

