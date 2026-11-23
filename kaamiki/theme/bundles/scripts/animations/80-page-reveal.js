    function revealBlocks(node) {
        return Array.from(node?.children ?? []).flatMap((child) => (
            child.tagName === 'SECTION' ? revealBlocks(child) : [child]
        ));
    }

    function arrival() {
        return root.getAttribute('data-km-arrival');
    }

    const morphed = root.hasAttribute('data-km-morph');

    function kept(node) {
        if (morphed && node.matches(
            `.km-page > .km-banner, .km-breadcrumbs, ${TITLE_HEADING}`,
        )) return true;
        return arrival() === 'link' && node.matches('.km-header, .km-footer');
    }

    function titleParts() {
        const heading = document.querySelector(TITLE_HEADING);
        if (!heading) return [];
        return [
            document.querySelector('.km-header'),
            document.querySelector('.km-page > .km-banner'),
            document.querySelector('.km-breadcrumbs'),
            heading,
            ...Array.from(heading.parentElement.children).filter((child) => (
                child.matches('.km-text--lead, .km-byline')
            )),
        ].filter((part) => part && !kept(part));
    }

    function titleStep(part) {
        return TITLE_ORDER.findIndex((selector) => part.matches(selector));
    }

    function bodyBlocks(title) {
        return [
            document.querySelector('.km-header'),
            document.querySelector('.km-page > .km-banner'),
            document.querySelector('.km-breadcrumbs'),
            ...revealBlocks(document.getElementById('km-content')),
            document.querySelector('.km-feedback-section'),
            document.querySelector('.km-page__updated'),
            document.querySelector('.km-page__more-button'),
            document.querySelector('.km-pagination'),
            document.querySelector('.km-related'),
            document.querySelector('.km-footer'),
        ].filter((block) => block && !title.includes(block) && !kept(block));
    }

    function rails(block) {
        const release = block.parentElement;
        if (!release?.matches('.km-release')
            || release.firstElementChild !== block) return [];
        return [
            [release, ENTRANCE_FRAMES.rail, '::before'],
            [release, ENTRANCE_FRAMES.block, '::after'],
        ];
    }

    function edges(fold) {
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
    }

    function inView(block, clip) {
        const box = block.getBoundingClientRect();
        const rise = new DOMMatrixReadOnly(getComputedStyle(block).transform).f;
        const [top, bottom] = clip(block.parentElement);
        return (box.width > 0 || box.height > 0)
            && box.bottom - rise >= top && box.top - rise < bottom;
    }

    function held() {
        return root.hasAttribute('data-km-handing');
    }

    function whenReady(fn) {
        const fonts = arrival() ? Promise.resolve() : document.fonts.ready;
        const cap = new Promise((resolve) => window.setTimeout(
            resolve,
            Math.max(0, ENTRANCE_CAP_MS - performance.now()),
        ));
        requestAnimationFrame(() => Promise.race([fonts, cap]).then(() => (
            whenRoot(['data-km-handing'], held, () => (
                requestAnimationFrame(fn)
            ))
        )));
    }

    function stage(all) {
        const easing = getCssVar('--km-ease-smooth');
        const ahead = (document.timeline.currentTime ?? 0) + ENTRANCE_AHEAD_MS;
        const enter = (node, frames, pseudoElement) => {
            const animation = node.animate(frames, {
                duration: prefersStill(node) ? 0 : engine.ms('enter', node),
                easing,
                fill: 'backwards',
                pseudoElement,
            });
            animation.startTime = ahead;
            all.push(animation);
            return animation;
        };
        const title = titleParts();
        const linked = arrival() === 'link';
        const lead = linked && title.length
            ? Math.min(...title.map(titleStep))
            : 0;
        const skip = linked ? TIMING.titleSkip() : 0;
        const step = TIMING.titleStep();
        title.forEach((part) => enter(part, ENTRANCE_FRAMES.title)
            .effect.updateTiming({
                delay: step * (titleStep(part) - lead) - skip,
            }));
        const blocks = new Map(bodyBlocks(title).map((block) => [block, [
            enter(block, ENTRANCE_FRAMES.block),
            ...rails(block).map((rail) => enter(...rail)),
        ]]));
        for (const block of blocks.keys()) {
            entrance.blocks.set(block, new Moment());
        }
        return {
            all,
            blocks,
            fold: Math.max(window.innerHeight, screenHeight()),
            hold: title.length
                ? Math.max(0, step * (TITLE_ORDER.length - lead) - skip)
                : 0,
        };
    }

    function play({ all, blocks, fold, hold }) {
        const clip = edges(fold);
        const shown = Array.from(blocks.keys())
            .filter((block) => inView(block, clip));
        const now = document.timeline.currentTime;
        blocks.forEach((parts, block) => {
            if (shown.includes(block)) return;
            parts.forEach((animation) => animation.cancel());
            entrance.blocks.get(block).pass();
        });
        const step = clamp(
            (REVEAL_BUDGET_MS / engine.speed() - engine.ms('enter'))
                / Math.max(1, shown.length - 1),
            REVEAL_MIN_STEP_MS,
            engine.ms('stagger'),
        );
        shown.forEach((block, index) => {
            const delay = hold + index * step;
            blocks.get(block).forEach((animation) => (
                animation.effect.updateTiming({ delay })
            ));
            window.setTimeout(() => entrance.blocks.get(block).pass(), delay);
        });
        const live = all.filter((animation) => animation.playState !== 'idle');
        live.forEach((animation) => {
            animation.startTime = now;
        });
        return live;
    }

    function settle(animations) {
        entrance.started.pass();
        Promise.allSettled(animations.map((animation) => animation.finished))
            .then(() => entrance.done.pass());
    }

    function abandon(animations, error) {
        animations.forEach((animation) => animation.cancel());
        entrance.blocks.forEach((moment) => moment.pass());
        settle([]);
        console.error(error);
    }

    function enterPage() {
        if (!root.classList.contains(ENTRANCE_GATE[0])) {
            settle([]);
            return;
        }
        const all = [];
        let staged = null;
        try {
            if (!prefersReducedMotion() && arrival() !== 'history') {
                staged = stage(all);
            }
        } catch (error) {
            abandon(all, error);
        } finally {
            root.classList.remove(...ENTRANCE_GATE);
        }
        if (!staged) {
            if (!all.length) settle([]);
            return;
        }
        whenReady(() => {
            try {
                settle(play(staged));
            } catch (error) {
                abandon(all, error);
            }
        });
    }

    function initPageReveal() {
        if (document.readyState !== 'loading') enterPage();
        else {
            document.addEventListener('DOMContentLoaded', enterPage, {
                once: true,
            });
        }
    }
