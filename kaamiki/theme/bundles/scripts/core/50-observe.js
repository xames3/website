    function afterReveal(node, fn) {
        if (root.classList.contains('km-document--loading')) {
            const shown = new MutationObserver(() => {
                if (root.classList.contains('km-document--loading')) return;
                shown.disconnect();
                afterReveal(node, fn);
            });
            shown.observe(root, {
                attributes: true,
                attributeFilter: ['class'],
            });
            return;
        }
        const block = node.closest(`.${REVEAL_WAITING}:not(.${REVEAL_SHOWN})`);
        if (block) {
            block.addEventListener('km:reveal', () => fn(node), { once: true });
        }
        else fn(node);
    }

    function onVisible(nodes, onEnter, options = { rootMargin: '200px' }) {
        const list = Array.from(nodes);
        if (!list.length) return;
        const observer = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (!entry.isIntersecting) continue;
                observer.unobserve(entry.target);
                afterReveal(entry.target, onEnter);
            }
        }, options);
        list.forEach((node) => observer.observe(node));
    }

    async function fetchJson(url) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
        try {
            const response = await fetch(url, { signal: controller.signal });
            return response.ok ? await response.json() : null;
        } catch {
            return null;
        } finally {
            clearTimeout(timer);
        }
    }

