    function focusLine() {
        const top = headerHeight();
        return top + (window.innerHeight - top) / 2;
    }

    function jumpTo(top) {
        stopGlide();
        window.scrollTo({ top, behavior: 'instant' });
    }

    function scrollsInside(element, deltaY) {
        for (
            let node = element;
            node instanceof Element && node !== document.body;
            node = node.parentElement
        ) {
            if (!/auto|scroll/.test(getComputedStyle(node).overflowY)) continue;
            const spare = deltaY > 0
                ? node.scrollHeight - node.clientHeight - node.scrollTop
                : node.scrollTop;
            if (spare > 1) return true;
        }
        return false;
    }

