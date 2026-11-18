    // A spring is a damped oscillator that settles on a target. It's written
    // as the exact answer to the motion, not stepped frame by frame, so one
    // curve is the same on every screen, can be handed to the browser as a
    // `linear()` easing, and can start from a speed it's given, which is what
    // lets a motion be reversed mid-flight without a jolt.
    // A spring is "settled" when it is within this much of its target; the
    // last bit is closed at the end so a motion lands exactly. It's left
    // this far, and not nearer, so the motion ends still moving by a pixel
    // or two a frame. A spring that goes on to 0.5% crawls through its last
    // pixels at a fraction of one a frame, and a screen that places text on
    // whole pixels shows that as a shimmer.
    const SPRING_SETTLED = 0.01;
    const SPRING_POINTS = 48;
    const SPRING_FLAT_ZETA = 0.9999;

    // The `omega` times the settle time at which a critically damped spring,
    // `1 - (1 + x) e^-x`, gets that near, found once by halving.
    function flatDecay(target) {
        let low = 0;
        let high = 30;
        for (let i = 0; i < 40; i += 1) {
            const middle = (low + high) / 2;
            if ((1 + middle) * Math.exp(-middle) > target) low = middle;
            else high = middle;
        }
        return high;
    }

    const SPRING_FLAT = flatDecay(SPRING_SETTLED);

    // One that overshoots swings inside an envelope that shrinks as
    // `e^(-zeta omega t)`; its swing is `1 / sqrt(1 - zeta^2)` of that.
    function makeSpring(settleMs, zeta = 1) {
        const decay = zeta >= SPRING_FLAT_ZETA
            ? SPRING_FLAT
            : -Math.log(SPRING_SETTLED * Math.sqrt(1 - zeta * zeta)) / zeta;
        return { settleMs, zeta, omega: decay / settleMs };
    }

    // The distance still to go, and how fast that is changing, `time` ms
    // into a spring that started `from` away from its target (1 for a whole
    // motion) and closing at `speed` (negative while it gets nearer, per ms).
    function springAt(spring, time, from = 1, speed = 0) {
        const { omega, zeta } = spring;
        const gone = Math.exp(-zeta * omega * time);
        if (zeta >= SPRING_FLAT_ZETA) {
            const carry = speed + omega * from;
            const wave = from + carry * time;
            return {
                left: wave * gone,
                speed: (carry - omega * wave) * gone,
            };
        }
        const beat = omega * Math.sqrt(1 - zeta * zeta);
        const sine = (speed + zeta * omega * from) / beat;
        const cos = Math.cos(beat * time);
        const sin = Math.sin(beat * time);
        return {
            left: gone * (from * cos + sine * sin),
            speed: gone * (
                (sine * beat - zeta * omega * from) * cos
                - (from * beat + zeta * omega * sine) * sin
            ),
        };
    }

    // How far a spring has come, from 0 to 1, `time` ms in.
    function springProgressAt(spring, time) {
        return 1 - springAt(spring, time).left;
    }

    // The easing for a motion that starts `from` of the way to its target
    // (as a fraction of the whole way) and is already moving at `speed`
    // (fractions of the whole way per ms): it is 0 where the motion starts
    // and 1 where it ends, so it fits any pair of keyframes.
    function springSamples(
        spring,
        from = 0,
        speed = 0,
        points = SPRING_POINTS,
        until = 1,
    ) {
        const total = 1 - from;
        if (total < 1e-6) return [0, 1];
        const at = (time) => (
            1 - springAt(spring, time, total, -speed).left / total
        );
        // The curve is stretched by what it still lacks at its last point,
        // so it lands on 1 without a jump at the end.
        const span = spring.settleMs * until;
        const settled = at(span);
        const samples = [];
        for (let i = 0; i <= points; i += 1) {
            samples.push(at((span * i) / points) / settled);
        }
        samples[0] = 0;
        samples[points] = 1;
        return samples;
    }

    function springEasing(
        spring,
        from = 0,
        speed = 0,
        points = SPRING_POINTS,
        until = 1,
    ) {
        const samples = springSamples(spring, from, speed, points, until);
        return `linear(${samples.map((value) => (
            Number(value.toFixed(4))
        )).join(', ')})`;
    }

