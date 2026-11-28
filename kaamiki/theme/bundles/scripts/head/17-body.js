(function() {
    const PEAK = 1.15;
    const HANDOVER = 0.7;

    function glided(easing, at) {
        const effect = new KeyframeEffect(null, null, {
            duration: 1,
            fill: 'both',
            easing,
        });
        new Animation(effect).currentTime = at;
        return effect.getComputedTiming().progress;
    }

    function peak(start = 1, grown = 1) {
        return PEAK / (start + (1 - start) * grown);
    }

    function handover(animation, share = HANDOVER) {
        const { endTime } = animation.effect.getComputedTiming();
        const mark = new Animation(
            new KeyframeEffect(null, null, endTime * share),
        );
        mark.currentTime = animation.currentTime ?? 0;
        mark.play();
        return mark.finished;
    }

    window.Kaamiki = {
        ...window.Kaamiki,
        body: { glided, peak, handover },
    };
})();
