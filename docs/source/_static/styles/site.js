(function() {
    var still = !window.matchMedia
        || window.matchMedia("(prefers-reduced-motion: reduce)").matches
        || !Element.prototype.animate;
    var segmenter = window.Intl && Intl.Segmenter
        ? new Intl.Segmenter(undefined, {granularity: "grapheme"})
        : null;

    function make(name, content) {
        var element = document.createElement("span");
        element.className = "am-greetings__" + name;
        if (content !== undefined) element.textContent = content;
        return element;
    }

    function split(word) {
        if (!segmenter) return Array.from(word);
        return Array.from(segmenter.segment(word), function(part) {
            return part.segment;
        });
    }

    function greet(box) {
        var text = box.querySelector(".am-greetings__text");
        var word = box.querySelector(".am-greetings__word");
        var greetings = [];
        var interval = Number(box.dataset.amInterval);
        var duration = Number(box.dataset.amDuration);
        var stagger = Number(box.dataset.amStagger);
        var index = 0;

        function next() {
            var from = greetings[index];
            index = (index + 1) % greetings.length;
            var to = greetings[index];
            roll(from, to, function() {
                word.textContent = to;
                text.removeAttribute("aria-hidden");
                setTimeout(next, interval);
            });
        }

        function measure(text, parts) {
            var at = 0;
            var base;

            word.textContent = text;
            base = word.getBoundingClientRect().left;
            return parts.map(function(part) {
                var range = document.createRange();
                range.setStart(word.firstChild, at);
                range.setEnd(word.firstChild, at + part.length);
                at += part.length;
                var box = range.getBoundingClientRect();
                return {x: box.left - base, w: box.width};
            });
        }

        function roll(from, to, done) {
            var before = split(from);
            var after = split(to);
            var count = Math.max(before.length, after.length);
            var easing = getComputedStyle(document.documentElement)
                .getPropertyValue("--km-ease-smooth").trim();
            var width = word.offsetWidth;
            var old = measure(from, before);
            var now = measure(to, after);
            var last;

            width = Math.max(width, word.offsetWidth);
            text.setAttribute("aria-hidden", "true");
            word.textContent = "";
            word.style.width = width + "px";
            for (var i = 0; i < count; i++) {
                var edges = [old[i], now[i]].filter(Boolean);
                var left = Math.min.apply(null, edges.map(function(_) {
                    return _.x;
                }));
                var right = Math.max.apply(null, edges.map(function(_) {
                    return _.x + _.w;
                }));
                var cube = make("cube");
                var front = make(
                    "face am-greetings__face--front", before[i] || ""
                );
                var back = make(
                    "face am-greetings__face--back", after[i] || ""
                );
                var slot = make("slot");
                var timing = {
                    duration: duration,
                    delay: i * stagger,
                    easing: easing,
                    fill: "both"
                };
                slot.style.left = left + "px";
                slot.style.width = (right - left) + "px";
                if (old[i]) front.style.left = (old[i].x - left) + "px";
                if (now[i]) back.style.left = (now[i].x - left) + "px";
                cube.appendChild(front);
                cube.appendChild(back);
                slot.appendChild(cube);
                word.appendChild(slot);
                cube.animate([
                    {transform: "translateZ(-0.625em) rotateX(0deg)"},
                    {transform: "translateZ(-0.625em) rotateX(90deg)"}
                ], timing);
                front.animate(
                    [{filter: "blur(0px)"}, {filter: "blur(2px)"}], timing
                );
                last = back.animate(
                    [{filter: "blur(2px)"}, {filter: "blur(0px)"}], timing
                );
            }
            last.onfinish = function() {
                word.style.width = "";
                done();
            };
        }

        fetch(box.dataset.amSource)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                greetings = data.map(function(item) { return item.name; });
                if (!greetings.length) return;
                word.textContent = greetings[0];
                if (greetings.length > 1 && !still) {
                    setTimeout(next, interval);
                }
            })
            .catch(function() {});
    }

    document.querySelectorAll(".am-greetings").forEach(greet);
})();

(function() {
    const reduceMotionQuery = window.matchMedia(
        '(prefers-reduced-motion: reduce)'
    );

    function contribute(box) {
        const scrollers = box.querySelectorAll(
            '.am-contributed__scroller'
        );

        function setup() {
            scrollers.forEach((scroller) => {
                const list = scroller.querySelector(
                    '.am-contributed__list'
                );
                if (!list) return;
                const originals = Array.from(list.children);
                if (originals.length < 2) {
                    scroller.dataset.amAnimated = 'false';
                    return;
                }

                let resizeObserver;
                let lastDistance = 0;
                let resizeHandlerAttached = false;

                function updateLoopDistance() {
                    const first = list.children[originals.length];
                    if (!first) return;
                    const firstLeft = first.getBoundingClientRect().left;
                    const loopDistance = firstLeft -
                        list.children[0].getBoundingClientRect().left;
                    if (!loopDistance) return;
                    if (Math.abs(loopDistance - lastDistance) < 0.5) return;
                    lastDistance = loopDistance;
                    list.style.setProperty(
                        '--am-contributed-loop-distance',
                        `${loopDistance}px`
                    );
                }

                function bindResizeListener() {
                    if (typeof ResizeObserver !== 'undefined') {
                        if (resizeObserver) return;
                        resizeObserver = new ResizeObserver(
                            () => updateLoopDistance()
                        );
                        resizeObserver.observe(list);
                    } else if (!resizeHandlerAttached) {
                        resizeHandlerAttached = true;
                        window.addEventListener('resize', updateLoopDistance, {
                            passive: true
                        });
                    }
                }

                function enableAnimation() {
                    if (reduceMotionQuery.matches) return;
                    scroller.dataset.amAnimated = 'true';
                    updateLoopDistance();
                }

                function initialise() {
                    if (!scroller.dataset.amCloned) {
                        originals.forEach((item) => {
                            const clone = item.cloneNode(true);
                            clone.setAttribute('aria-hidden', 'true');
                            list.appendChild(clone);
                        });
                        scroller.dataset.amCloned = '1';
                        bindResizeListener();
                    }
                    requestAnimationFrame(() => enableAnimation());
                }

                if (reduceMotionQuery.matches) {
                    scroller.dataset.amAnimated = 'false';
                } else {
                    initialise();
                }

                reduceMotionQuery.addEventListener('change', (event) => {
                    if (event.matches) {
                        scroller.dataset.amAnimated = 'false';
                        list.style.removeProperty(
                            '--am-contributed-loop-distance'
                        );
                    } else {
                        initialise();
                    }
                });
            });
        }

        function render(organisations) {
            const list = box.querySelector(
                '.am-contributed__list'
            );
            organisations.forEach((organisation) => {
                const item = document.createElement('li');
                item.className = 'am-contributed__item';
                if (organisation.raised) {
                    item.classList.add(
                        'am-contributed__item--raised'
                    );
                }
                item.style.setProperty(
                    '--am-contributed-logo',
                    `url("${organisation.logo}")`
                );
                if (organisation.width) {
                    item.style.inlineSize = organisation.width;
                }
                const label = document.createElement('span');
                label.className = 'km-sr-only';
                label.textContent = organisation.name;
                item.appendChild(label);
                list.appendChild(item);
            });
        }

        fetch(box.dataset.amSource)
            .then((response) => response.json())
            .then((organisations) => {
                render(organisations);
                setup();
            })
            .catch(() => {});
    }

    document.querySelectorAll('.am-contributed').forEach(
        contribute
    );
})();

(function() {
    var still = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"];
    var SLIP = 0.03;
    var SOLID = 350;

    function normal() {
        return (Math.random() + Math.random() + Math.random() - 1.5) / 0.5;
    }

    function slip(char) {
        var lower = char.toLowerCase();
        var near = [];
        ROWS.forEach(function(row, y) {
            var x = row.indexOf(lower);
            if (x === -1) return;
            near.push(row.charAt(x - 1), row.charAt(x + 1));
            if (ROWS[y - 1]) near.push(ROWS[y - 1].charAt(x));
            if (ROWS[y + 1]) near.push(ROWS[y + 1].charAt(x));
        });
        near = near.filter(Boolean);
        if (!near.length) return "";
        var key = near[Math.floor(Math.random() * near.length)];
        return char === lower ? key : key.toUpperCase();
    }

    function gap(previous, speed, drift) {
        var wait = speed * drift * Math.exp(normal() * 0.3);
        if (previous === " ") {
            wait += speed * (0.3 + Math.random() * 0.7);
        } else if (previous === "," || previous === "-") {
            wait += speed * (0.8 + Math.random() * 1.2);
        }
        if (Math.random() < 0.05) wait += speed * (2 + Math.random() * 3);
        return Math.round(wait);
    }

    function typing(word, speed, back) {
        var steps = [];
        var shown = "";
        var drift = 1;
        var careful = false;

        function put(text, wait) {
            steps.push({text: text, wait: wait});
            shown = text;
        }

        while (shown !== word) {
            var at = shown.length;
            var char = word.charAt(at);
            var wrong = at > 0 && !careful && Math.random() < SLIP
                ? slip(char)
                : "";
            drift = Math.min(
                1.25, Math.max(0.8, drift + (Math.random() - 0.5) * 0.2)
            );
            careful = false;
            if (!wrong) {
                put(shown + char, gap(word.charAt(at - 1), speed, drift));
                continue;
            }
            var run = Math.min(
                word.length - at - 1, Math.floor(Math.random() * 3)
            );
            put(shown + wrong, gap(word.charAt(at - 1), speed, drift));
            for (var i = 1; i <= run; i++) {
                put(
                    shown + word.charAt(at + i),
                    gap(word.charAt(at + i - 1), speed, drift)
                );
            }
            for (var j = 0; j <= run; j++) {
                put(
                    shown.slice(0, -1),
                    j
                        ? Math.round(back * (0.8 + Math.random() * 0.4))
                        : Math.round(speed * (2 + Math.random() * 2))
                );
            }
            careful = true;
        }
        return steps;
    }

    function deleting(word, back) {
        var steps = [];
        for (var i = word.length - 1; i >= 0; i--) {
            var held = word.length - 1 - i;
            var wait = held === 0
                ? back * 1.5
                : held === 1 ? back * 4 : back * (0.85 + Math.random() * 0.3);
            steps.push({text: word.slice(0, i), wait: Math.round(wait)});
        }
        return steps;
    }

    function teach(box) {
        var element = box.querySelector(".am-currently-teaching__course");
        var cursor = box.querySelector(".am-blinking-cursor");
        var speed = Number(box.dataset.amTypingSpeed);
        var back = Number(box.dataset.amDeletingSpeed);
        var pauseTyped = Number(box.dataset.amPauseAfterTyping);
        var pauseDeleted = Number(box.dataset.amPauseAfterDeleting);
        var courses = [];
        var index = 0;
        var rest;

        function show(text) {
            element.textContent = text;
            cursor.classList.add("am-is-typing");
            clearTimeout(rest);
            rest = setTimeout(function() {
                cursor.classList.remove("am-is-typing");
            }, SOLID);
        }

        function play(steps, lead, done) {
            var at = 0;

            function step() {
                show(steps[at].text);
                at++;
                if (at < steps.length) {
                    setTimeout(step, steps[at].wait);
                } else {
                    done();
                }
            }

            setTimeout(step, lead + steps[0].wait);
        }

        function cycle() {
            var word = courses[index];
            index = (index + 1) % courses.length;
            play(typing(word, speed, back), pauseDeleted, function() {
                play(deleting(word, back), pauseTyped, cycle);
            });
        }

        function start() {
            if (still) {
                element.textContent = courses.length > 1
                    ? courses.slice(0, -1).join(", ") + " and " +
                        courses[courses.length - 1]
                    : courses[0];
                cursor.style.display = "none";
                return;
            }
            cycle();
        }

        fetch(box.dataset.amSource)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                courses = data.map(function(item) { return item.name; });
                if (courses.length) start();
            })
            .catch(function() {});
    }

    document.querySelectorAll(".am-currently-teaching").forEach(teach);
})();
