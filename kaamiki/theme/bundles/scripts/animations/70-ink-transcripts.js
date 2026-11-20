    function initInkReveal() {
        ['km-sharpie', 'km-pencil'].forEach((block) => {
            onVisible(
                document.querySelectorAll(`.${block}`),
                (element) => element.classList.add(`${block}--visible`),
                { threshold: 0.1 },
            );
        });
    }

    function spokenForm(text) {
        return text.replace(/^\W+|\W+$/g, '').toLowerCase()
            .replace(/[\u2018\u2019]/g, "'");
    }

    function soundAlike(text) {
        const [, lead, core, trail] = text.match(/^(\W*)(.*?)(\W*)$/);
        const guess = SOUND_ALIKES.get(spokenForm(text));
        if (!guess) return null;
        const cased = core[0] === core[0].toUpperCase()
            ? guess[0].toUpperCase() + guess.slice(1)
            : guess;
        return lead + cased + trail;
    }

    function transcribe(quote) {
        const spoken = quote.querySelector('p');
        if (!spoken) return;
        const nodes = [];
        const walker = document.createTreeWalker(spoken, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) nodes.push(walker.currentNode);

        const words = [];
        nodes.forEach((node) => {
            const parts = node.textContent.split(/(\s+)/);
            node.replaceWith(...parts.map((part) => {
                if (!part.trim()) return part;
                const word = document.createElement('span');
                word.className = 'km-transcript__word';
                word.textContent = part;
                words.push(word);
                return word;
            }));
        });

        let elapsed = 0;
        const delays = words.map((word) => {
            const text = word.textContent;
            const start = elapsed;
            elapsed += SPEECH_WORD_MS + SPEECH_CHAR_MS * text.length;
            if (/[,;:]$/.test(text)) elapsed += SPEECH_COMMA_MS;
            else if (/[.!?\u2026\u2014]$/.test(text)) elapsed += SPEECH_STOP_MS;
            return start;
        });
        delays.push(elapsed);

        const guesses = words.map(() => null);
        const taken = [];
        const used = new Set();
        const order = Array.from(
            words.keys(),
            (index) => [Math.random(), index],
        ).sort((a, b) => a[0] - b[0]);
        for (const [, index] of order) {
            const word = words[index];
            const key = spokenForm(word.textContent);
            const guess = soundAlike(word.textContent);
            if (!guess || word.closest('a') || used.has(key)) continue;
            if (taken.some((other) => (
                Math.abs(other - index) < SPEECH_GAP_WORDS
            ))) continue;
            guesses[index] = guess;
            used.add(key);
            taken.push(index);
        }

        const scale = Math.min(1, SPEECH_MAX_MS / elapsed);
        const milliseconds = (value) => `${Math.round(value * scale)}ms`;
        words.forEach((word, index) => {
            if (!guesses[index]) {
                word.style.setProperty(
                    '--km-delay',
                    milliseconds(delays[index]),
                );
                return;
            }
            const fix = milliseconds(
                delays[Math.min(index + SPEECH_FIX_WORDS, words.length)],
            );
            const heard = document.createElement('span');
            const guess = document.createElement('span');
            heard.className = 'km-transcript__heard';
            guess.className = 'km-transcript__guess';
            guess.setAttribute('aria-hidden', 'true');
            guess.textContent = guesses[index];
            guess.style.setProperty('--km-delay', milliseconds(delays[index]));
            guess.style.setProperty('--km-fix', fix);
            word.style.setProperty('--km-delay', fix);
            guess.addEventListener('animationstart', (event) => {
                if (event.animationName !== 'km-guess-out') return;
                const from = heard.getBoundingClientRect().width;
                const to = word.getBoundingClientRect().width;
                const close = heard.animate(
                    [{ width: `${from}px` }, { width: `${to}px` }],
                    {
                        duration: engine.ms('fade'),
                        easing: getCssVar('--km-ease-smooth'),
                        fill: 'forwards',
                    },
                );
                close.onfinish = () => {
                    guess.remove();
                    close.cancel();
                };
            });
            word.replaceWith(heard);
            heard.append(guess, word);
        });
        quote.style.setProperty('--km-transcript-total', milliseconds(elapsed));
        quote.classList.add('km-transcript');
    }

    function initTranscripts() {
        if (prefersReducedMotion()) return;
        const quotes = Array.from(
            document.querySelectorAll('blockquote.epigraph'),
        );
        quotes.forEach(transcribe);
        onVisible(
            quotes.filter((quote) => quote.classList.contains('km-transcript')),
            (quote) => quote.classList.add('km-transcript--visible'),
            { rootMargin: '0px 0px -15% 0px' },
        );
    }

