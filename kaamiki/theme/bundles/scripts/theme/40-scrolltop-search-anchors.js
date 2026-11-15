    function initScrollTop() {
        const button = document.getElementById('km-scrolltop');
        if (!button) return;
        let last = 0;
        const ring = document.createElementNS(
            'http://www.w3.org/2000/svg',
            'svg',
        );
        ring.setAttribute('class', 'km-scrolltop__ring');
        ring.setAttribute('viewBox', '0 0 44 44');
        ring.setAttribute('aria-hidden', 'true');
        ring.innerHTML = '<circle class="km-scrolltop__track" cx="22" cy="22" '
            + 'r="20.5" /><circle class="km-scrolltop__bar" cx="22" cy="22" '
            + 'r="20.5" pathLength="100" />';
        button.append(ring);
        const progress = () => {
            const far = Math.max(1, root.scrollHeight - window.innerHeight);
            const share = clamp(window.scrollY / far, 0, 1);
            button.style.setProperty(
                '--km-scroll-progress',
                (share * 100).toFixed(1),
            );
        };
        button.addEventListener('click', () => glideTo(0));
        progress();
        window.addEventListener('scroll', () => {
            const y = window.scrollY;
            progress();
            if (y !== last) {
                const bottom = y + window.innerHeight
                    >= root.scrollHeight - SCROLLTOP_AFTER_PX;
                button.classList.toggle(
                    'km-scrolltop--hidden',
                    !(y > SCROLLTOP_AFTER_PX && (y < last || bottom)),
                );
            }
            last = Math.max(0, y);
        }, { passive: true });
    }

    function initHeaderSearch() {
        const search = document.querySelector('.km-header__search .km-search');
        if (!search) return;
        const input = search.querySelector('.km-search__input');
        const submit = search.querySelector('.km-search__submit');

        const open = () => {
            search.classList.add('km-search--open');
            if (!input) return;
            input.focus({ preventScroll: true });
        };
        const close = () => {
            if (input && input.value.trim()) return;
            search.classList.remove('km-search--open');
        };

        submit?.addEventListener('click', (event) => {
            if (search.classList.contains('km-search--open')) return;
            event.preventDefault();
            open();
        });

        input?.addEventListener('focus', () => (
            search.classList.add('km-search--open')
        ));
        input?.addEventListener('blur', () => setTimeout(close, 0));
        input?.addEventListener('keydown', (event) => {
            if (event.key !== 'Escape') return;
            close();
            input.blur();
        });

        const apple = /Mac|iPhone|iPad|iPod/.test(
            navigator.userAgentData?.platform || navigator.platform || '',
        );
        window.addEventListener('keydown', (event) => {
            if (!input || String(event.key).toLowerCase() !== 'k') return;
            if (!(apple ? event.metaKey : event.ctrlKey)
                || event.altKey || event.shiftKey) return;
            event.preventDefault();
            input.focus();
        });

        document.addEventListener('click', (event) => {
            if (!search.contains(event.target)) close();
        });
    }

    function scrollToElement(element) {
        return glideTo(anchorTargetY(element));
    }

    function initAnchorScrolling() {
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a[href^="#"]');
            if (!link || isModifiedClick(event)) return;
            const href = link.getAttribute('href') || '';
            if (href === '#') return;
            const id = decodeId(href.slice(1));
            const target = document.getElementById(id);
            if (!target) return;

            event.preventDefault();
            attempt(() => history.pushState(history.state, '', `#${id}`));
            scrollToElement(target).then((arrived) => {
                if (arrived && !target.contains(link)) focusTarget(target);
            });
        });

        if (!revisited()) settleHash();
    }

    function revisited() {
        const [entry] = performance.getEntriesByType('navigation');
        return entry?.type === 'reload' || entry?.type === 'back_forward';
    }

    function focusTarget(element) {
        if (!element.matches(FOCUSABLE)) element.setAttribute('tabindex', '-1');
        element.focus({ preventScroll: true });
    }

    function reachFocus(target) {
        const began = performance.now();
        let last = window.scrollY;
        let quiet = 0;
        const look = (now) => {
            if (document.activeElement !== target) return;
            quiet = window.scrollY === last ? quiet + 1 : 0;
            last = window.scrollY;
            if (quiet < SCROLL_QUIET_FRAMES) {
                if (now - began < SCROLL_PATIENCE_MS) {
                    requestAnimationFrame(look);
                }
                return;
            }
            const top = headerHeight();
            const rect = target.getBoundingClientRect();
            const fits = rect.height <= window.innerHeight - top;
            const seen = fits
                ? rect.top >= top - 1 && rect.bottom <= window.innerHeight + 1
                : rect.top < window.innerHeight && rect.bottom > top;
            if (!seen) glideTo(layoutTop(target) - top);
        };
        requestAnimationFrame(look);
    }

    function initFocusInView() {
        document.addEventListener('focusin', (event) => {
            if (!root.hasAttribute('data-km-keyboard')) return;
            if (event.target.closest?.(
                '.km-header, .km-sidebar, .km-enlarge',
            )) return;
            reachFocus(event.target);
        });
    }

