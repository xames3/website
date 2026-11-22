    function readPayload(host) {
        return JSON.parse(host.querySelector('[data-km-payload]').textContent);
    }

    function sourceOf(payload) {
        const code = payload.code || '';
        if (!payload.setup) return code;
        const { open = '#', close = '' } = payload.comment || {};
        const head = `${open} ${say('setup')}${close ? ` ${close}` : ''}`;
        return `${head}\n${payload.setup}\n\n${code}`;
    }

    function valueNode(item, opened) {
        const value = document.createElement('span');
        value.className = 'km-code-explain__value';
        if (!item.short) {
            value.textContent = item.full;
            return value;
        }
        const short = document.createElement('span');
        short.className = 'km-code-explain__short';
        short.textContent = item.short;
        const full = document.createElement('span');
        full.className = 'km-code-explain__full';
        full.textContent = item.full;
        value.dataset.kmKey = item.key;
        value.setAttribute('data-km-long', '');
        value.setAttribute('role', 'button');
        value.tabIndex = 0;
        const open = opened.has(item.key);
        if (open) value.setAttribute('data-km-open', '');
        value.setAttribute('aria-expanded', String(open));
        value.append(short, full);
        return value;
    }

    function entryNode(item, opened) {
        const entry = document.createElement('span');
        entry.className = 'km-code-explain__variable';
        if (item.fresh) entry.setAttribute('data-km-fresh', '');
        if (item.kind) entry.dataset.kmKind = item.kind;
        entry.append(
            item.name ? `${item.name}: ` : `${item.mark} `,
            valueNode(item, opened),
        );
        return entry;
    }

    function diffLines(before, after) {
        const table = Array.from(
            { length: before.length + 1 },
            () => new Uint32Array(after.length + 1),
        );
        for (let row = before.length - 1; row >= 0; row -= 1) {
            for (let column = after.length - 1; column >= 0; column -= 1) {
                table[row][column] = before[row] === after[column]
                    ? table[row + 1][column + 1] + 1
                    : Math.max(table[row + 1][column], table[row][column + 1]);
            }
        }
        const script = [];
        let i = 0;
        let j = 0;
        while (i < before.length || j < after.length) {
            if (i < before.length && j < after.length
                && before[i] === after[j]) {
                script.push(['=', i, j]);
                i += 1;
                j += 1;
            } else if (j === after.length
                || (i < before.length && table[i + 1][j] >= table[i][j + 1])) {
                script.push(['-', i, -1]);
                i += 1;
            } else {
                script.push(['+', -1, j]);
                j += 1;
            }
        }
        return script;
    }

    function signLine(line, change) {
        const sign = document.createElement('span');
        sign.className = 'km-code-version__sign';
        sign.setAttribute('aria-hidden', 'true');
        sign.textContent = change === 'added' ? '+' : '-';
        line.dataset.kmDiff = change;
        line.prepend(sign);
    }

    function colorRows(rows, lines) {
        rows.forEach((row) => {
            const runs = lines[Number(row.dataset.kmLine) - 1];
            if (!runs?.length) return;
            row.querySelector('.km-code-explain__source').replaceChildren(
                ...runs.map((run) => {
                    if (typeof run === 'string') return run;
                    const token = document.createElement('span');
                    token.className = run[0];
                    token.textContent = run[1];
                    return token;
                }),
            );
        });
    }

    function showVersion(view, rows) {
        view.marked = [];
        view.filled = [];
        view.current = null;
        view.lines.clear();
        view.code.replaceChildren(...rows.map((row) => {
            const line = row.cloneNode(true);
            view.lines.set(Number(line.dataset.kmLine), line);
            return line;
        }));
    }

