    function whenRoot(attributes, busy, fn) {
        if (!busy()) {
            fn();
            return;
        }
        const freed = new MutationObserver(() => {
            if (busy()) return;
            freed.disconnect();
            fn();
        });
        freed.observe(root, {
            attributes: true,
            attributeFilter: attributes,
        });
    }

    class Moment {
        constructor() {
            this.passed = false;
            this.reached = new Promise((resolve) => {
                this.pass = () => {
                    this.passed = true;
                    resolve();
                };
            });
        }

        then(fn) {
            return this.reached.then(fn);
        }
    }

    const entrance = {
        started: new Moment(),
        done: new Moment(),
        blocks: new Map(),
    };

    const landed = window.Kaamiki?.landed;

    function afterLanding(fn) {
        if (landed) landed.then(fn);
        else fn();
    }

    function afterReveal(node, fn) {
        let block = node;
        while (block && !entrance.blocks.has(block)) {
            block = block.parentElement;
        }
        (entrance.blocks.get(block) ?? entrance.started).then(() => fn(node));
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

