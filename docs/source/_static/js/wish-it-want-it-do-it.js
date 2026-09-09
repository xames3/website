/*
Wish It. Want It. Do It. widget behaviour
=========================================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 August, 2026
Last updated on: 09 September, 2026
*/

// Note. This file is entirely vibe-coded using Claude Code.

(function () {
    const SIGNALR_CLIENT_CDN_URL = 'https://cdn.jsdelivr.net/npm/@microsoft/signalr@8.0.7/dist/browser/signalr.min.js';

    const HOST_CHARACTER = 'God';
    const HIDDEN = 'site-wish-it-want-it-do-it--hidden';

    // Matches the backend's `MAX_IMAGE_DATA_URI_LENGTH` -- a submission's
    // content lives in one Table Storage property, hard-capped at 64KiB
    // by the platform, so an attached image has to fit under that as a
    // `data:image/...;base64,...` string.
    const MAX_IMAGE_DATA_URI_LENGTH = 60000;
    const IMAGE_DATA_URI_PREFIX = 'data:image/';

    function isImageContent(content) {
        return typeof content === 'string' && content.startsWith(IMAGE_DATA_URI_PREFIX);
    }

    const CHARACTER_AVATARS = {
        'Adam': 'https://i.imgur.com/dkDNA8Q.png',
        'Babs': 'https://i.imgur.com/72NLPni.png',
        'Bonnie': 'https://i.imgur.com/qz3zcPG.png',
        'Brian': 'https://i.imgur.com/UQTRSMN.png',
        'Bruce': 'https://i.imgur.com/p9n83Dy.png',
        'Carter': 'https://i.imgur.com/tqoou5t.png',
        'Chris': 'https://i.imgur.com/oVk6Uqg.png',
        'Cleveland': 'https://i.imgur.com/Jj8L6aL.png',
        'Consuela': 'https://i.imgur.com/Rs42UQn.png',
        'God': 'https://i.imgur.com/qmi1utl.png',
        'Hartman': 'https://i.imgur.com/zYmKDIc.png',
        'Herbert': 'https://i.imgur.com/jVNORMF.png',
        'Joe': 'https://i.imgur.com/XNnNPMK.png',
        'Lois': 'https://i.imgur.com/ebwwb1u.png',
        'Meg': 'https://i.imgur.com/Y2yCFnQ.png',
        'Mort': 'https://i.imgur.com/NdjLJBo.png',
        'Peter': 'https://i.imgur.com/iUDCTZR.png',
        'Quagmire': 'https://i.imgur.com/BZXVyFv.png',
        'Stewie': 'https://i.imgur.com/ngyn7Es.png',
        'Tom': 'https://i.imgur.com/jVPKW6Z.png',
    };

    function avatarImageFor(displayName) {
        return CHARACTER_AVATARS[displayName] || null;
    }

    function initialsFor(displayName) {
        return String(displayName || '?').trim().slice(0, 2).toUpperCase();
    }

    function ensureSignalRLoaded() {
        if (window.signalR) return Promise.resolve();
        if (window.__wishItWantItDoItSignalRPromise) return window.__wishItWantItDoItSignalRPromise;
        window.__wishItWantItDoItSignalRPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = SIGNALR_CLIENT_CDN_URL;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load SignalR client.'));
            document.head.appendChild(script);
        });
        return window.__wishItWantItDoItSignalRPromise;
    }

    class ApiError extends Error {
        constructor(message, status) {
            super(message);
            this.name = 'ApiError';
            this.status = status;
        }
    }

    function initWishItWantItDoIt(root) {
        const UID = root.id;
        const API_BASE = root.dataset.apiBaseUrl || '';
        const HEADCOUNT_MAX = Number(root.dataset.headcountMax || 20);
        const STORAGE_KEY = 'wish-it-want-it-do-it-session-' + UID;
        const DRAFT_KEY = 'wish-it-want-it-do-it-draft-' + UID;
        const $ = (id) => document.getElementById(UID + '-' + id);

        let hostToken = null;
        let roomCode = null;
        let participantId = null;
        let sessionToken = null;
        let isHost = false;
        let myDisplayName = null;
        let joinOpen = true;
        let connection = null;
        let reconnectAttempts = 0;
        let currentPhase = 'choice';
        let resultsItems = [];
        let resultsIndex = 0;
        let resultsDismissed = false;
        let mySubmissions = [];
        let mySubmissionCursor = 0;
        let mySubmissionsHydrated = false;
        let composerImages = [];
        let lastParticipants = [];
        let lastExpectedHeadcount = HEADCOUNT_MAX;

        const headcountInput = $('choice-headcount');
        if (headcountInput) {
            headcountInput.max = String(HEADCOUNT_MAX);
            headcountInput.min = '1';
        }

        function setNotice(el, message, level) {
            if (!el) return;
            el.textContent = '';
            if (!message) {
                el.classList.add(HIDDEN);
                return;
            }
            const box = document.createElement('div');
            box.className = 'admonition ' + level + ' site-wish-it-want-it-do-it__notice';
            const heading = document.createElement('p');
            heading.className = 'admonition-title';
            heading.textContent = level === 'warning' ? 'Warning' : 'Error';
            const body = document.createElement('p');
            body.textContent = message;
            box.appendChild(heading);
            box.appendChild(body);
            el.appendChild(box);
            el.classList.remove(HIDDEN);
        }

        function showError(el, message) {
            setNotice(el, message, 'error');
        }

        function showWarning(el, message) {
            setNotice(el, message, 'warning');
        }

        function clearNotice(el) {
            setNotice(el, '', 'error');
        }

        function setStatus(message, level) {
            setNotice($('connection-status'), message, level || 'warning');
        }

        function noticeFor(err) {
            return err instanceof ApiError && err.status >= 400 && err.status < 500
                ? showWarning
                : showError;
        }

        function reportError(el, err) {
            noticeFor(err)(el, err.message);
        }

        let historyTrapArmed = false;

        function onPopState() {
            if (!historyTrapArmed) return;
            history.pushState({ wishItWantItDoIt: UID }, '');
        }

        function armHistoryTrap() {
            if (historyTrapArmed) return;
            historyTrapArmed = true;
            history.pushState({ wishItWantItDoIt: UID }, '');
            window.addEventListener('popstate', onPopState);
        }

        function disarmHistoryTrap() {
            if (!historyTrapArmed) return;
            historyTrapArmed = false;
            window.removeEventListener('popstate', onPopState);
        }

        function showPhase(phase) {
            currentPhase = phase;
            ['choice', 'lobby', 'submission', 'voting', 'results'].forEach((p) => {
                const el = $('phase-' + p);
                if (el) el.classList.toggle(HIDDEN, p !== phase);
            });
            if (phase === 'voting' || phase === 'results') {
                armHistoryTrap();
            } else {
                disarmHistoryTrap();
            }
            if (phase !== 'submission') mySubmissionsHydrated = false;
            renderLeaveLink();
        }

        function canActuallyLeave() {
            return !isHost && ['lobby', 'submission', 'voting'].includes(currentPhase);
        }

        function renderLeaveLink() {
            const link = $('leave-session');
            if (!link) return;
            if (isHost) {
                link.classList.add(HIDDEN);
                return;
            }
            link.classList.toggle(HIDDEN, currentPhase === 'choice');
            link.textContent = canActuallyLeave() ? 'Not you? Leave the room' : 'Not you? Leave and start over';
        }

        $('leave-session').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            if (canActuallyLeave()) {
                const warning = currentPhase === 'lobby'
                    ? 'Leave the room? Your seat and character free up for someone else.'
                    : "Leave the room? Anything you've submitted is removed, and your seat frees up.";
                if (!window.confirm(warning)) return;
                let serverConfirmed = false;
                try {
                    await api('/rooms/' + roomCode + '/leave', {
                        method: 'POST',
                        body: JSON.stringify({
                            sessionToken
                        }),
                    });
                    serverConfirmed = true;
                } catch {
                    /* still leave locally below */
                }
                leaveToChoice(
                    serverConfirmed ? '' : "Left here, but couldn't reach the server to free your seat. Tell the host if it still shows you as joined.",
                    'warning'
                );
                return;
            }
            if (!window.confirm('This forgets your session on this device. Continue?')) return;
            leaveToChoice('');
        }));

        function resetHostChoiceFields() {
            const signedIn = Boolean(hostToken);
            $('host-login-fields').classList.toggle(HIDDEN, signedIn);
            $('host-create-fields').classList.toggle(HIDDEN, !signedIn);
            clearNotice($('login-error'));
            clearNotice($('choice-host-error'));
            clearNotice($('choice-join-error'));
        }

        function saveSession() {
            try {
                sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
                    roomCode,
                    participantId,
                    sessionToken,
                    isHost,
                    myDisplayName,
                }));
            } catch {
                /* private mode, or a full quota -- the session just won't resume */
            }
        }

        function readDraft() {
            try {
                return sessionStorage.getItem(DRAFT_KEY) || '';
            } catch {
                return '';
            }
        }

        function saveDraft(text) {
            try {
                if (text) sessionStorage.setItem(DRAFT_KEY, text);
                else sessionStorage.removeItem(DRAFT_KEY);
            } catch {
                /* nothing to do -- an unsaved draft is not worth an error */
            }
        }

        async function teardownConnection() {
            const existing = connection;
            connection = null;
            if (!existing) return;
            try {
                await existing.stop();
            } catch {
                /* already closed */
            }
        }

        function clearSession() {
            try {
                sessionStorage.removeItem(STORAGE_KEY);
            } catch {
                /* nothing to clear */
            }
            saveDraft('');
            roomCode = participantId = sessionToken = myDisplayName = null;
            isHost = false;
            joinOpen = true;
            reconnectAttempts = 0;
            mySubmissions = [];
            mySubmissionCursor = 0;
            mySubmissionsHydrated = false;
            composerImages = [];
            lastParticipants = [];
            resultsItems = [];
            resultsIndex = 0;
            resultsDismissed = false;
            resetHostChoiceFields();
            teardownConnection();
        }

        function leaveToChoice(message, level) {
            clearSession();
            showPhase('choice');
            setStatus(message || '', level || 'warning');
        }

        async function api(path, options) {
            options = options || {};
            const headers = Object.assign({
                'Content-Type': 'application/json'
            }, options.headers || {});
            let response;
            try {
                response = await fetch(API_BASE + path, Object.assign({}, options, {
                    headers
                }));
            } catch {
                throw new ApiError('Couldn\'t reach the server, try again.', 0);
            }
            let body = null;
            try {
                body = await response.json();
            } catch {
                /* empty body is fine */
            }
            if (!response.ok) {
                const message = (body && body.error) || ('Request failed (' + response.status + ')');
                throw new ApiError(message, response.status);
            }
            return body;
        }

        async function withButtonBusy(button, fn) {
            if (!button || button.disabled) return;
            button.disabled = true;
            try {
                await fn();
            } finally {
                button.disabled = false;
            }
        }

        function onEnter(input, handler) {
            if (!input) return;
            input.addEventListener('keydown', (event) => {
                if (event.key !== 'Enter') return;
                event.preventDefault();
                handler();
            });
        }

        // ------------------------------------------------------------
        // Choice phase
        // ------------------------------------------------------------

        function submitLogin() {
            return withButtonBusy($('login-submit'), async () => {
                const username = $('login-username').value.trim();
                const password = $('login-password').value;
                clearNotice($('login-error'));
                if (!username || !password) {
                    showWarning($('login-error'), 'Enter both a username and a password.');
                    return;
                }
                try {
                    const result = await api('/login', {
                        method: 'POST',
                        body: JSON.stringify({
                            username,
                            password
                        }),
                    });
                    hostToken = result.hostToken;
                    $('login-password').value = '';
                    $('host-login-fields').classList.add(HIDDEN);
                    $('host-create-fields').classList.remove(HIDDEN);
                } catch (err) {
                    reportError($('login-error'), err);
                }
            });
        }

        $('login-submit').addEventListener('click', submitLogin);
        onEnter($('login-username'), submitLogin);
        onEnter($('login-password'), submitLogin);

        function createRoom() {
            return withButtonBusy($('choice-create'), async () => {
                clearNotice($('choice-host-error'));
                const headcount = parseInt($('choice-headcount').value, 10);
                if (!headcount || headcount < 1 || headcount > HEADCOUNT_MAX) {
                    showWarning($('choice-host-error'), 'Enter a headcount from 1 to ' + HEADCOUNT_MAX + '.');
                    return;
                }
                if (!hostToken) {
                    showWarning($('choice-host-error'), 'Sign in again first.');
                    resetHostChoiceFields();
                    return;
                }
                try {
                    const result = await api('/rooms', {
                        method: 'POST',
                        body: JSON.stringify({
                            hostToken,
                            expectedHeadcount: headcount,
                        }),
                    });
                    roomCode = result.roomCode;
                    participantId = result.participantId;
                    sessionToken = result.sessionToken;
                    isHost = true;
                    myDisplayName = result.displayName || HOST_CHARACTER;
                    saveSession();
                    await enterRoom();
                } catch (err) {
                    if (err instanceof ApiError && err.status === 401) {
                        hostToken = null;
                        resetHostChoiceFields();
                    }
                    reportError($('choice-host-error'), err);
                }
            });
        }

        $('choice-create').addEventListener('click', createRoom);
        onEnter($('choice-headcount'), createRoom);

        function joinRoom() {
            return withButtonBusy($('choice-join'), async () => {
                clearNotice($('choice-join-error'));
                const code = $('choice-room-code').value.trim().toUpperCase();
                if (!code) {
                    showWarning($('choice-join-error'), 'Enter a room code.');
                    return;
                }
                try {
                    const result = await api('/rooms/' + encodeURIComponent(code) + '/join', {
                        method: 'POST',
                        body: JSON.stringify({}),
                    });
                    roomCode = code;
                    participantId = result.participantId;
                    sessionToken = result.sessionToken;
                    isHost = false;
                    myDisplayName = result.displayName;
                    saveSession();
                    await enterRoom();
                } catch (err) {
                    reportError($('choice-join-error'), err);
                }
            });
        }

        $('choice-join').addEventListener('click', joinRoom);
        onEnter($('choice-room-code'), joinRoom);

        $('choice-room-code').addEventListener('input', (event) => {
            event.target.value = event.target.value.toUpperCase();
        });

        async function enterRoom() {
            setStatus('');
            try {
                await connectRealtime();
            } catch {
                setStatus('Live updates are unavailable. The page will still work, but may lag behind.', 'warning');
            }
            await resyncState();
        }

        // ------------------------------------------------------------
        // Lobby
        // ------------------------------------------------------------

        const AVATAR_STACK_LIMIT_DESKTOP = 8;
        const AVATAR_STACK_LIMIT_MOBILE = 4;

        function currentAvatarStackLimit() {
            return window.matchMedia('(min-width: 900px)').matches
                ? AVATAR_STACK_LIMIT_DESKTOP
                : AVATAR_STACK_LIMIT_MOBILE;
        }

        function renderParticipants(participants, expectedHeadcount) {
            lastParticipants = participants || [];
            lastExpectedHeadcount = expectedHeadcount;
            const list = $('lobby-participants');
            if (!list) return;
            list.textContent = '';
            const ordered = [
                ...lastParticipants.filter((p) => p.participantId === participantId),
                ...lastParticipants.filter((p) => p.isHost && p.participantId !== participantId),
                ...lastParticipants.filter((p) => !p.isHost && p.participantId !== participantId),
            ];
            const visible = ordered.slice(0, currentAvatarStackLimit());
            const overflowCount = ordered.length - visible.length;
            visible.forEach((p, index) => {
                const isMe = p.participantId === participantId;
                const li = document.createElement('li');
                let className = 'site-wish-it-want-it-do-it__avatar';
                if (isMe) className += ' site-wish-it-want-it-do-it__avatar--you';
                if (p.isHost) className += ' site-wish-it-want-it-do-it__avatar--host';
                li.className = className;
                const image = avatarImageFor(p.displayName);
                if (image) {
                    li.style.backgroundImage = 'url(' + image + ')';
                } else {
                    li.textContent = initialsFor(p.displayName);
                }
                li.style.zIndex = String(visible.length - index);
                const label = p.isHost ? p.displayName + ' (host)' : p.displayName;
                li.title = isMe ? 'Me -- ' + label : label;
                list.appendChild(li);
            });
            if (overflowCount > 0) {
                const li = document.createElement('li');
                li.className = 'site-wish-it-want-it-do-it__avatar site-wish-it-want-it-do-it__avatar--overflow';
                li.style.zIndex = '0';
                li.textContent = '+' + overflowCount;
                li.title = overflowCount + ' more';
                list.appendChild(li);
            }
            $('lobby-count').textContent = lastParticipants.length + ' of ' + expectedHeadcount + ' joined for ' + roomCode;
            $('lobby-host-actions').classList.toggle(HIDDEN, !isHost);
            renderLobbyDoor();
        }

        function renderLobbyDoor() {
            const button = $('lobby-toggle-join');
            const status = $('lobby-status');
            if (button) {
                button.textContent = joinOpen ? 'Lock' : 'Unlock';
                button.setAttribute('aria-pressed', String(!joinOpen));
            }
            if (!status) return;
            if (isHost) {
                status.textContent = joinOpen
                    ? 'The room is open. Anyone with the code can join.'
                    : 'The room is locked. Nobody new can join.';
            } else {
                status.textContent = joinOpen ? '' : 'The host has locked the room.';
            }
        }

        let avatarResizeTimer = null;
        window.addEventListener('resize', () => {
            if (avatarResizeTimer) clearTimeout(avatarResizeTimer);
            avatarResizeTimer = setTimeout(() => {
                if (currentPhase === 'lobby' && lastParticipants.length) {
                    renderParticipants(lastParticipants, lastExpectedHeadcount);
                }
            }, 150);
        });

        $('lobby-toggle-join').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            const next = !joinOpen;
            try {
                const result = await api('/rooms/' + roomCode + '/lobby', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken,
                        open: next
                    }),
                });
                joinOpen = result.joinOpen;
                renderLobbyDoor();
                setStatus('');
            } catch (err) {
                setStatus(err.message, err.status >= 400 && err.status < 500 ? 'warning' : 'error');
            }
        }));

        $('lobby-start-submission').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            try {
                await api('/rooms/' + roomCode + '/force-start-submission', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken
                    }),
                });
                await resyncState();
                setStatus('');
            } catch (err) {
                setStatus(err.message, 'error');
            }
        }));

        async function stopSessionForEveryone(event) {
            const button = event && event.currentTarget;
            if (button && button.disabled) return;
            if (!roomCode) return;
            if (!window.confirm('This ends the session for everyone and returns them to the start. Continue?')) return;
            if (button) button.disabled = true;
            try {
                await api('/rooms/' + roomCode + '/stop', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken
                    }),
                });
                leaveToChoice('');
            } catch (err) {
                setStatus(err.message, 'error');
            } finally {
                if (button) button.disabled = false;
            }
        }

        $('lobby-stop-session').addEventListener('click', stopSessionForEveryone);
        $('submission-stop-session').addEventListener('click', stopSessionForEveryone);
        $('voting-stop-session').addEventListener('click', stopSessionForEveryone);
        $('restart-session').addEventListener('click', stopSessionForEveryone);

        window.addEventListener('pageshow', (event) => {
            if (event.persisted && roomCode && sessionToken) resyncState();
        });

        // ------------------------------------------------------------
        // Submission phase
        // ------------------------------------------------------------

        function updateSubmitEnabled() {
            const hasText = $('submission-textarea').value.trim().length > 0;
            $('submission-submit').disabled = !(hasText || composerImages.length > 0);
        }

        function renderImageChips() {
            const preview = $('submission-image-preview');
            const textarea = $('submission-textarea');
            preview.textContent = '';
            if (composerImages.length === 0) {
                preview.classList.add(HIDDEN);
                textarea.classList.remove(HIDDEN);
                updateSubmitEnabled();
                return;
            }
            preview.classList.remove(HIDDEN);
            textarea.classList.add(HIDDEN);
            composerImages.forEach((dataUri, index) => {
                const chip = document.createElement('div');
                chip.className = 'site-wish-it-want-it-do-it__composer-image-chip';
                // The blurred image is rendered slightly larger than this
                // wrapper and clipped to it, so the wrapper's crisp corners
                // define the chip's shape (blur is a whole-element effect,
                // so blurring the <img> directly would soften its edges
                // too, not just its content).
                const thumb = document.createElement('div');
                thumb.className = 'site-wish-it-want-it-do-it__composer-image-chip-thumb';
                const img = document.createElement('img');
                img.src = dataUri;
                img.alt = 'Attached image';
                img.draggable = false;
                thumb.appendChild(img);
                chip.appendChild(thumb);
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'site-wish-it-want-it-do-it__composer-image-chip-remove';
                removeBtn.setAttribute('aria-label', 'Remove image');
                removeBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
                removeBtn.addEventListener('click', () => {
                    composerImages.splice(index, 1);
                    renderImageChips();
                });
                chip.appendChild(removeBtn);
                preview.appendChild(chip);
            });
            updateSubmitEnabled();
        }

        function setComposerImages(dataUris) {
            composerImages = dataUris.slice();
            renderImageChips();
        }

        function loadImageFile(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onerror = () => reject(new Error('Could not read that file.'));
                reader.onload = () => {
                    const img = new Image();
                    img.onerror = () => reject(new Error("That file doesn't look like an image."));
                    img.onload = () => resolve(img);
                    img.src = reader.result;
                };
                reader.readAsDataURL(file);
            });
        }

        async function compressImageToDataUri(file) {
            if (!file.type.startsWith('image/')) {
                throw new Error('Please choose an image file.');
            }
            const img = await loadImageFile(file);
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            let maxDimension = 500;
            let quality = 0.7;
            for (let attempt = 0; attempt < 6; attempt++) {
                const scale = Math.min(1, maxDimension / Math.max(img.width, img.height));
                canvas.width = Math.max(1, Math.round(img.width * scale));
                canvas.height = Math.max(1, Math.round(img.height * scale));
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                const dataUri = canvas.toDataURL('image/jpeg', quality);
                if (dataUri.length <= MAX_IMAGE_DATA_URI_LENGTH) return dataUri;
                maxDimension = Math.round(maxDimension * 0.8);
                quality = Math.max(0.4, quality - 0.1);
            }
            throw new Error('That image is too large even after compressing. Try a smaller photo.');
        }

        function nextPaint() {
            // A single requestAnimationFrame only guarantees "before the
            // next paint" -- if a status message was just set and heavy
            // synchronous work follows immediately, the browser can still
            // batch that work into the same frame and never actually paint
            // the message at all. Nesting two rAFs waits until a paint has
            // genuinely happened, which is what makes "Processing..."
            // reliably show up before compression starts, and gives the
            // browser a real chance to stay responsive between files
            // instead of running the whole batch as one unbroken block.
            return new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        }

        async function handleImageFiles(fileList) {
            const files = Array.from(fileList || []).filter((f) => f.type.startsWith('image/'));
            if (!files.length) {
                showWarning($('submission-error'), 'Please choose an image file.');
                return;
            }
            clearNotice($('submission-error'));
            $('submission-status').textContent = files.length > 1 ? 'Processing images...' : 'Processing image...';
            await nextPaint();
            const compressed = [];
            const failures = [];
            for (const file of files) {
                try {
                    compressed.push(await compressImageToDataUri(file));
                } catch (err) {
                    failures.push(err.message);
                }
                await nextPaint();
            }
            $('submission-status').textContent = '';
            if (failures.length) {
                showWarning($('submission-error'), failures.length === 1
                    ? failures[0]
                    : failures.length + ' of those images could not be used. ' + failures[0]);
            }
            if (compressed.length) {
                setComposerImages(composerImages.concat(compressed));
            }
        }

        $('submission-attach-image').addEventListener('click', () => {
            $('submission-image-input').click();
        });

        $('submission-image-input').addEventListener('change', (event) => {
            handleImageFiles(event.target.files);
            event.target.value = '';
        });

        const submissionComposerEl = $('submission-composer');
        submissionComposerEl.addEventListener('dragover', (event) => {
            event.preventDefault();
            submissionComposerEl.classList.add('site-wish-it-want-it-do-it__composer--drag-over');
        });
        submissionComposerEl.addEventListener('dragleave', () => {
            submissionComposerEl.classList.remove('site-wish-it-want-it-do-it__composer--drag-over');
        });
        submissionComposerEl.addEventListener('drop', (event) => {
            event.preventDefault();
            submissionComposerEl.classList.remove('site-wish-it-want-it-do-it__composer--drag-over');
            handleImageFiles(event.dataTransfer.files);
        });

        function renderSubmissionNav() {
            const nav = $('submission-nav');
            // Needs to show once there's even a single real submission, not
            // just at 2+: viewing entry 1 of 1 plus "next" to reach the
            // blank compose slot is the only way to start a second, separate
            // submission once landing-on-what-you-just-added (rather than
            // auto-jumping past it) is the behavior. Hiding this at exactly
            // 1 submission left that slot completely unreachable.
            if (mySubmissions.length < 1) {
                nav.classList.add(HIDDEN);
                return;
            }
            nav.classList.remove(HIDDEN);
            const total = mySubmissions.length + 1;
            $('submission-nav-label').textContent = (mySubmissionCursor + 1) + ' of ' + total;
            $('submission-nav-prev').disabled = mySubmissionCursor === 0;
            $('submission-nav-next').disabled = mySubmissionCursor >= total - 1;
        }

        function loadSubmissionAtCursor() {
            const current = mySubmissions[mySubmissionCursor];
            if (current && isImageContent(current.content)) {
                $('submission-textarea').value = '';
                setComposerImages([current.content]);
            } else if (current) {
                setComposerImages([]);
                $('submission-textarea').value = current.content;
            } else {
                setComposerImages([]);
                $('submission-textarea').value = readDraft();
            }
            $('submission-status').textContent = current ? 'Submitted. You can keep editing until voting starts.' : '';
            renderSubmissionNav();
            updateSubmitEnabled();
        }

        $('submission-nav-prev').addEventListener('click', () => {
            if (mySubmissionCursor === 0) return;
            mySubmissionCursor -= 1;
            loadSubmissionAtCursor();
        });

        $('submission-nav-next').addEventListener('click', () => {
            if (mySubmissionCursor >= mySubmissions.length) return;
            mySubmissionCursor += 1;
            loadSubmissionAtCursor();
        });

        $('submission-textarea').addEventListener('input', (event) => {
            $('submission-status').textContent = '';
            clearNotice($('submission-error'));
            if (!mySubmissions[mySubmissionCursor]) saveDraft(event.target.value);
            updateSubmitEnabled();
        });

        let submissionSubmitInFlight = false;

        $('submission-submit').addEventListener('click', async (event) => {
            const button = event.currentTarget;
            if (submissionSubmitInFlight || button.disabled) return;
            clearNotice($('submission-error'));
            $('submission-status').textContent = '';
            const editing = mySubmissions[mySubmissionCursor];
            const textContent = $('submission-textarea').value.trim();
            if (composerImages.length === 0 && !textContent) {
                showWarning($('submission-error'), 'Paste or enter something, or attach an image.');
                return;
            }
            submissionSubmitInFlight = true;
            button.disabled = true;
            $('submission-status').textContent = 'Submitting...';
            try {
                let createdAny = false;
                if (composerImages.length > 0) {
                    // Each attached image becomes its own separate
                    // submission. If we're editing an existing entry, the
                    // first image replaces it in place; any further images
                    // become new entries after it.
                    for (let i = 0; i < composerImages.length; i++) {
                        const content = composerImages[i];
                        const target = i === 0 ? editing : undefined;
                        const result = await api('/rooms/' + roomCode + '/submit', {
                            method: 'POST',
                            body: JSON.stringify({
                                sessionToken,
                                content,
                                submissionId: target ? target.submissionId : undefined,
                            }),
                        });
                        if (target) {
                            target.content = content;
                        } else {
                            mySubmissions.push({
                                submissionId: result.submissionId,
                                content
                            });
                            createdAny = true;
                        }
                    }
                } else {
                    const result = await api('/rooms/' + roomCode + '/submit', {
                        method: 'POST',
                        body: JSON.stringify({
                            sessionToken,
                            content: textContent,
                            submissionId: editing ? editing.submissionId : undefined,
                        }),
                    });
                    if (editing) {
                        editing.content = textContent;
                    } else {
                        mySubmissions.push({
                            submissionId: result.submissionId,
                            content: textContent
                        });
                        createdAny = true;
                    }
                }
                saveDraft('');
                if (!createdAny) {
                    // Pure edit-in-place (existing text, or a single existing
                    // image swapped for another) -- nothing new was added to
                    // the list, so stay right where we are instead of
                    // jumping anywhere.
                    renderSubmissionNav();
                    $('submission-status').textContent = 'Submitted. You can keep editing until voting starts.';
                } else if (composerImages.length > 0) {
                    // Land on the last image actually just added, so the
                    // user sees confirmation of what they uploaded instead
                    // of an empty "N of N" slot that looks like the upload
                    // vanished. They can still attach more or use the
                    // arrows to review earlier ones.
                    mySubmissionCursor = mySubmissions.length - 1;
                    loadSubmissionAtCursor();
                    $('submission-status').textContent = 'Submitted! Use the arrows to review what you\'ve added, or attach more.';
                } else {
                    mySubmissionCursor = mySubmissions.length;
                    loadSubmissionAtCursor();
                    $('submission-status').textContent = 'Submitted! You can make another submission, or edit a previous one until The God starts voting.';
                }
            } catch (err) {
                $('submission-status').textContent = '';
                reportError($('submission-error'), err);
            } finally {
                submissionSubmitInFlight = false;
                updateSubmitEnabled();
            }
        });

        $('submission-start-voting').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            try {
                await api('/rooms/' + roomCode + '/force-start-voting', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken
                    }),
                });
                await resyncState();
                setStatus('');
            } catch (err) {
                setStatus(err.message, err.status === 409 ? 'warning' : 'error');
            }
        }));

        async function goBackToPhase(event) {
            const button = event.currentTarget;
            if (button.disabled) return;
            if (!window.confirm('Step the whole room back one stage. Continue?')) return;
            button.disabled = true;
            try {
                await api('/rooms/' + roomCode + '/go-back', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken
                    }),
                });
                await resyncState();
                setStatus('');
            } catch (err) {
                setStatus(err.message, 'error');
            } finally {
                button.disabled = false;
            }
        }

        $('submission-go-back').addEventListener('click', goBackToPhase);
        $('voting-go-back').addEventListener('click', goBackToPhase);
        $('results-go-back').addEventListener('click', goBackToPhase);

        function renderSubmissionProgress(submittedCount, totalParticipants) {
            $('submission-host-count').textContent =
                submittedCount + ' of ' + totalParticipants + ' have submitted something';
        }

        function enterSubmissionPhase() {
            showPhase('submission');
            $('submission-host-actions').classList.toggle(HIDDEN, !isHost);
            $('submission-host-count').classList.toggle(HIDDEN, !isHost);
            updateSubmitEnabled();
        }

        // ------------------------------------------------------------
        // Voting phase
        // ------------------------------------------------------------

        const SWIPE_THRESHOLD = 100;
        const SWIPE_MAX_ROTATION = 18;
        let swipeVoting = false;

        const RESULTS_END_IMAGES = [
            'https://static0.srcdn.com/wordpress/wp-content/uploads/2019/03/Brian-Griffin-in-Family-GUy-3.jpg',
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSDMR6yiAS6UVo79PUZMoLS0S83qkhVYNcLfJOXL7rYu3bKO5xJCY_TwwY&s=10',
            'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1RvgJtjgxOQ6rQH4qa8vPhCVjtD2JipHqYOQFEClSctxCGvp_FP3-EfE&s=10',
        ];

        function buildSwipeCard(content, stackLevel) {
            const card = document.createElement('div');
            card.className = 'site-wish-it-want-it-do-it__swipe-card site-wish-it-want-it-do-it__swipe-card--fresh';
            if (stackLevel === 0) {
                card.classList.add('site-wish-it-want-it-do-it__swipe-card--top');
            } else {
                card.classList.add('site-wish-it-want-it-do-it__swipe-card--stack-' + stackLevel);
            }
            if (isImageContent(content)) {
                card.classList.add('site-wish-it-want-it-do-it__swipe-card--image');
                const img = document.createElement('img');
                img.src = content;
                img.alt = 'Submitted image';
                img.draggable = false;
                card.appendChild(img);
            } else {
                card.textContent = content;
            }
            return card;
        }

        function releaseFreshCard(card) {
            void card.getBoundingClientRect();
            card.classList.remove('site-wish-it-want-it-do-it__swipe-card--fresh');
        }

        function renderCardStack(deck, contents, attachTopSwipe) {
            const freshCards = [];
            for (let i = contents.length - 1; i >= 0; i--) {
                const card = buildSwipeCard(contents[i], i);
                deck.appendChild(card);
                freshCards.push(card);
                if (i === 0) attachTopSwipe(card);
            }
            freshCards.forEach(releaseFreshCard);
        }

        const SWIPE_FLY_DURATION = 220;

        function wait(ms) {
            return new Promise((resolve) => setTimeout(resolve, ms));
        }

        function attachSwipeGesture(card, deck, options) {
            const hintAi = options.hintAi || null;
            const hintHuman = options.hintHuman || null;
            let startX = 0;
            let rawDx = 0;
            let dx = 0;
            let dragging = false;
            let locked = false;
            let capturedPointerId = null;

            let restLeft = 0;
            let restRight = 0;

            function onPointerDown(event) {
                if (locked || (options.isLocked && options.isLocked())) return;
                dragging = true;
                startX = event.clientX;
                const restRect = card.getBoundingClientRect();
                restLeft = restRect.left;
                restRight = restRect.right;
                card.classList.add('site-wish-it-want-it-do-it__swipe-card--dragging');
                try {
                    card.setPointerCapture(event.pointerId);
                    capturedPointerId = event.pointerId;
                } catch {
                    capturedPointerId = null;
                }
            }

            function onPointerMove(event) {
                if (!dragging) return;
                const viewportWidth = document.documentElement.clientWidth;
                const maxDragLeft = restLeft;
                const maxDragRight = viewportWidth - restRight;
                rawDx = event.clientX - startX;
                dx = Math.max(-maxDragLeft, Math.min(maxDragRight, rawDx));
                const rotation = Math.max(-1, Math.min(1, dx / 300)) * SWIPE_MAX_ROTATION;
                card.style.transform = 'translateX(' + dx + 'px) rotate(' + rotation + 'deg)';
                const pull = Math.min(Math.abs(rawDx) / SWIPE_THRESHOLD, 1);
                if (hintAi) hintAi.style.opacity = rawDx < 0 ? String(pull) : '0';
                if (hintHuman) hintHuman.style.opacity = rawDx > 0 ? String(pull) : '0';
            }

            function releasePointer() {
                if (capturedPointerId === null) return;
                try {
                    card.releasePointerCapture(capturedPointerId);
                } catch {
                    /* the pointer is already gone */
                }
                capturedPointerId = null;
            }

            function onPointerUp() {
                if (!dragging) return;
                dragging = false;
                releasePointer();
                card.classList.remove('site-wish-it-want-it-do-it__swipe-card--dragging');
                if (hintAi) hintAi.style.opacity = '0';
                if (hintHuman) hintHuman.style.opacity = '0';
                if (Math.abs(rawDx) >= SWIPE_THRESHOLD) {
                    const direction = rawDx > 0 ? 'right' : 'left';
                    const flyClass = rawDx > 0 ? 'site-wish-it-want-it-do-it__swipe-card--fly-right' : 'site-wish-it-want-it-do-it__swipe-card--fly-left';
                    card.classList.add(flyClass);
                    card.style.transform = '';
                    const consumed = options.onSwipe(direction, card);
                    if (consumed === false) {
                        card.classList.remove(flyClass);
                    } else {
                        locked = true;
                    }
                } else {
                    card.style.transform = '';
                }
                rawDx = 0;
                dx = 0;
            }

            card.addEventListener('pointerdown', onPointerDown);
            card.addEventListener('pointermove', onPointerMove);
            card.addEventListener('pointerup', onPointerUp);
            card.addEventListener('pointercancel', onPointerUp);
        }

        async function castVoteAndAdvance(verdict, card) {
            if (swipeVoting) return;
            swipeVoting = true;
            clearNotice($('voting-error'));
            try {
                const [next] = await Promise.all([
                    api('/rooms/' + roomCode + '/vote', {
                        method: 'POST',
                        body: JSON.stringify({
                            sessionToken,
                            verdict
                        }),
                    }),
                    wait(SWIPE_FLY_DURATION),
                ]);
                renderVotingItem(next);
            } catch (err) {
                if (err instanceof ApiError && err.status === 409) {
                    await resyncState();
                } else {
                    reportError($('voting-error'), err);
                    card.classList.remove('site-wish-it-want-it-do-it__swipe-card--fly-left', 'site-wish-it-want-it-do-it__swipe-card--fly-right');
                }
            } finally {
                swipeVoting = false;
            }
        }

        function attachVotingSwipe(card) {
            const deck = $('voting-deck');
            const hintAi = deck.querySelector('.site-wish-it-want-it-do-it__swipe-hint--ai');
            const hintHuman = deck.querySelector('.site-wish-it-want-it-do-it__swipe-hint--human');
            attachSwipeGesture(card, deck, {
                hintAi,
                hintHuman,
                isLocked: () => swipeVoting,
                onSwipe: (direction) => {
                    const verdict = direction === 'right' ? 'human' : 'ai';
                    castVoteAndAdvance(verdict, card);
                },
            });
        }

        function voteFromButton(verdict) {
            if (swipeVoting) return;
            const deck = $('voting-deck');
            const card = deck.querySelector('.site-wish-it-want-it-do-it__swipe-card--top') || deck.querySelector('.site-wish-it-want-it-do-it__swipe-card');
            if (!card) return;
            const flyClass = verdict === 'human' ? 'site-wish-it-want-it-do-it__swipe-card--fly-right' : 'site-wish-it-want-it-do-it__swipe-card--fly-left';
            card.classList.add(flyClass);
            castVoteAndAdvance(verdict, card);
        }

        $('voting-vote-ai').addEventListener('click', () => voteFromButton('ai'));
        $('voting-vote-human').addEventListener('click', () => voteFromButton('human'));

        $('voting-show-results').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            if (!window.confirm('Show the results now, using the votes gathered so far?')) return;
            try {
                await api('/rooms/' + roomCode + '/force-start-results', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken
                    }),
                });
                await resyncState();
                setStatus('');
            } catch (err) {
                setStatus(err.message, 'error');
            }
        }));

        function renderVotingProgress(votedThroughCount, totalParticipants) {
            const el = $('voting-progress');
            if (!el) return;
            el.classList.toggle(HIDDEN, !isHost);
            el.textContent = votedThroughCount + ' of ' + totalParticipants + ' have submitted their votes';
        }

        function renderVotingItem(data) {
            $('voting-host-actions').classList.toggle(HIDDEN, !isHost);
            if (data.done) {
                $('voting-active').classList.add(HIDDEN);
                $('voting-waiting').classList.remove(HIDDEN);
                return;
            }
            $('voting-active').classList.remove(HIDDEN);
            $('voting-waiting').classList.add(HIDDEN);
            clearNotice($('voting-error'));

            const deck = $('voting-deck');
            deck.querySelectorAll('.site-wish-it-want-it-do-it__swipe-card').forEach((card) => card.remove());
            const stack = [data.content, ...(data.upcoming || [])];
            renderCardStack(deck, stack, attachVotingSwipe);
        }

        // ------------------------------------------------------------
        // Results
        // ------------------------------------------------------------

        async function loadResults() {
            $('results-host-actions').classList.toggle(HIDDEN, !isHost);
            try {
                const result = await api('/rooms/' + roomCode + '/results', {
                    headers: {
                        'x-session-token': sessionToken
                    },
                });
                resultsItems = result.items;
                resultsIndex = 0;
                resultsDismissed = false;
                renderResultsItem();
            } catch (err) {
                setStatus(err.message, 'error');
            }
        }

        function attachResultsSwipe(card) {
            const deck = $('results-deck');
            attachSwipeGesture(card, deck, {
                onSwipe: (direction) => {
                    if (direction === 'left') {
                        if (resultsIndex === 0) return false;
                        resultsIndex -= 1;
                        renderResultsItem();
                        return true;
                    }
                    if (resultsIndex >= resultsItems.length - 1) {
                        resultsDismissed = true;
                        renderResultsItem();
                        return true;
                    }
                    resultsIndex += 1;
                    renderResultsItem();
                    return true;
                },
            });
        }

        function renderResultsItem() {
            const deck = $('results-deck');
            deck.querySelectorAll('.site-wish-it-want-it-do-it__swipe-card').forEach((card) => card.remove());
            deck.querySelectorAll('.site-wish-it-want-it-do-it__results-end-image').forEach((img) => img.remove());
            if (!resultsItems.length) {
                $('results-tally').classList.add(HIDDEN);
                deck.appendChild(buildSwipeCard('No submissions.', 0));
                return;
            }
            if (resultsDismissed) {
                $('results-tally').classList.add(HIDDEN);
                const img = document.createElement('img');
                img.src = RESULTS_END_IMAGES[Math.floor(Math.random() * RESULTS_END_IMAGES.length)];
                img.alt = "That's everyone -- tap to see results again.";
                img.className = 'site-wish-it-want-it-do-it__results-end-image';
                img.addEventListener('click', () => {
                    resultsDismissed = false;
                    resultsIndex = resultsItems.length - 1;
                    renderResultsItem();
                });
                deck.appendChild(img);
                return;
            }
            $('results-tally').classList.remove(HIDDEN);
            const item = resultsItems[resultsIndex];
            const total = item.aiVotes + item.humanVotes;
            const aiPercent = total ? (item.aiVotes / total) * 100 : 50;
            const humanPercent = total ? 100 - aiPercent : 50;
            $('results-tally-bar-ai').style.flexGrow = String(aiPercent);
            $('results-tally-bar-human').style.flexGrow = String(humanPercent);
            $('results-tally-ai-count').textContent = String(item.aiVotes);
            $('results-tally-human-count').textContent = String(item.humanVotes);

            const stack = resultsItems.slice(resultsIndex, resultsIndex + 3).map((i) => i.content);
            renderCardStack(deck, stack, attachResultsSwipe);
        }

        // ------------------------------------------------------------
        // Realtime
        // ------------------------------------------------------------

        const MAX_RECONNECT_ATTEMPTS = 6;

        async function attemptReconnect() {
            if (!roomCode || !sessionToken) return;
            if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                setStatus('Disconnected. Refresh the page to rejoin.', 'error');
                return;
            }
            reconnectAttempts += 1;
            const delayMs = Math.min(1500 * (2 ** (reconnectAttempts - 1)), 20000);
            setStatus('Connection lost. Retrying in ' + Math.ceil(delayMs / 1000) + 's...', 'warning');
            await wait(delayMs);
            if (!roomCode) return;
            await teardownConnection();
            try {
                await connectRealtime();
                await resyncState();
                reconnectAttempts = 0;
                setStatus('');
            } catch {
                await teardownConnection();
                await attemptReconnect();
            }
        }

        async function joinSignalRGroups() {
            await api('/rooms/' + roomCode + '/join-groups', {
                method: 'POST',
                body: JSON.stringify({
                    sessionToken,
                    participantId
                }),
            });
        }

        async function connectRealtime() {
            if (connection) return;
            await ensureSignalRLoaded();
            if (!window.signalR) {
                setStatus('Live updates could not load. Refresh and try again.', 'error');
                return;
            }
            const negotiateInfo = await api('/negotiate', {
                method: 'POST',
                headers: {
                    'x-participant-id': participantId
                },
                body: JSON.stringify({
                    roomCode,
                    participantId
                }),
            }).catch(() => null);
            if (!negotiateInfo) {
                setStatus('Could not connect to live updates. Refresh to retry.', 'error');
                return;
            }
            connection = new window.signalR.HubConnectionBuilder()
                .withUrl(negotiateInfo.url, {
                    accessTokenFactory: () => negotiateInfo.accessToken
                })
                .withAutomaticReconnect()
                .build();

            connection.on('PresenceUpdated', (data) => {
                joinOpen = data.joinOpen !== false;
                renderParticipants(data.participants, data.expectedHeadcount);
            });
            connection.on('PhaseChanged', () => {
                resyncState();
            });
            connection.on('SubmissionProgress', (data) => {
                if (!isHost) return;
                renderSubmissionProgress(data.submittedCount, data.totalParticipants);
            });
            connection.on('VotingProgress', (data) => {
                if (!isHost) return;
                renderVotingProgress(data.votedThroughCount, data.totalParticipants);
            });
            connection.on('RoomStopped', () => {
                leaveToChoice('The host ended the session.', 'warning');
            });

            connection.onreconnecting(() => setStatus('Reconnecting...', 'warning'));
            connection.onreconnected(async () => {
                try {
                    await joinSignalRGroups();
                    setStatus('');
                    await resyncState();
                } catch (err) {
                    setStatus(err.message, 'error');
                }
            });
            connection.onclose(() => {
                attemptReconnect();
            });
            await connection.start();
            await joinSignalRGroups();
        }

        async function resyncState() {
            if (!roomCode || !sessionToken) return;
            let state;
            try {
                state = await api('/rooms/' + roomCode + '/state', {
                    headers: {
                        'x-session-token': sessionToken
                    },
                });
            } catch (err) {
                if (err instanceof ApiError && (err.status === 404 || err.status === 401)) {
                    leaveToChoice('That session has ended. Join or host a new room.', 'warning');
                    return;
                }
                setStatus(err.message, 'error');
                return;
            }

            isHost = state.isHost;
            joinOpen = state.joinOpen !== false;
            if (state.displayName) myDisplayName = state.displayName;
            saveSession();
            renderParticipants(state.participants, state.expectedHeadcount);

            if (state.phase === 'lobby') {
                showPhase('lobby');
            } else if (state.phase === 'submission') {
                enterSubmissionPhase();
                renderSubmissionProgress(state.submittedCount, state.totalParticipants);
                if (!mySubmissionsHydrated) {
                    mySubmissionsHydrated = true;
                    mySubmissions = state.mySubmissions || [];
                    mySubmissionCursor = mySubmissions.length ? mySubmissions.length - 1 : 0;
                    loadSubmissionAtCursor();
                }
            } else if (state.phase === 'voting') {
                showPhase('voting');
                renderVotingProgress(state.votedThroughCount, state.totalParticipants);
                try {
                    const item = await api('/rooms/' + roomCode + '/voting-item', {
                        headers: {
                            'x-session-token': sessionToken
                        },
                    });
                    renderVotingItem(item);
                } catch (err) {
                    reportError($('voting-error'), err);
                }
            } else if (state.phase === 'results') {
                showPhase('results');
                await loadResults();
            }
        }

        (async function resumeIfPossible() {
            let saved = null;
            try {
                saved = sessionStorage.getItem(STORAGE_KEY);
            } catch {
                /* storage is unavailable -- start fresh */
            }
            if (!saved) {
                showPhase('choice');
                return;
            }
            let parsed;
            try {
                parsed = JSON.parse(saved);
            } catch {
                leaveToChoice('');
                return;
            }
            if (!parsed || !parsed.roomCode || !parsed.sessionToken) {
                leaveToChoice('');
                return;
            }
            roomCode = parsed.roomCode;
            participantId = parsed.participantId;
            sessionToken = parsed.sessionToken;
            isHost = Boolean(parsed.isHost);
            myDisplayName = parsed.myDisplayName || null;
            showPhase('lobby');
            try {
                await connectRealtime();
            } catch {
                setStatus('Live updates are unavailable. The page will still work, but may lag behind.', 'warning');
            }
            await resyncState();
        })();
    }

    function bootWishItWantItDoIt() {
        document.querySelectorAll('.site-wish-it-want-it-do-it[data-wish-it-want-it-do-it="true"]').forEach(initWishItWantItDoIt);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootWishItWantItDoIt, {
            once: true
        });
    } else {
        bootWishItWantItDoIt();
    }
})();
