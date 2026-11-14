    function markMissingIcons() {
        const icons = Array.from(document.querySelectorAll(ICON_ONLY))
            .filter((icon) => icon.getClientRects().length);
        const bare = icons.length > 0 && icons.every((icon) => (
            ['none', 'normal'].includes(
                getComputedStyle(icon, '::before').content,
            )
        ));
        document.fonts.ready.then(() => {
            const failed = Array.from(document.fonts).some((face) => (
                face.status === 'error' && /Font Awesome/.test(face.family)
            ));
            root.classList.toggle('km-document--no-icons', bare || failed);
        });
    }

    window.addEventListener('load', markMissingIcons, { once: true });

