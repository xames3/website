    function copyByHand(text) {
        const field = document.createElement('textarea');
        const active = document.activeElement;
        field.value = text;
        field.setAttribute('readonly', '');
        field.style.cssText = 'position: fixed; top: 0; left: 0; opacity: 0; '
            + 'pointer-events: none;';
        document.body.append(field);
        field.select();
        let copied;
        try {
            copied = document.execCommand('copy');
        } catch {
            copied = false;
        }
        field.remove();
        active?.focus?.({ preventScroll: true });
        return copied;
    }

    function copyText(text) {
        if (window.isSecureContext && navigator.clipboard?.writeText) {
            return navigator.clipboard.writeText(text)
                .then(() => true, () => copyByHand(text));
        }
        return Promise.resolve(copyByHand(text));
    }

    const liveRegion = document.createElement('div');
    liveRegion.className = 'km-sr-only';
    liveRegion.setAttribute('role', 'status');
    document.body.append(liveRegion);
    let announcing = 0;

    function announce(message) {
        window.clearTimeout(announcing);
        liveRegion.textContent = message;
        announcing = window.setTimeout(() => {
            liveRegion.textContent = '';
        }, TIMING.tooltipHold());
    }

    const copiedTimers = new WeakMap();

    function showCopied(button, copied) {
        announce(say(copied ? 'copied' : 'failed'));
        window.clearTimeout(copiedTimers.get(button));
        button.toggleAttribute('data-km-copied', copied);
        if (!copied) return;
        copiedTimers.set(button, window.setTimeout(
            () => button.removeAttribute('data-km-copied'),
            TIMING.tooltipHold(),
        ));
    }

    function clamp(value, low, high) {
        return Math.max(low, Math.min(high, value));
    }

