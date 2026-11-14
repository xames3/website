    function formatCount(value) {
        if (value < 1000) return String(value);
        const units = [[1e9, 'b'], [1e6, 'm'], [1e3, 'k']];
        let at = units.findIndex(([each]) => value >= each);
        const tenthsOf = (unit) => Math.floor((value * 10 + unit / 2) / unit);
        if (at > 0 && tenthsOf(units[at][0]) >= 10000) at -= 1;
        const [size, suffix] = units[at];
        const tenths = tenthsOf(size);
        return `${Math.floor(tenths / 10)}.${tenths % 10}`
            .replace(/\.0$/, '') + suffix;
    }

    function tickerSymbol(character) {
        const symbol = document.createElement('span');
        symbol.className = 'km-ticker__symbol';
        symbol.textContent = character;
        return symbol;
    }

    function tickerWheel(place, shown, travel) {
        const digit = document.createElement('span');
        digit.className = 'km-ticker__digit';
        digit.classList.toggle('km-ticker__digit--shown', shown);
        const reel = document.createElement('span');
        reel.className = 'km-ticker__reel';
        for (let i = 0; i < TICKER_CELLS; i += 1) {
            const cell = document.createElement('span');
            cell.className = 'km-ticker__cell';
            cell.textContent = String(i % 10);
            reel.appendChild(cell);
        }
        digit.appendChild(reel);
        return { digit, reel, place, shown, travel, position: 0 };
    }

    // `driven` is true when something else (an animation) is already moving
    // the reel and only the digit showing and the blur are left to do.
    function turnTickerWheel(wheel, value, progress, landed, driven = false) {
        if (!wheel.shown && value >= 10 ** wheel.place) {
            wheel.shown = true;
            wheel.digit.classList.add('km-ticker__digit--shown');
        }
        const position = (wheel.travel * progress) % 10;
        const blur = landed
            ? 0
            : Math.min(TICKER_BLUR_PX, (position - wheel.position + 10) % 10);
        if (!driven) {
            const lift = (position / TICKER_CELLS) * 100;
            wheel.reel.style.transform = `translateY(-${lift}%)`;
        }
        wheel.reel.style.filter = blur > 0.05
            ? `blur(${blur.toFixed(2)}px)`
            : '';
        wheel.position = position;
    }

    // A reel turns through its ten digits again and again on the way, so
    // its path is a run of climbs with a jump back after each: the keyframes
    // are at the points it wraps, in how far through the count it is.
    function tickerPath(wheel) {
        const lift = (cell) => `translateY(-${(cell / TICKER_CELLS) * 100}%)`;
        const frames = [{ offset: 0, transform: lift(0) }];
        for (let turn = 1; turn * 10 < wheel.travel; turn += 1) {
            const offset = (turn * 10) / wheel.travel;
            frames.push({ offset, transform: lift(10) });
            frames.push({ offset, transform: lift(0) });
        }
        frames.push({ offset: 1, transform: lift(wheel.travel % 10) });
        return frames;
    }

    function reserveTickerWidths(items) {
        if (!items.length) return;
        const marked = items.map(({ ticker }) => {
            const digits = Array.from(
                ticker.querySelectorAll('.km-ticker__digit'),
            );
            const shown = digits.map((digit) => (
                digit.classList.contains('km-ticker__digit--shown')
            ));
            ticker.classList.add('km-ticker__wheels--measuring');
            digits.forEach((digit) => (
                digit.classList.add('km-ticker__digit--shown')
            ));
            return { digits, shown };
        });
        const widths = items.map(({ ticker }) => (
            ticker.getBoundingClientRect().width
        ));
        marked.forEach(({ digits, shown }) => {
            digits.forEach((digit, index) => digit.classList.toggle(
                'km-ticker__digit--shown',
                shown[index],
            ));
        });
        items[0].ticker.getBoundingClientRect();
        items.forEach(({ ticker }) => (
            ticker.classList.remove('km-ticker__wheels--measuring')
        ));
        const sizes = items.map(({ field }) => (
            parseFloat(getComputedStyle(field).fontSize)
        ));
        items.forEach(({ field }, index) => {
            field.style.minWidth = `${widths[index] / sizes[index]}em`;
        });
    }

    function makeTicker(field, text) {
        const decimal = text.includes('.');
        const target = Number(text.replace(/\D/g, ''));
        const places = Math.max(String(target).length, decimal ? 2 : 1);
        const digits = String(target).padStart(places, '0');
        const reduced = prefersStill(field);
        const ticker = document.createElement('span');
        ticker.className = 'km-ticker__wheels';
        ticker.setAttribute('aria-hidden', 'true');
        const wheels = [];
        for (let place = places - 1; place >= 0; place -= 1) {
            const index = places - 1 - place;
            const travel = Number(digits[index]) + 10 * index;
            const wheel = tickerWheel(
                place,
                reduced || place < (decimal ? 2 : 1),
                travel,
            );
            wheels.push(wheel);
            ticker.appendChild(wheel.digit);
            if (decimal && place === 1) ticker.appendChild(tickerSymbol('.'));
        }
        if (/[kmb]$/.test(text)) {
            ticker.appendChild(tickerSymbol(text.slice(-1)));
        }
        const label = document.createElement('span');
        label.className = 'sr-only';
        label.textContent = text;

        wheels.forEach((wheel) => turnTickerWheel(
            wheel,
            reduced ? target : 0,
            reduced ? 1 : 0,
        ));
        field.replaceChildren(label, ticker);

        const count = (duration) => {
            if (reduced || !target) return;
            const easing = engine.ease(duration);
            const moving = wheels.map((wheel) => wheel.reel.animate(
                tickerPath(wheel),
                { duration, easing, fill: 'both' },
            ));
            const turn = () => {
                const progress = moving[0].effect.getComputedTiming().progress
                    ?? 1;
                const landed = moving[0].playState === 'finished';
                wheels.forEach((wheel) => turnTickerWheel(
                    wheel,
                    target * progress,
                    progress,
                    landed,
                    true,
                ));
                if (!landed) requestAnimationFrame(turn);
            };
            requestAnimationFrame(turn);
            Promise.all(moving.map((each) => each.finished)).then(() => {
                wheels.forEach((wheel) => turnTickerWheel(
                    wheel,
                    target,
                    1,
                    true,
                ));
                moving.forEach((each) => each.cancel());
            }).catch(() => {});
        };
        return { ticker, count };
    }

    function buildTicker(field, text) {
        const { ticker, count } = makeTicker(field, text);
        reserveTickerWidths([{ field, ticker }]);
        return count;
    }

