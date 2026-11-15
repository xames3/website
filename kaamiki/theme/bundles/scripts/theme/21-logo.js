    function initLogoInvert() {
        const SOLID_RATIO = 0.98;
        const verdicts = new Map();

        const tone = (image) => {
            if (!image.naturalWidth) return '';
            const scale = Math.min(
                1,
                64 / Math.max(image.naturalWidth, image.naturalHeight),
            );
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
            canvas.height = Math.max(
                1,
                Math.round(image.naturalHeight * scale),
            );
            const context = canvas
                .getContext('2d', { willReadFrequently: true });
            context.drawImage(image, 0, 0, canvas.width, canvas.height);
            const { data } = context
                .getImageData(0, 0, canvas.width, canvas.height);
            let opaque = 0;
            let black = 0;
            let white = 0;
            for (let i = 0; i < data.length; i += 4) {
                if (data[i + 3] < 32) continue;
                opaque += 1;
                if (Math.max(data[i], data[i + 1], data[i + 2]) < 64) {
                    black += 1;
                } else if (Math.min(data[i], data[i + 1], data[i + 2]) > 191) {
                    white += 1;
                }
            }
            if (!opaque) return '';
            if (black / opaque >= SOLID_RATIO) return 'black';
            return white / opaque >= SOLID_RATIO ? 'white' : '';
        };

        const logos = document.querySelectorAll('.km-logo--single');
        const paint = () => {
            const light = isLightMode();
            logos.forEach((image) => {
                const verdict = verdicts.get(image.currentSrc || image.src);
                image.classList.toggle(
                    'km-logo--invert',
                    verdict === (light ? 'white' : 'black'),
                );
            });
        };

        logos.forEach((image) => {
            const check = () => {
                const key = image.currentSrc || image.src;
                if (!verdicts.has(key)) {
                    try {
                        verdicts.set(key, tone(image));
                    } catch {
                        verdicts.set(key, '');
                    }
                }
                paint();
            };
            if (image.complete) check();
            else image.addEventListener('load', check, { once: true });
        });
        if (!logos.length) return;
        document.addEventListener('km:colourmode', paint);
        window.matchMedia('(prefers-color-scheme: light)')
            .addEventListener('change', paint);
    }

