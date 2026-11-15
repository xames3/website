    function markLoadedIcons() {
        const mark = () => {
            const loaded = Array.from(document.fonts).some((face) => (
                face.status === 'loaded' && /Font ?Awesome/.test(face.family)
            ));
            if (loaded) root.classList.add('km-document--icons-loaded');
        };
        const later = () => document.fonts.ready.then(mark);
        later();
        document.fonts.addEventListener('loading', later);
    }

    markLoadedIcons();
