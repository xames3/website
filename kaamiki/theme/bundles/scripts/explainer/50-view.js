    function createView(frame) {
        const stage = frame.querySelector('[data-km-stage]');
        const lines = new Map();
        frame.querySelectorAll('[data-km-line]').forEach((line) => {
            lines.set(Number(line.dataset.kmLine), line);
        });
        return {
            frame,
            stage,
            lines,
            code: stage.querySelector('pre'),
            out: frame.querySelector('[data-km-output]'),
            marked: [],
            filled: [],
            current: null,
        };
    }

    function markLines(view, step) {
        view.marked.forEach((line) => line.removeAttribute('data-km-current'));
        view.marked = [];
        for (let line = step.line; line <= (step.end ?? step.line); line += 1) {
            const found = view.lines.get(line);
            if (!found) continue;
            found.setAttribute('data-km-current', '');
            view.marked.push(found);
        }
        view.current = view.marked[0] || null;
    }

    function annotateLines(view, step, comment, opened) {
        view.filled.forEach((slot) => slot.replaceChildren());
        view.filled = [];
        const groups = new Map();
        const add = (lineNumber, item) => {
            if (!view.lines.has(lineNumber)) return;
            if (!groups.has(lineNumber)) groups.set(lineNumber, []);
            groups.get(lineNumber).push(item);
        };
        (step.vars || []).forEach(([name, lineNumber, full, short, fresh]) => {
            add(lineNumber, { name, full, short, fresh, key: name });
        });
        if (step.ret) {
            add(step.line, {
                mark: say('returns'), full: step.ret[0], short: step.ret[1],
                key: 'returns:', kind: 'return', fresh: 1,
            });
        }
        if (step.error) {
            add(step.line, {
                mark: say('error'), full: step.error[0], short: step.error[1],
                key: 'error:', kind: 'error', fresh: 1,
            });
        }
        const { open = '#', close = '' } = comment || {};
        groups.forEach((items, lineNumber) => {
            const slot = view.lines.get(lineNumber)
                .querySelector('[data-km-annotation]');
            slot.append(`${open} `);
            items.forEach((item, n) => {
                if (n) slot.append(', ');
                slot.append(entryNode(item, opened));
            });
            if (close) slot.append(` ${close}`);
            view.filled.push(slot);
        });
    }

    function followLine(view, room, shift) {
        const line = view.current;
        if (!line) return shift;
        const rect = line.getBoundingClientRect();
        const top = rect.top - view.code.getBoundingClientRect().top;
        const pad = Math.min(room / 3, rect.height * 2);
        let target = shift;
        if (top < target + pad) target = top - pad;
        else if (top + rect.height > target + room - pad) {
            target = top + rect.height - room + pad;
        }
        return clamp(
            Math.round(target),
            0,
            Math.max(0, view.code.offsetHeight - room),
        );
    }

    function hasMore({ stage }) {
        return stage.scrollWidth - stage.clientWidth - stage.scrollLeft > 2;
    }

    function markEdges(view, above, below, more = hasMore(view)) {
        const { stage } = view;
        stage.toggleAttribute('data-km-more', more);
        stage.toggleAttribute('data-km-above', above > 2);
        stage.toggleAttribute('data-km-below', below > 2);
    }

