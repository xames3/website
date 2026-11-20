    function revealBlocks(node) {
        return Array.from(node?.children ?? []).flatMap((child) => (
            child.tagName === 'SECTION' ? revealBlocks(child) : [child]
        ));
    }

    function arrival() {
        return root.getAttribute('data-km-arrival');
    }

    function kept(node) {
        return arrival() === 'link' && node.matches('.km-header, .km-footer');
    }

    function markTitle() {
        const heading = document.querySelector('#km-content > section > h1');
        if (!heading) return [];
        const items = [
            document.querySelector('.km-header'),
            document.querySelector('.km-breadcrumbs'),
            heading,
            ...Array.from(heading.parentElement.children).filter((child) => (
                child.matches('.km-text--lead, .km-byline')
            )),
        ].filter((item) => item && !kept(item));
        items.forEach((item) => item.classList.add(TITLE_ITEM));
        return items;
    }

    function titleHold() {
        if (!document.querySelector(`.${TITLE_ITEM}`)) return 0;
        const lead = Number.parseFloat(
            getComputedStyle(root).getPropertyValue('--km-title-lead'),
        ) || 0;
        const hold = TIMING.titleStep() * (TITLE_STEPS - lead);
        return Math.max(0, hold - TIMING.titleSkip());
    }

    function afterLoading(callback) {
        if (!root.classList.contains('km-document--loading')) {
            callback();
            return;
        }
        const watcher = new MutationObserver(() => {
            if (root.classList.contains('km-document--loading')) return;
            watcher.disconnect();
            callback();
        });
        watcher.observe(root, { attributes: true, attributeFilter: ['class'] });
    }

    function initPageReveal() {
        if (prefersReducedMotion() || arrival() === 'history') return;
        const title = new Set(markTitle());
        const blocks = [
            document.querySelector('.km-header'),
            document.querySelector('.km-breadcrumbs'),
            ...revealBlocks(document.getElementById('km-content')),
            document.querySelector('.km-feedback-section'),
            document.querySelector('.km-page__updated'),
            document.querySelector('.km-page__more-button'),
            document.querySelector('.km-pagination'),
            document.querySelector('.km-related'),
            document.querySelector('.km-footer'),
        ].filter((block) => block && !title.has(block) && !kept(block));

        const duration = engine.ms('enter');
        let step = engine.ms('stagger');
        let titled = false;
        let hold = 0;
        let waiting = blocks;
        let began = null;
        let busy = 0;
        let ends = 0;
        let screen = 0;
        let done = false;

        const release = (block, animate) => {
            if (animate) block.classList.add(REVEAL_SHOWN);
            else block.classList.remove(REVEAL_WAITING);
            block.dispatchEvent(new Event('km:reveal'));
        };

        const finish = () => {
            if (done) return;
            done = true;
            waiting.forEach((block) => release(block, false));
            waiting = [];
            blocks.forEach((block) => (
                block.classList.remove(REVEAL_WAITING, REVEAL_SHOWN)
            ));
        };

        const play = (block, now) => {
            busy = now + step;
            ends = Math.max(ends, now + duration);
            release(block, true);
        };

        const edges = (fold) => {
            const known = new Map();
            const clip = (node) => {
                if (!node || node === document.body) return [0, fold];
                if (!known.has(node)) {
                    let [top, bottom] = clip(node.parentElement);
                    if (getComputedStyle(node).overflowY !== 'visible') {
                        const box = node.getBoundingClientRect();
                        top = Math.max(top, box.top);
                        bottom = Math.min(bottom, box.bottom);
                    }
                    known.set(node, [top, bottom]);
                }
                return known.get(node);
            };
            return clip;
        };

        const inView = (block, clip) => {
            const box = block.getBoundingClientRect();
            const [top, bottom] = clip(block.parentElement);
            return (box.width > 0 || box.height > 0)
                && box.bottom >= top && box.top < bottom;
        };

        const tick = (now) => {
            if (done) return;
            try {
                if (root.classList.contains('km-document--loading')) {
                    requestAnimationFrame(tick);
                    return;
                }
                if (began === null) {
                    began = now;
                    screen = screenHeight();
                    hold = titleHold();
                    const clip = edges(Math.max(window.innerHeight, screen));
                    const seen = waiting.map((block) => inView(block, clip));
                    waiting.filter((block, index) => !seen[index])
                        .forEach((block) => release(block, false));
                    waiting = waiting.filter((block, index) => seen[index]);
                    step = clamp(
                        (REVEAL_BUDGET_MS / engine.speed() - duration)
                            / Math.max(1, waiting.length - 1),
                        REVEAL_MIN_STEP_MS,
                        step,
                    );
                }
                if (!titled) {
                    if (now - began < hold) {
                        requestAnimationFrame(tick);
                        return;
                    }
                    titled = true;
                }
                const fold = Math.max(window.innerHeight, screen);
                const clip = edges(fold);
                const ready = waiting.filter((block) => inView(block, clip));
                if (ready.length && now >= busy) {
                    const block = ready[0];
                    const waitingIndex = waiting.indexOf(block);
                    waiting.slice(0, waitingIndex)
                        .forEach((passed) => release(passed, false));
                    waiting = waiting.slice(waitingIndex + 1);
                    play(block, now);
                } else if (!ready.length && now >= Math.max(busy, ends)) {
                    finish();
                    return;
                }
                requestAnimationFrame(tick);
            } catch (error) {
                finish();
                console.error(error);
            }
        };
        blocks.forEach((block) => block.classList.add(REVEAL_WAITING));
        requestAnimationFrame(tick);
    }

