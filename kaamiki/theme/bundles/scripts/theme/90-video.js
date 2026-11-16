    function enrichYouTubeBlock(block) {
        const id = block.getAttribute('data-km-youtube-id');
        if (!id) return;
        const title = block.querySelector('.km-thumbnail__title a');
        const channel = block.querySelector('.km-thumbnail__channel');
        const picture = block.querySelector('.km-thumbnail__image img');
        const writtenTitle = block.hasAttribute('data-km-youtube-title');
        const writtenChannel = block.hasAttribute('data-km-youtube-channel');

        const watch = encodeURIComponent(
            `https://www.youtube.com/watch?v=${id}`,
        );
        fetchJson(
            `https://www.youtube.com/oembed?url=${watch}&format=json`,
        ).then((data) => {
            if (!data) return;
            if (!writtenTitle && title && data.title) {
                title.textContent = data.title;
                if (picture) picture.alt = data.title;
            }
            if (!writtenChannel && channel && data.author_name) {
                channel.textContent = data.author_name;
            }
            if (channel && data.author_url) {
                linkChannel(channel, title, data.author_url);
            }
        });
    }

    function linkChannel(channel, title, address) {
        let url;
        try {
            url = new URL(address);
        } catch {
            return;
        }
        if (
            url.protocol !== 'https:'
            || !/(^|\.)youtube\.com$/.test(url.hostname)
        ) {
            return;
        }
        const link = document.createElement('a');
        link.href = url.href;
        if (title) {
            link.target = title.target;
            link.rel = title.rel;
        }
        link.append(...channel.childNodes);
        channel.append(link);
    }

    function initYouTubeBlocks() {
        onVisible(
            document.querySelectorAll('.km-thumbnail[data-km-youtube-id]'),
            enrichYouTubeBlock,
        );
    }

    // Safari, and every browser on an iPhone or iPad, which all run WebKit.
    function isWebKit() {
        return /AppleWebKit/.test(navigator.userAgent)
            && !/Chrome\/|Chromium\/|Edg\/|Android/.test(navigator.userAgent);
    }

    // A player that was asked to start and hasn't (a browser that only lets
    // a muted one play without a press inside the frame) is told to play
    // muted, so a press on the thumbnail always ends in a video that plays.
    function steerPlayer(frame) {
        const origin = new URL(frame.src).origin;
        let state = null;
        let timer = 0;
        const send = (message) => frame.contentWindow?.postMessage(
            JSON.stringify(message),
            origin,
        );
        const command = (func) => send({ event: 'command', func, args: [] });
        const stalled = () => state === -1 || state === 5;
        window.addEventListener('message', (event) => {
            if (event.source !== frame.contentWindow) return;
            let data;
            try {
                data = JSON.parse(event.data);
            } catch {
                return;
            }
            if (data.event === 'onStateChange') state = data.info;
            if (data.event === 'infoDelivery'
                && data.info && 'playerState' in data.info) {
                state = data.info.playerState;
            }
            if (data.event !== 'onReady' || timer) return;
            command('playVideo');
            timer = window.setTimeout(() => {
                if (!stalled()) return;
                command('mute');
                command('playVideo');
            }, YOUTUBE_PLAY_WAIT_MS);
        });
        frame.addEventListener('load', () => send({
            event: 'listening',
            id: frame.id,
            channel: 'widget',
        }));
    }

    function initYouTubeFacades() {
        document.querySelectorAll('[data-km-facade]').forEach((facade) => {
            facade.addEventListener('click', (event) => {
                if (isModifiedClick(event)) return;
                event.preventDefault();
                const url = new URL(
                    facade.getAttribute('data-km-facade-src'),
                    window.location.href,
                );
                url.searchParams.set('autoplay', '1');
                url.searchParams.set('enablejsapi', '1');
                if (window.location.protocol !== 'file:') {
                    url.searchParams.set('origin', window.location.origin);
                }
                if (isWebKit()) url.searchParams.set('mute', '1');
                const frame = document.createElement('iframe');
                frame.className = 'km-media__iframe';
                frame.src = url.href;
                frame.title = facade.getAttribute('data-km-facade-title') || '';
                frame.allow = facade.getAttribute('data-km-facade-allow') || '';
                frame.referrerPolicy = facade
                    .getAttribute('data-km-facade-referrer') || '';
                frame.allowFullscreen = true;
                facade.replaceWith(frame);
                steerPlayer(frame);
                frame.focus();
            });
        });
    }

    function initVideoFlags() {
        document.querySelectorAll('.km-media--video video').forEach((video) => {
            const frame = video.closest('.km-media__frame');
            const sync = () => frame.classList.toggle(
                'km-media__frame--paused',
                video.paused,
            );
            ['play', 'pause', 'ended', 'loadedmetadata'].forEach((name) => {
                video.addEventListener(name, sync, { passive: true });
            });
            sync();
        });
    }

    function initVideoAutoplay() {
        const held = new WeakSet();
        const watcher = new IntersectionObserver((entries) => {
            entries.forEach(({ target, isIntersecting }) => {
                if (isIntersecting) {
                    if (held.delete(target)) target.play().catch(() => {});
                } else if (!target.paused) {
                    held.add(target);
                    target.pause();
                }
            });
        });
        document.querySelectorAll(
            '.km-media--video video[autoplay]',
        ).forEach((video) => {
            watcher.observe(video);
        });
    }

