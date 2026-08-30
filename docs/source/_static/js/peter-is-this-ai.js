/*
Peter, Is this AI?  widget behaviour
=====================================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 12 August, 2026
Last updated on: 29 August, 2026
*/

// Note. This file is entirely vibe-coded using Claude Code.

(function () {
    const SIGNALR_CLIENT_CDN_URL = 'https://cdn.jsdelivr.net/npm/@microsoft/signalr@8.0.7/dist/browser/signalr.min.js';

    const HOST_CHARACTER = 'God';

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
        'Adam': 'https://i.imgur.com/72NLPni.png',
        'Babs': 'https://i.imgur.com/72NLPni.png',
        'Bonnie': 'https://i.imgur.com/72NLPni.png',
        'Brian': 'https://i.imgur.com/UQTRSMN.png',
        'Bruce': 'https://i.imgur.com/p9n83Dy.png',
        'Carter': 'https://i.imgur.com/oVk6Uqg.png',
        'Chris': 'https://i.imgur.com/oVk6Uqg.png',
        'Cleveland': 'https://i.imgur.com/Jj8L6aL.png',
        'Consuela': 'https://i.imgur.com/Rs42UQn.png',
        'God': 'https://i.imgur.com/qmi1utl.png',
        'Hartman': 'https://i.imgur.com/zYmKDIc.png',
        'Herbert': 'https://i.imgur.com/jVNORMF.png',
        'Joe': 'https://i.imgur.com/XNnNPMK.png',
        'Lois': 'https://i.imgur.com/ebwwb1u.png',
        'Meg': 'https://i.imgur.com/Y2yCFnQ.png',
        'Mort': 'https://i.imgur.com/Y2yCFnQ.png',
        'Peter': 'https://i.imgur.com/iUDCTZR.png',
        'Quagmire': 'https://i.imgur.com/BZXVyFv.png',
        'Stewie': 'https://i.imgur.com/ngyn7Es.png',
        'Tom': 'https://i.imgur.com/ngyn7Es.png',
    };
    const CHARACTER_AVATAR_LIST = Object.values(CHARACTER_AVATARS);

    function avatarImageFor(displayName) {
        if (CHARACTER_AVATARS[displayName]) return CHARACTER_AVATARS[displayName];
        let hash = 0;
        for (let i = 0; i < displayName.length; i++) {
            hash = (hash * 31 + displayName.charCodeAt(i)) >>> 0;
        }
        return CHARACTER_AVATAR_LIST[hash % CHARACTER_AVATAR_LIST.length];
    }

    function ensureSignalRLoaded() {
        if (window.signalR) return Promise.resolve();
        if (window.__isThisAISignalRPromise) return window.__isThisAISignalRPromise;
        window.__isThisAISignalRPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = SIGNALR_CLIENT_CDN_URL;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load SignalR client.'));
            document.head.appendChild(script);
        });
        return window.__isThisAISignalRPromise;
    }

    function createMockBackend() {
        const CHARACTERS = [
            'Adam',
            'Babs',
            'Bonnie',
            'Brian',
            'Bruce',
            'Carter',
            'Chris',
            'Cleveland',
            'Consuela',
            'God',
            'Hartman',
            'Herbert',
            'Joe',
            'Lois',
            'Meg',
            'Mort',
            'Peter',
            'Quagmire',
            'Stewie',
            'Tom',
        ];
        const ROOMS_STORAGE_KEY = 'peter-is-this-ai-mock-rooms';
        const DEFAULT_ROOM_CODE = 'ABCDE';
        let listeners = {};

        function shuffledCharacters() {
            const pool = CHARACTERS.filter((c) => c !== HOST_CHARACTER);
            for (let i = pool.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [pool[i], pool[j]] = [pool[j], pool[i]];
            }
            return pool;
        }

        function loadRooms() {
            try {
                return JSON.parse(localStorage.getItem(ROOMS_STORAGE_KEY)) || {};
            } catch {
                return {};
            }
        }

        function saveRooms(rooms) {
            localStorage.setItem(ROOMS_STORAGE_KEY, JSON.stringify(rooms));
        }

        let pendingEmits = null;

        function withRoom(roomCode, fn) {
            const rooms = loadRooms();
            pendingEmits = [];
            let result;
            try {
                result = fn(rooms, rooms[roomCode]);
            } finally {
                const queued = pendingEmits;
                pendingEmits = null;
                saveRooms(rooms);
                queued.forEach(([event, args]) => {
                    (listeners[event] || []).forEach((cb) => cb(...args));
                });
            }
            return result;
        }

        function emit(event, ...args) {
            if (pendingEmits) {
                pendingEmits.push([event, args]);
            } else {
                (listeners[event] || []).forEach((cb) => cb(...args));
            }
        }

        function randomRoomCode() {
            return DEFAULT_ROOM_CODE;
        }

        function randomToken() {
            return Math.random().toString(36).slice(2) + Math.random().toString(36).slice(2);
        }

        function publicParticipant(p) {
            return {
                participantId: p.participantId,
                displayName: p.displayName,
                isHost: p.isHost,
            };
        }

        function broadcastPresence(room) {
            emit('PresenceUpdated', {
                participants: room.participants.map(publicParticipant),
                joinedCount: room.participants.length,
                expectedHeadcount: room.expectedHeadcount,
            });
        }

        function maybeAdvanceToSubmission(room) {
            if (room.participants.length < room.expectedHeadcount || room.phase !== 'lobby' || room.autoStartAt) return;
            const delaySeconds = room.autoStartDelaySeconds || 0;
            if (delaySeconds <= 0) {
                startSubmissionPhase(room);
            } else {
                room.autoStartAt = Date.now() + delaySeconds * 1000;
                emit('AutoStartScheduled', {
                    delaySeconds
                });
            }
        }

        function startSubmissionPhase(room) {
            room.phase = 'submission';
            emit('PhaseChanged', {
                phase: 'submission'
            });
        }

        function mySubmissionsFor(room, participantId) {
            return Object.values(room.submissions)
                .filter((s) => s.participantId === participantId)
                .sort((a, b) => a.createdAt - b.createdAt);
        }

        function submitContentFor(room, participantId, content, submissionId) {
            if (submissionId) {
                const existing = room.submissions[submissionId];
                if (!existing || existing.participantId !== participantId) {
                    throw new Error('Submission not found.');
                }
                existing.content = content;
            } else {
                submissionId = 'sub-' + randomToken();
                room.submissions[submissionId] = {
                    submissionId,
                    participantId,
                    content,
                    createdAt: Date.now(),
                };
            }
            const submittedParticipants = new Set(Object.values(room.submissions).map((s) => s.participantId)).size;
            emit('SubmissionArrived', {
                submittedCount: submittedParticipants,
                totalParticipants: room.participants.length,
                skippedCount: room.skippedCount || 0,
            });
            return submissionId;
        }

        function startVotingPhase(room) {
            const submissionIds = Object.keys(room.submissions);
            room.participants.forEach((p) => {
                const order = submissionIds.filter((id) => room.submissions[id].participantId !== p.participantId);
                for (let i = order.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [order[i], order[j]] = [order[j], order[i]];
                }
                room.votingOrder[p.participantId] = order;
                room.votingIndex[p.participantId] = 0;
            });
            // Nobody ever casts a vote to trigger the usual completion
            // check when every submitter's queue is already empty (e.g.
            // a single submitter with nobody else to vote on) -- without
            // this, the room would sit in `voting` forever.
            if (allDoneVoting(room)) {
                room.phase = 'results';
                emit('PhaseChanged', {
                    phase: 'results'
                });
                emit('ResultsReady', {
                    roomCode: room.roomCode
                });
                return;
            }
            room.phase = 'voting';
            emit('PhaseChanged', {
                phase: 'voting'
            });
        }

        function votingItemPayload(room, participantId) {
            const order = room.votingOrder[participantId] || [];
            const index = room.votingIndex[participantId] || 0;
            if (index >= order.length) {
                return {
                    itemIndex: index,
                    totalItems: order.length,
                    content: null,
                    upcoming: [],
                    done: true
                };
            }
            const upcoming = order
                .slice(index + 1, index + 3)
                .map((id) => room.submissions[id].content);
            return {
                itemIndex: index,
                totalItems: order.length,
                content: room.submissions[order[index]].content,
                upcoming,
                done: false,
            };
        }

        function allDoneVoting(room) {
            const submitterIds = new Set(Object.values(room.submissions).map((s) => s.participantId));
            return room.participants
                .filter((p) => submitterIds.has(p.participantId))
                .every((p) => (room.votingIndex[p.participantId] || 0) >= (room.votingOrder[p.participantId] || []).length);
        }

        function castVoteFor(room, voterParticipantId, verdict) {
            const order = room.votingOrder[voterParticipantId] || [];
            const index = room.votingIndex[voterParticipantId] || 0;
            if (index >= order.length) return votingItemPayload(room, voterParticipantId);
            const submissionId = order[index];
            room.votes[submissionId] = room.votes[submissionId] || [];
            const voter = room.participants.find((p) => p.participantId === voterParticipantId);
            room.votes[submissionId].push({
                voterDisplayName: voter ? voter.displayName : 'Unknown',
                verdict
            });
            room.votingIndex[voterParticipantId] = index + 1;
            emit('VoteTallyUpdated', {
                votedCount: room.votes[submissionId].length,
                totalParticipants: room.participants.length,
            });
            if (allDoneVoting(room)) {
                room.phase = 'results';
                emit('PhaseChanged', {
                    phase: 'results'
                });
                emit('ResultsReady', {
                    roomCode: room.roomCode
                });
            }
            return votingItemPayload(room, voterParticipantId);
        }

        function stopRoom(rooms, room) {
            delete rooms[room.roomCode];
            emit('RoomStopped', {});
            emit('RoomRestarted', {});
        }

        const api = {
            async login(body) {
                if (body.username === 'demo' && body.password === 'demo') {
                    return {
                        ok: true,
                        hostToken: randomToken()
                    };
                }
                const err = new Error('Invalid credentials.');
                throw err;
            },

            async createRoom(body) {
                const roomCode = randomRoomCode();
                const hostParticipantId = 'host-' + randomToken();
                withRoom(roomCode, (rooms) => {
                    rooms[roomCode] = {
                        roomCode,
                        expectedHeadcount: body.expectedHeadcount,
                        autoStartDelaySeconds: Math.max(0, Number(body.autoStartDelaySeconds) || 0),
                        characterPool: shuffledCharacters(),
                        phase: 'lobby',
                        participants: [{
                            participantId: hostParticipantId,
                            displayName: HOST_CHARACTER,
                            isHost: true
                        }],
                        submissions: {},
                        votingOrder: {},
                        votingIndex: {},
                        votes: {},
                    };
                    maybeAdvanceToSubmission(rooms[roomCode]);
                });
                return {
                    roomCode,
                    participantId: hostParticipantId,
                    sessionToken: 'session-' + hostParticipantId,
                    isHost: true,
                };
            },

            async joinRoom(roomCode, body) {
                const participantId = 'guest-' + randomToken();
                let displayName = (body.displayName || '').trim();
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase !== 'lobby') throw new Error('This room has already started.');
                    if (room.participants.length >= room.expectedHeadcount) throw new Error('This room is full.');
                    if (!displayName) {
                        const pool = room.characterPool || CHARACTERS;
                        displayName = pool[room.participants.length % pool.length];
                    }
                    room.participants.push({
                        participantId,
                        displayName,
                        isHost: false
                    });
                    broadcastPresence(room);
                    maybeAdvanceToSubmission(room);
                });
                return {
                    participantId,
                    sessionToken: 'session-' + participantId,
                    displayName,
                    isHost: false,
                };
            },

            async getState(roomCode, participantId) {
                let room = loadRooms()[roomCode];
                if (!room) throw new Error('Room not found.');
                if (room.phase === 'lobby' && room.autoStartAt && Date.now() >= room.autoStartAt) {
                    withRoom(roomCode, (rooms, r) => {
                        if (r && r.phase === 'lobby' && r.autoStartAt && Date.now() >= r.autoStartAt) {
                            startSubmissionPhase(r);
                        }
                    });
                    room = loadRooms()[roomCode];
                }
                const participant = room.participants.find((p) => p.participantId === participantId);
                if (!participant) throw new Error('Invalid session.');
                const submittedParticipants = new Set(Object.values(room.submissions).map((s) => s.participantId)).size;
                return {
                    phase: room.phase,
                    participants: room.participants.map(publicParticipant),
                    expectedHeadcount: room.expectedHeadcount,
                    isHost: participant.isHost,
                    participantId,
                    submittedCount: submittedParticipants,
                    skippedCount: room.skippedCount || 0,
                    autoStartAt: room.autoStartAt || null,
                    mySubmissions: mySubmissionsFor(room, participantId).map((s) => ({
                        submissionId: s.submissionId,
                        content: s.content,
                    })),
                };
            },

            async forceStartSubmission(roomCode) {
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase !== 'lobby') throw new Error('Room is not in the lobby phase.');
                    room.skippedCount = Math.max(0, room.expectedHeadcount - room.participants.length);
                    broadcastPresence(room);
                    startSubmissionPhase(room);
                });
                return {
                    ok: true
                };
            },

            async submitContent(roomCode, participantId, content, submissionId) {
                if (isImageContent(content) && content.length > MAX_IMAGE_DATA_URI_LENGTH) {
                    throw new Error('Image is too large. Try a smaller photo.');
                }
                let savedId;
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase !== 'submission') throw new Error('Room is not accepting submissions.');
                    savedId = submitContentFor(room, participantId, content, submissionId);
                });
                return {
                    ok: true,
                    submissionId: savedId,
                };
            },

            async forceStartVoting(roomCode) {
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase !== 'submission') throw new Error('Room is not in the submission phase.');
                    if (!Object.keys(room.submissions).length) throw new Error('No submissions to vote on yet.');
                    startVotingPhase(room);
                });
                return {
                    ok: true
                };
            },

            async goBack(roomCode) {
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase === 'submission') {
                        room.phase = 'lobby';
                        room.autoStartAt = null;
                        emit('PhaseChanged', {
                            phase: 'lobby'
                        });
                    } else if (room.phase === 'voting') {
                        room.phase = 'submission';
                        emit('PhaseChanged', {
                            phase: 'submission'
                        });
                    } else {
                        throw new Error('Cannot go back from this phase.');
                    }
                });
                return {
                    ok: true
                };
            },

            async getVotingItem(roomCode, participantId) {
                const room = loadRooms()[roomCode];
                if (!room) throw new Error('Room not found.');
                if (room.phase !== 'voting') throw new Error('Room is not in the voting phase.');
                return votingItemPayload(room, participantId);
            },

            async castVote(roomCode, participantId, verdict) {
                let payload;
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    if (room.phase !== 'voting') throw new Error('Room is not in the voting phase.');
                    payload = castVoteFor(room, participantId, verdict);
                });
                return payload;
            },

            async getResults(roomCode) {
                const room = loadRooms()[roomCode];
                if (!room) throw new Error('Room not found.');
                if (room.phase !== 'results') throw new Error('Results are not ready yet.');
                const items = Object.keys(room.submissions).map((submissionId) => {
                    const votes = room.votes[submissionId] || [];
                    return {
                        content: room.submissions[submissionId].content,
                        aiVotes: votes.filter((v) => v.verdict === 'ai').length,
                        humanVotes: votes.filter((v) => v.verdict === 'human').length,
                        votes,
                    };
                });
                return {
                    items
                };
            },

            async stop(roomCode) {
                withRoom(roomCode, (rooms, room) => {
                    if (!room) throw new Error('Room not found.');
                    stopRoom(rooms, room);
                });
                return {
                    ok: true
                };
            },
        };

        function fakeConnection() {
            let onExternalChange = null;
            function handleStorage(event) {
                if (event.key !== ROOMS_STORAGE_KEY || !onExternalChange) return;
                let rooms = {};
                try {
                    rooms = JSON.parse(event.newValue) || {};
                } catch {
                    rooms = {};
                }
                onExternalChange(rooms);
            }
            return {
                on(event, cb) {
                    listeners[event] = listeners[event] || [];
                    listeners[event].push(cb);
                },
                onreconnecting() { },
                onreconnected() { },
                onclose() { },
                onExternalChange(cb) {
                    onExternalChange = cb;
                },
                async start() {
                    window.addEventListener('storage', handleStorage);
                },
                async stop() {
                    window.removeEventListener('storage', handleStorage);
                },
            };
        }

        return {
            api,
            fakeConnection
        };
    }

    function initIsThisAI(root) {
        const UID = root.id;
        const IS_LOCALHOST = ['localhost', '127.0.0.1', '::1', '0.0.0.0'].includes(window.location.hostname);
        const LOCAL_DEV = root.dataset.localDev === 'true' || IS_LOCALHOST;
        const USE_MOCK_BACKEND = LOCAL_DEV && root.dataset.localDevRealBackend !== 'true';
        const API_BASE = LOCAL_DEV
            ? (root.dataset.localApiBaseUrl || 'http://localhost:7071/api')
            : (root.dataset.apiBaseUrl || '');
        const HEADCOUNT_MAX = Number(root.dataset.headcountMax || 20);
        const AUTO_START_DELAY_SECONDS = (() => {
            const parsed = Number(root.dataset.autoStartDelaySeconds);
            return Number.isFinite(parsed) && parsed >= 0 ? parsed : 5;
        })();
        const STORAGE_KEY = 'peter-is-this-ai-session-' + UID;
        const CREATED_HERE_KEY = 'peter-is-this-ai-created-here-' + UID;
        const $ = (id) => document.getElementById(UID + '-' + id);
        const mock = USE_MOCK_BACKEND ? createMockBackend() : null;

        let hostToken = null;
        let roomCode = null;
        let participantId = null;
        let sessionToken = null;
        let isHost = false;
        let myDisplayName = null;
        let connection = null;
        let reconnectAttempts = 0;
        let resultsItems = [];
        let resultsIndex = 0;
        let resultsDismissed = false;
        let mySubmissions = [];
        let mySubmissionCursor = 0;
        let mySubmissionsHydrated = false;
        let autoStartAt = null;
        let autoStartCountdownInterval = null;
        let autoStartCheckTimeout = null;

        if ($('choice-headcount')) $('choice-headcount').max = String(HEADCOUNT_MAX);

        function showPhase(phase) {
            ['choice', 'lobby', 'submission', 'voting', 'results'].forEach((p) => {
                const el = $('phase-' + p);
                if (el) el.classList.toggle('site-peter-is-this-ai--hidden', p !== phase);
            });
            if (phase !== 'lobby') clearAutoStartCountdown();
        }

        function clearAutoStartCountdown() {
            autoStartAt = null;
            if (autoStartCountdownInterval) {
                clearInterval(autoStartCountdownInterval);
                autoStartCountdownInterval = null;
            }
            if (autoStartCheckTimeout) {
                clearTimeout(autoStartCheckTimeout);
                autoStartCheckTimeout = null;
            }
            const el = $('lobby-countdown');
            if (el) el.textContent = '';
        }

        function tickAutoStartCountdown() {
            const el = $('lobby-countdown');
            if (!el || !autoStartAt) return;
            const remainingMs = autoStartAt - Date.now();
            if (remainingMs <= 0) {
                el.textContent = 'Starting...';
                return;
            }
            const seconds = Math.ceil(remainingMs / 1000);
            el.textContent = 'Starting in ' + seconds + (seconds === 1 ? ' second...' : ' seconds...');
        }

        function scheduleAutoStart(targetAt) {
            clearAutoStartCountdown();
            autoStartAt = targetAt;
            tickAutoStartCountdown();
            autoStartCountdownInterval = setInterval(tickAutoStartCountdown, 250);
            const remainingMs = Math.max(0, targetAt - Date.now());
            autoStartCheckTimeout = setTimeout(() => {
                resyncState();
            }, remainingMs + 300);
        }

        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && autoStartAt && Date.now() >= autoStartAt) {
                resyncState();
            }
        });

        function setStatus(message) {
            const el = $('connection-status');
            if (el) el.textContent = message || '';
        }

        function resetHostChoiceFields() {
            $('host-login-fields').classList.remove('site-peter-is-this-ai--hidden');
            $('host-create-fields').classList.add('site-peter-is-this-ai--hidden');
            $('login-error').textContent = '';
            $('choice-host-error').textContent = '';
        }

        function saveSession() {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                roomCode,
                participantId,
                sessionToken,
                isHost,
                myDisplayName,
            }));
        }

        function clearSession() {
            localStorage.removeItem(STORAGE_KEY);
            sessionStorage.removeItem(CREATED_HERE_KEY);
            roomCode = participantId = sessionToken = myDisplayName = null;
            isHost = false;
            mySubmissions = [];
            mySubmissionCursor = 0;
            mySubmissionsHydrated = false;
            composerImages = [];
            resetHostChoiceFields();
        }

        async function mockApi(path, options) {
            options = options || {};
            const body = options.body ? JSON.parse(options.body) : {};
            const roomMatch = path.match(/^\/rooms\/([^/]+)(\/.*)?$/);
            const code = roomMatch ? roomMatch[1] : null;
            const sub = roomMatch ? (roomMatch[2] || '') : null;

            if (path === '/login') return mock.api.login(body);
            if (path === '/rooms' && (options.method || 'GET') === 'POST') return mock.api.createRoom(body);
            if (code && sub === '/join') return mock.api.joinRoom(code, body);
            if (code && sub === '/state') return mock.api.getState(code, participantId);
            if (code && sub === '/force-start-submission') return mock.api.forceStartSubmission(code);
            if (code && sub === '/submit') return mock.api.submitContent(code, participantId, body.content, body.submissionId);
            if (code && sub === '/force-start-voting') return mock.api.forceStartVoting(code);
            if (code && sub === '/go-back') return mock.api.goBack(code);
            if (code && sub === '/voting-item') return mock.api.getVotingItem(code, participantId);
            if (code && sub === '/vote') return mock.api.castVote(code, participantId, body.verdict);
            if (code && sub === '/results') return mock.api.getResults(code);
            if (code && sub === '/stop') return mock.api.stop(code);
            if (code && sub === '/restart') return mock.api.stop(code);
            if (code && sub === '/join-groups') return {
                ok: true
            };
            if (path === '/negotiate') return {
                url: 'mock://local-dev',
                accessToken: 'mock'
            };
            throw new Error('Local dev mock: no handler for ' + path);
        }

        async function api(path, options) {
            if (USE_MOCK_BACKEND) return mockApi(path, options);
            options = options || {};
            const headers = Object.assign({
                'Content-Type': 'application/json'
            }, options.headers || {});
            const response = await fetch(API_BASE + path, Object.assign({}, options, {
                headers
            }));
            let body = null;
            try {
                body = await response.json();
            } catch {
                /* empty body is fine */
            }
            if (!response.ok) {
                const message = (body && body.error) || ('Request failed (' + response.status + ')');
                throw new Error(message);
            }
            return body;
        }

        async function withButtonBusy(button, fn) {
            if (button.disabled) return;
            button.disabled = true;
            try {
                await fn();
            } finally {
                button.disabled = false;
            }
        }

        $('login-submit').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            const username = $('login-username').value.trim();
            const password = $('login-password').value;
            $('login-error').textContent = '';
            try {
                const result = await api('/login', {
                    method: 'POST',
                    body: JSON.stringify({
                        username,
                        password
                    }),
                });
                hostToken = result.hostToken;
                $('host-login-fields').classList.add('site-peter-is-this-ai--hidden');
                $('host-create-fields').classList.remove('site-peter-is-this-ai--hidden');
            } catch (err) {
                $('login-error').textContent = err.message;
            }
        }));

        $('choice-create').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            $('choice-host-error').textContent = '';
            const headcount = parseInt($('choice-headcount').value, 10);
            if (!headcount || headcount < 1 || headcount > HEADCOUNT_MAX) {
                $('choice-host-error').textContent = 'Enter a headcount from 1 to ' + HEADCOUNT_MAX + '.';
                return;
            }
            $('choice-host-error').textContent = 'Creating room...';
            try {
                const result = await api('/rooms', {
                    method: 'POST',
                    body: JSON.stringify({
                        hostToken,
                        expectedHeadcount: headcount,
                        autoStartDelaySeconds: AUTO_START_DELAY_SECONDS,
                    }),
                });
                roomCode = result.roomCode;
                participantId = result.participantId;
                sessionToken = result.sessionToken;
                isHost = true;
                myDisplayName = HOST_CHARACTER;
                saveSession();
                sessionStorage.setItem(CREATED_HERE_KEY, '1');
                $('choice-host-error').textContent = '';
                await enterLobby();
            } catch (err) {
                $('choice-host-error').textContent = err.message;
            }
        }));

        $('choice-join').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            $('choice-join-error').textContent = '';
            const code = $('choice-room-code').value.trim().toUpperCase();
            if (!code) {
                $('choice-join-error').textContent = 'Enter a room code.';
                return;
            }
            $('choice-join-error').textContent = 'Joining...';
            try {
                const result = await api('/rooms/' + code + '/join', {
                    method: 'POST',
                    body: JSON.stringify({
                        displayName: null
                    }),
                });
                roomCode = code;
                participantId = result.participantId;
                sessionToken = result.sessionToken;
                isHost = false;
                myDisplayName = result.displayName;
                saveSession();
                $('choice-join-error').textContent = '';
                await enterLobby();
            } catch (err) {
                $('choice-join-error').textContent = err.message;
            }
        }));

        async function enterLobby() {
            await connectRealtime();
            await resyncState();
        }

        const AVATAR_STACK_LIMIT_DESKTOP = 8;
        const AVATAR_STACK_LIMIT_MOBILE = 4;

        function currentAvatarStackLimit() {
            return window.matchMedia('(min-width: 900px)').matches
                ? AVATAR_STACK_LIMIT_DESKTOP
                : AVATAR_STACK_LIMIT_MOBILE;
        }

        function renderParticipants(participants, expectedHeadcount) {
            const list = $('lobby-participants');
            list.innerHTML = '';
            const ordered = [
                ...participants.filter((p) => p.participantId === participantId),
                ...participants.filter((p) => p.participantId !== participantId),
            ];
            const visible = ordered.slice(0, currentAvatarStackLimit());
            const overflowCount = ordered.length - visible.length;
            visible.forEach((p, index) => {
                const isMe = p.participantId === participantId;
                const li = document.createElement('li');
                let className = 'site-peter-is-this-ai__avatar';
                if (isMe) className += ' site-peter-is-this-ai__avatar--you';
                li.className = className;
                li.style.backgroundImage = 'url(' + avatarImageFor(p.displayName) + ')';
                li.style.zIndex = String(visible.length - index);
                li.title = isMe ? 'Me (' + p.displayName + ')' : p.displayName;
                list.appendChild(li);
            });
            if (overflowCount > 0) {
                const li = document.createElement('li');
                li.className = 'site-peter-is-this-ai__avatar site-peter-is-this-ai__avatar--overflow';
                li.style.zIndex = '0';
                li.textContent = '+' + overflowCount;
                li.title = overflowCount + ' more';
                list.appendChild(li);
            }
            $('lobby-count').textContent = participants.length + ' of ' + expectedHeadcount + ' joined for ' + roomCode;
            $('lobby-host-actions').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
        }

        $('lobby-start-submission').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            setStatus('Starting submissions...');
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
                setStatus(err.message);
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
                clearSession();
                showPhase('choice');
            } catch (err) {
                setStatus(err.message);
            } finally {
                if (button) button.disabled = false;
            }
        }

        $('lobby-stop-session').addEventListener('click', stopSessionForEveryone);
        $('submission-stop-session').addEventListener('click', stopSessionForEveryone);
        $('voting-stop-session').addEventListener('click', stopSessionForEveryone);

        let composerImages = [];

        function updateSubmitEnabled() {
            const hasText = $('submission-textarea').value.trim().length > 0;
            $('submission-submit').disabled = !(hasText || composerImages.length > 0);
        }

        function renderImageChips() {
            const preview = $('submission-image-preview');
            const textarea = $('submission-textarea');
            preview.innerHTML = '';
            if (composerImages.length === 0) {
                preview.classList.add('site-peter-is-this-ai--hidden');
                textarea.classList.remove('site-peter-is-this-ai--hidden');
                updateSubmitEnabled();
                return;
            }
            preview.classList.remove('site-peter-is-this-ai--hidden');
            textarea.classList.add('site-peter-is-this-ai--hidden');
            composerImages.forEach((dataUri, index) => {
                const chip = document.createElement('div');
                chip.className = 'site-peter-is-this-ai__composer-image-chip';
                // The blurred image is rendered slightly larger than this
                // wrapper and clipped to it, so the wrapper's crisp corners
                // define the chip's shape (blur is a whole-element effect,
                // so blurring the <img> directly would soften its edges
                // too, not just its content).
                const thumb = document.createElement('div');
                thumb.className = 'site-peter-is-this-ai__composer-image-chip-thumb';
                const img = document.createElement('img');
                img.src = dataUri;
                img.alt = 'Attached image';
                img.draggable = false;
                thumb.appendChild(img);
                chip.appendChild(thumb);
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'site-peter-is-this-ai__composer-image-chip-remove';
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
                $('submission-error').textContent = 'Please choose an image file.';
                return;
            }
            $('submission-error').textContent = '';
            $('submission-status').textContent = files.length > 1 ? 'Processing images...' : 'Processing image...';
            await nextPaint();
            const compressed = [];
            for (const file of files) {
                try {
                    compressed.push(await compressImageToDataUri(file));
                } catch (err) {
                    $('submission-error').textContent = err.message;
                }
                await nextPaint();
            }
            $('submission-status').textContent = '';
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
            submissionComposerEl.classList.add('site-peter-is-this-ai__composer--drag-over');
        });
        submissionComposerEl.addEventListener('dragleave', () => {
            submissionComposerEl.classList.remove('site-peter-is-this-ai__composer--drag-over');
        });
        submissionComposerEl.addEventListener('drop', (event) => {
            event.preventDefault();
            submissionComposerEl.classList.remove('site-peter-is-this-ai__composer--drag-over');
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
                nav.classList.add('site-peter-is-this-ai--hidden');
                return;
            }
            nav.classList.remove('site-peter-is-this-ai--hidden');
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
            } else {
                setComposerImages([]);
                $('submission-textarea').value = current ? current.content : '';
            }
            $('submission-status').textContent = current ? 'Submitted. You can keep editing until the host starts voting.' : '';
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

        $('submission-textarea').addEventListener('input', () => {
            $('submission-status').textContent = '';
            $('submission-error').textContent = '';
            updateSubmitEnabled();
        });

        let submissionSubmitInFlight = false;

        $('submission-submit').addEventListener('click', async (event) => {
            const button = event.currentTarget;
            if (submissionSubmitInFlight || button.disabled) return;
            $('submission-error').textContent = '';
            $('submission-status').textContent = '';
            const editing = mySubmissions[mySubmissionCursor];
            const textContent = $('submission-textarea').value.trim();
            if (composerImages.length === 0 && !textContent) {
                $('submission-error').textContent = 'Paste or enter something, or attach an image.';
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
                if (!createdAny) {
                    // Pure edit-in-place (existing text, or a single existing
                    // image swapped for another) -- nothing new was added to
                    // the list, so stay right where we are instead of
                    // jumping anywhere.
                    renderSubmissionNav();
                    $('submission-status').textContent = 'Submitted. You can keep editing until the host starts voting.';
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
                    $('submission-status').textContent = 'Submitted! You can make another submission, or edit a previous one until the host starts voting.';
                }
            } catch (err) {
                $('submission-error').textContent = err.message;
            } finally {
                submissionSubmitInFlight = false;
                updateSubmitEnabled();
            }
        });

        $('submission-start-voting').addEventListener('click', (event) => withButtonBusy(event.currentTarget, async () => {
            setStatus('Starting voting...');
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
                setStatus(err.message);
            }
        }));

        async function goBackToPhase(event) {
            const button = event.currentTarget;
            if (button.disabled) return;
            button.disabled = true;
            setStatus('Going back...');
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
                setStatus(err.message);
            } finally {
                button.disabled = false;
            }
        }

        $('submission-go-back').addEventListener('click', goBackToPhase);
        $('voting-go-back').addEventListener('click', goBackToPhase);

        function renderSubmissionProgress(submittedCount, totalParticipants, skippedCount) {
            let text = submittedCount + ' of ' + totalParticipants + ' submitted';
            if (skippedCount > 0) {
                text += '; ' + skippedCount + (skippedCount === 1 ? ' user was skipped' : ' users were skipped');
            }
            $('submission-host-count').textContent = text;
        }

        function enterSubmissionPhase() {
            showPhase('submission');
            $('submission-host-actions').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
            $('submission-host-count').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
            $('submission-status').classList.toggle('site-peter-is-this-ai--hidden', isHost);
            updateSubmitEnabled();
        }

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
            card.className = 'site-peter-is-this-ai__swipe-card site-peter-is-this-ai__swipe-card--fresh';
            if (stackLevel === 0) {
                card.classList.add('site-peter-is-this-ai__swipe-card--top');
            } else {
                card.classList.add('site-peter-is-this-ai__swipe-card--stack-' + stackLevel);
            }
            if (isImageContent(content)) {
                card.classList.add('site-peter-is-this-ai__swipe-card--image');
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
            card.classList.remove('site-peter-is-this-ai__swipe-card--fresh');
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

            let restLeft = 0;
            let restRight = 0;

            function onPointerDown(event) {
                if (locked || (options.isLocked && options.isLocked())) return;
                dragging = true;
                startX = event.clientX;
                const restRect = card.getBoundingClientRect();
                restLeft = restRect.left;
                restRight = restRect.right;
                card.classList.add('site-peter-is-this-ai__swipe-card--dragging');
                card.setPointerCapture(event.pointerId);
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

            function onPointerUp() {
                if (!dragging) return;
                dragging = false;
                card.classList.remove('site-peter-is-this-ai__swipe-card--dragging');
                if (hintAi) hintAi.style.opacity = '0';
                if (hintHuman) hintHuman.style.opacity = '0';
                if (Math.abs(rawDx) >= SWIPE_THRESHOLD) {
                    const direction = rawDx > 0 ? 'right' : 'left';
                    const flyClass = rawDx > 0 ? 'site-peter-is-this-ai__swipe-card--fly-right' : 'site-peter-is-this-ai__swipe-card--fly-left';
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
            $('voting-error').textContent = '';
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
                $('voting-error').textContent = err.message;
                card.classList.remove('site-peter-is-this-ai__swipe-card--fly-left', 'site-peter-is-this-ai__swipe-card--fly-right');
            } finally {
                swipeVoting = false;
            }
        }

        function attachVotingSwipe(card) {
            const deck = $('voting-deck');
            const hintAi = deck.querySelector('.site-peter-is-this-ai__swipe-hint--ai');
            const hintHuman = deck.querySelector('.site-peter-is-this-ai__swipe-hint--human');
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
            const card = deck.querySelector('.site-peter-is-this-ai__swipe-card--top') || deck.querySelector('.site-peter-is-this-ai__swipe-card');
            if (!card) return;
            const flyClass = verdict === 'human' ? 'site-peter-is-this-ai__swipe-card--fly-right' : 'site-peter-is-this-ai__swipe-card--fly-left';
            card.classList.add(flyClass);
            castVoteAndAdvance(verdict, card);
        }

        $('voting-vote-ai').addEventListener('click', () => voteFromButton('ai'));
        $('voting-vote-human').addEventListener('click', () => voteFromButton('human'));

        function renderVotingItem(data) {
            $('voting-host-actions').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
            if (data.done) {
                $('voting-active').classList.add('site-peter-is-this-ai--hidden');
                $('voting-waiting').classList.remove('site-peter-is-this-ai--hidden');
                return;
            }
            $('voting-active').classList.remove('site-peter-is-this-ai--hidden');
            $('voting-waiting').classList.add('site-peter-is-this-ai--hidden');
            $('voting-error').textContent = '';

            const deck = $('voting-deck');
            deck.querySelectorAll('.site-peter-is-this-ai__swipe-card').forEach((card) => card.remove());
            const stack = [data.content, ...(data.upcoming || [])];
            renderCardStack(deck, stack, attachVotingSwipe);
        }

        async function loadResults() {
            $('results-host-actions').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
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
                setStatus(err.message);
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
            deck.querySelectorAll('.site-peter-is-this-ai__swipe-card').forEach((card) => card.remove());
            if (!resultsItems.length) {
                $('results-tally').classList.add('site-peter-is-this-ai--hidden');
                deck.appendChild(buildSwipeCard('No submissions.', 0));
                return;
            }
            if (resultsDismissed) {
                $('results-tally').classList.add('site-peter-is-this-ai--hidden');
                const img = document.createElement('img');
                img.src = RESULTS_END_IMAGES[Math.floor(Math.random() * RESULTS_END_IMAGES.length)];
                img.alt = "That's everyone -- tap to see results again.";
                img.className = 'site-peter-is-this-ai__results-end-image';
                img.addEventListener('click', () => {
                    resultsDismissed = false;
                    resultsIndex = resultsItems.length - 1;
                    renderResultsItem();
                });
                deck.appendChild(img);
                return;
            }
            $('results-tally').classList.remove('site-peter-is-this-ai--hidden');
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

        const MAX_RECONNECT_ATTEMPTS = 6;

        async function attemptReconnect() {
            if (!roomCode || !sessionToken) return;
            if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                setStatus('Disconnected. Tap Refresh to rejoin.');
                return;
            }
            reconnectAttempts += 1;
            const delayMs = Math.min(1500 * (2 ** (reconnectAttempts - 1)), 20000);
            setStatus('Connection lost. Retrying in ' + Math.ceil(delayMs / 1000) + 's...');
            await wait(delayMs);
            if (!roomCode) return;
            connection = null;
            try {
                await connectRealtime();
                await resyncState();
                reconnectAttempts = 0;
                setStatus('');
            } catch {
                connection = null;
                await attemptReconnect();
            }
        }

        async function connectRealtime() {
            if (connection) return;
            if (USE_MOCK_BACKEND) {
                connection = mock.fakeConnection();
            } else {
                await ensureSignalRLoaded();
                if (!window.signalR) {
                    setStatus('SignalR failed to load. Refresh and try again.');
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
                    setStatus('Could not connect to realtime updates. Refresh to retry.');
                    return;
                }
                connection = new window.signalR.HubConnectionBuilder()
                    .withUrl(negotiateInfo.url, {
                        accessTokenFactory: () => negotiateInfo.accessToken
                    })
                    .withAutomaticReconnect()
                    .build();
            }

            connection.on('PresenceUpdated', (data) => renderParticipants(data.participants, data.expectedHeadcount));
            connection.on('PhaseChanged', async (data) => {
                if (data.phase === 'lobby') showPhase('lobby');
                if (data.phase === 'submission') enterSubmissionPhase();
                if (data.phase === 'voting') {
                    showPhase('voting');
                    const item = await api('/rooms/' + roomCode + '/voting-item', {
                        headers: {
                            'x-session-token': sessionToken
                        },
                    });
                    renderVotingItem(item);
                }
                if (data.phase === 'results') {
                    showPhase('results');
                    loadResults();
                }
            });
            connection.on('AutoStartScheduled', (data) => {
                scheduleAutoStart(Date.now() + (data.delaySeconds || 0) * 1000);
            });
            connection.on('SubmissionArrived', (data) => {
                if (!isHost) return;
                renderSubmissionProgress(data.submittedCount, data.totalParticipants, data.skippedCount);
            });
            connection.on('VoteTallyUpdated', (data) => {
                $('voting-tally').textContent = data.votedCount + ' of ' + data.totalParticipants + ' voted on that item';
                $('voting-tally').classList.toggle('site-peter-is-this-ai--hidden', !isHost);
            });
            connection.on('ResultsReady', () => loadResults());
            connection.on('RoomStopped', () => {
                clearSession();
                window.location.reload();
            });
            connection.on('RoomRestarted', () => {
                clearSession();
                window.location.reload();
            });

            async function joinSignalRGroups() {
                await api('/rooms/' + roomCode + '/join-groups', {
                    method: 'POST',
                    body: JSON.stringify({
                        sessionToken,
                        participantId
                    }),
                });
            }

            connection.onreconnecting(() => setStatus('Reconnecting...'));
            connection.onreconnected(async () => {
                await joinSignalRGroups();
                setStatus('');
                await resyncState();
            });
            if (USE_MOCK_BACKEND && connection.onExternalChange) {
                connection.onExternalChange(async (rooms) => {
                    if (!rooms[roomCode]) {
                        clearSession();
                        window.location.reload();
                        return;
                    }
                    await resyncState();
                });
            }
            connection.onclose(() => attemptReconnect());
            await connection.start();
            await joinSignalRGroups();
        }

        async function resyncState() {
            try {
                const state = await api('/rooms/' + roomCode + '/state', {
                    headers: {
                        'x-session-token': sessionToken
                    },
                });
                isHost = state.isHost;
                const me = state.participants.find((p) => p.participantId === participantId);
                if (me) {
                    myDisplayName = me.displayName;
                    saveSession();
                }
                renderParticipants(state.participants, state.expectedHeadcount);
                if (state.phase === 'lobby') {
                    showPhase('lobby');
                    if (state.autoStartAt) {
                        const targetAt = new Date(state.autoStartAt).getTime();
                        if (targetAt > Date.now()) {
                            scheduleAutoStart(targetAt);
                        } else {
                            clearAutoStartCountdown();
                        }
                    } else {
                        clearAutoStartCountdown();
                    }
                }
                if (state.phase === 'submission') {
                    enterSubmissionPhase();
                    renderSubmissionProgress(state.submittedCount, state.participants.length, state.skippedCount);
                    if (!mySubmissionsHydrated) {
                        mySubmissionsHydrated = true;
                        mySubmissions = state.mySubmissions || [];
                        mySubmissionCursor = mySubmissions.length ? mySubmissions.length - 1 : 0;
                        loadSubmissionAtCursor();
                    }
                }
                if (state.phase === 'voting') {
                    showPhase('voting');
                    const item = await api('/rooms/' + roomCode + '/voting-item', {
                        headers: {
                            'x-session-token': sessionToken
                        },
                    });
                    renderVotingItem(item);
                }
                if (state.phase === 'results') {
                    showPhase('results');
                    loadResults();
                }
            } catch (err) {
                setStatus(err.message);
            }
        }

        $('restart-session').addEventListener('click', stopSessionForEveryone);

        function requestStopBeacon() {
            if (!isHost || !roomCode || !sessionToken) return;
            // `localStorage` is shared across every tab/window of this browser
            // profile, so a second window opened on the same origin silently
            // inherits the host session too. Only the tab that actually
            // created the room should be able to end it on close -- otherwise
            // closing what looks like a harmless duplicate window stops the
            // game for everyone.
            if (sessionStorage.getItem(CREATED_HERE_KEY) !== '1') return;
            if (USE_MOCK_BACKEND) {
                try {
                    mock.api.stop(roomCode);
                } catch {
                    /* best effort */
                }
                return;
            }
            if (!navigator.sendBeacon) return;
            const payload = new Blob([JSON.stringify({
                sessionToken
            })], {
                type: 'application/json'
            });
            navigator.sendBeacon(API_BASE + '/rooms/' + roomCode + '/stop', payload);
        }

        window.addEventListener('pagehide', requestStopBeacon);

        (async function resumeIfPossible() {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) {
                showPhase('choice');
                return;
            }
            try {
                const parsed = JSON.parse(saved);
                roomCode = parsed.roomCode;
                participantId = parsed.participantId;
                sessionToken = parsed.sessionToken;
                isHost = parsed.isHost;
                myDisplayName = parsed.myDisplayName || null;
                await connectRealtime();
                await resyncState();
            } catch {
                clearSession();
                showPhase('choice');
            }
        })();
    }

    function bootIsThisAI() {
        document.querySelectorAll('.site-peter-is-this-ai[data-peter-is-this-ai="true"]').forEach(initIsThisAI);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bootIsThisAI, {
            once: true
        });
    } else {
        bootIsThisAI();
    }
})();
