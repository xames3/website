    function say(key) {
        return STRINGS[key];
    }

    function makeIcon(key, ...classes) {
        if (!MARKS[key]) return null;
        const mark = document.createElement('i');
        mark.className = [MARKS[key], ...classes].join(' ');
        mark.setAttribute('aria-hidden', 'true');
        return mark;
    }

    function attempt(fn) {
        try {
            return fn();
        } catch {
            return undefined;
        }
    }

    function decodeId(value) {
        try {
            return decodeURIComponent(value);
        } catch {
            return value;
        }
    }

    function prefersReducedMotion() {
        return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    // A reader who asks for less motion, or a directive that says
    // `:no-motion:` and holds the element.
    function prefersStill(element) {
        return prefersReducedMotion()
            || element?.closest?.('.km-motion--off') != null;
    }

