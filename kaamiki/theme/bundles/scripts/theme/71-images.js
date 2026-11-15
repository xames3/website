    function clipPicture(node) {
        const image = node.matches('img')
            ? node
            : node.querySelector('img');
        const clip = document.createElement('div');
        clip.className = 'km-figure__clip';
        if (image.style.width) {
            clip.style.width = image.style.width;
            clip.style.maxWidth = '100%';
        }
        node.parentElement.insertBefore(clip, node);
        clip.appendChild(node);
    }

    function initFuzzyBlur() {
        document.querySelectorAll(
            '.km-page__content figure.km-figure--fuzzy-blur > img, '
            + '.km-page__content figure.km-figure--fuzzy-blur '
            + '> a.image-reference',
        ).forEach((node) => clipPicture(node));
    }

    function initImageZoom() {
        if (prefersReducedMotion()) return;
        const figures = '.km-page__content figure.km-figure--zoom';
        document.querySelectorAll(
            `${figures} > :is(img, a.image-reference), `
            + `${figures} > .km-figure__clip > :is(img, a.image-reference), `
            + '.km-page__content img.km-figure--zoom:not(figure img)',
        ).forEach((node) => {
            const parent = node.parentElement;
            const scale = document.createElement('div');
            scale.className = 'km-figure__scale';
            parent.insertBefore(scale, node);
            scale.appendChild(node);
            if (!parent.classList.contains('km-figure__clip')) {
                clipPicture(scale);
            }
        });
    }

    function initPixelatedBlur() {
        const draw = (image, canvas) => {
            const width = Math.max(
                1,
                Math.round(image.naturalWidth / PIXELATE_RATIO),
            );
            const height = Math.max(
                1,
                Math.round(image.naturalHeight / PIXELATE_RATIO),
            );
            canvas.width = width;
            canvas.height = height;
            canvas.getContext('2d').drawImage(image, 0, 0, width, height);
            canvas.classList.add('km-figure__pixelated-canvas--drawn');
        };

        document.querySelectorAll(
            '.km-page__content figure.km-figure--pixelated-blur img',
        ).forEach((image) => {
            const frame = document.createElement('div');
            frame.className = 'km-figure__pixelated-frame';
            if (image.style.width) frame.style.width = image.style.width;
            const canvas = document.createElement('canvas');
            canvas.className = 'km-figure__pixelated-canvas';
            canvas.setAttribute('aria-hidden', 'true');
            image.parentElement.insertBefore(frame, image);
            frame.append(image, canvas);

            const paint = () => {
                try {
                    draw(image, canvas);
                } catch (error) {
                    console.error(error);
                }
            };
            if (image.complete && image.naturalWidth) paint();
            else image.addEventListener('load', paint, { once: true });
        });
    }

    function initTouchReveal() {
        if (window.matchMedia('(hover: hover) and (pointer: fine)')
            .matches) return;
        const selector = '.km-page__content figure.km-figure--fuzzy-blur, '
            + '.km-page__content figure.km-figure--pixelated-blur, '
            + '.km-page__content figure.km-figure--greyscale';
        const figures = document.querySelectorAll(selector);
        if (!figures.length) return;

        document.addEventListener('click', (event) => {
            const figure = event.target.closest(selector);
            if (figure && event.target.closest('a')) return;
            const shouldReveal = figure
                && !figure.classList.contains('km-figure--revealed');
            figures.forEach((node) => (
                node.classList.remove('km-figure--revealed')
            ));
            if (shouldReveal) figure.classList.add('km-figure--revealed');
        });
    }

