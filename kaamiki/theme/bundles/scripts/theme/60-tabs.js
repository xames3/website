    function initTabSets() {
        const bars = [];
        const panels = new Map();
        document.querySelectorAll('.km-tabs').forEach((set) => {
            const tabs = Array.from(
                set.querySelectorAll(':scope > input'),
                (input) => {
                    const label = input.nextElementSibling;
                    return [input, label, label?.nextElementSibling];
                },
            );
            const shaped = ([, label, panel]) => (
                label?.matches('label') && panel?.matches('.km-tabs__panel')
            );
            if (!tabs.length || !tabs.every(shaped)) return;
            const bar = document.createElement('div');
            bar.className = ['km-tabs__bar', set.dataset.kmBar]
                .filter(Boolean).join(' ');
            bar.setAttribute('role', 'tablist');
            const frame = document.createElement('div');
            frame.className = 'km-tabs__frame';
            frame.append(bar);
            set.prepend(frame);
            bars.push(bar);
            tabs.forEach(([input, text, panel]) => {
                const label = document.createElement('span');
                label.className = text.className;
                label.id = text.id || `${input.id}-tab`;
                label.append(...text.childNodes);
                label.addEventListener('click', () => {
                    if (input.checked) return;
                    input.checked = true;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                });
                text.remove();
                bar.append(input, label);
                panels.set(input, panel);
                panel.id = panel.id || `${input.id}-panel`;
                label.setAttribute('role', 'tab');
                label.setAttribute('aria-controls', panel.id);
                panel.setAttribute('role', 'tabpanel');
                panel.setAttribute('aria-labelledby', label.id);
                input.setAttribute('tabindex', '-1');
                input.setAttribute('aria-hidden', 'true');
            });
        });
        if (!bars.length) return;

        const kept = (name) => `km:tabs:${name}`;
        const group = (input) => input.closest('.km-tabs')?.dataset.kmGroup;
        const nests = (set) => !!set.querySelector(
            `.km-tabs[data-km-group="${CSS.escape(set.dataset.kmGroup)}"]`,
        );
        const choose = (set, key) => {
            const input = Array.from(set.querySelectorAll('input[data-km-key]'))
                .find((tab) => (
                    tab.dataset.kmKey === key && tab.closest('.km-tabs') === set
                ));
            if (input && !input.checked) input.checked = true;
        };
        const linked = location.hash.length > 1
            ? document.getElementById(decodeId(location.hash.slice(1)))
            : null;
        document.querySelectorAll('.km-tabs[data-km-group]').forEach((set) => {
            if ((linked && set.contains(linked)) || nests(set)) return;
            const key = attempt(() => (
                localStorage.getItem(kept(set.dataset.kmGroup))
            ));
            if (key) choose(set, key);
        });

        const mark = () => panels.forEach((panel, input) => {
            const label = input.nextElementSibling;
            panel.classList.toggle('km-tabs__panel--current', input.checked);
            label.setAttribute('aria-selected', String(input.checked));
            label.tabIndex = input.checked ? 0 : -1;
        });
        const place = (bar, slide) => {
            const label = bar.querySelector(
                ':scope > input:checked + .km-tabs__label',
            );
            if (!label) return;
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            bar.classList.toggle('km-tabs__bar--sliding', slide);
            bar.style.setProperty(
                '--km-tab-x',
                `${box.left - view.left - bar.clientLeft + bar.scrollLeft}px`,
            );
            bar.style.setProperty(
                '--km-tab-y',
                `${box.top - view.top - bar.clientTop + bar.scrollTop}px`,
            );
            bar.style.setProperty('--km-tab-width', `${box.width}px`);
            bar.style.setProperty('--km-tab-height', `${box.height}px`);
        };
        const settle = () => {
            mark();
            bars.forEach((bar) => place(bar, false));
        };
        const reveal = (label) => {
            const bar = label.parentElement;
            const inset = parseFloat(getComputedStyle(bar).paddingLeft);
            const view = bar.getBoundingClientRect();
            const box = label.getBoundingClientRect();
            const start = box.left - view.left - bar.clientLeft - inset;
            const end = box.right - view.left - bar.clientLeft
                - bar.clientWidth + inset;
            const shift = start < 0 ? start : Math.min(Math.max(end, 0), start);
            if (shift) {
                bar.scrollBy({
                    left: shift,
                    behavior: prefersStill(label) ? 'auto' : 'smooth',
                });
            }
        };

        settle();
        document.addEventListener('DOMContentLoaded', settle, { once: true });
        const watch = new ResizeObserver((entries) => {
            new Set(entries.map(({ target }) => target.parentElement))
                .forEach((bar) => place(bar, false));
        });
        bars.forEach((bar) => (
            bar.querySelectorAll(':scope > .km-tabs__label')
                .forEach((label) => watch.observe(label))
        ));
        document.addEventListener('keydown', (event) => {
            const label = event.target.closest?.(
                '.km-tabs__bar > [role="tab"]',
            );
            if (!label) return;
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                label.click();
                return;
            }
            const moves = {
                ArrowLeft: -1, ArrowRight: 1, Home: 0, End: 0,
            };
            if (!(event.key in moves)) return;
            const bar = label.parentElement;
            const tabs = Array.from(
                bar.querySelectorAll(':scope > [role="tab"]'),
            );
            const here = tabs.indexOf(label);
            const to = event.key === 'Home' ? 0
                : event.key === 'End' ? tabs.length - 1
                    : (here + moves[event.key] + tabs.length) % tabs.length;
            const input = bar.querySelectorAll(':scope > input')[to];
            event.preventDefault();
            input.checked = true;
            input.dispatchEvent(new Event('change', { bubbles: true }));
            tabs[to].focus();
        });
        document.addEventListener('change', (event) => {
            if (!panels.has(event.target)) return;
            const named = group(event.target);
            if (named) {
                attempt(() => localStorage.setItem(
                    kept(named),
                    event.target.dataset.kmKey,
                ));
                document.querySelectorAll(
                    `.km-tabs[data-km-group="${CSS.escape(named)}"]`,
                ).forEach((set) => {
                    if (!set.contains(event.target) && !nests(set)) {
                        choose(set, event.target.dataset.kmKey);
                    }
                });
            }
            mark();
            bars.forEach((bar) => place(bar, true));
            reveal(event.target.nextElementSibling);
        });
    }

