/*
Theme Script
============

Author: Akshay Mestry <xa@mes3.dev>
Created on: 15 October 2026
Last updated on: 18 November 2026
*/

(() => {
    'use strict';

    const {
        FOCUSABLE,
        TIMING,
        anchorTargetY,
        announce,
        attempt,
        clamp,
        copyText,
        decodeId,
        fetchJson,
        glideAcross,
        glideTo,
        headerHeight,
        isModifiedClick,
        layoutTop,
        makeIcon,
        motion: engine,
        onVisible,
        prefersReducedMotion,
        prefersStill,
        rafThrottle,
        say,
        settleHash,
    } = window.Kaamiki;
    const root = document.documentElement;

    const SCROLL_QUIET_FRAMES = 3;
    const SCROLL_PATIENCE_MS = 3000;
    const PIXELATE_RATIO = 20;
    const DROPDOWN_OPEN_DELAY_MS = 40;
    const DOTS_TRAIL_SHARE = 0.2;
    const REVEAL_FEATHER_SHARE = 0.5;
    const REVEAL_FEATHER_MIN_PX = 280;
    const REVEAL_FEATHER_MAX_PX = 900;
    const REVEAL_STRETCH = 2.2;
    const COPY_HOLD_POLL_MS = 50;
    const YOUTUBE_PLAY_WAIT_MS = 1000;
    const COPY_HOLD_POLLS = 60;
    const PREFETCH_HOVER_MS = 65;
    const PREFETCH_QUIET_MS = 2500;
    const DRAWER_DRAG_START_PX = 10;
    const DRAWER_CLOSE_SHARE = 0.4;
    const DRAWER_FLICK_PX_PER_MS = 0.55;
    const DRAWER_VELOCITY_WINDOW_MS = 90;
    const DRAWER_COAST_MS = 120;
    const ENLARGE_SHRUNK = 0.9;
    const ENLARGE_GAIN = 1.1;
    const ENLARGE_SEEN_SHARE = 0.25;
    const ENLARGE_GAP_PX = 12;
    const ENLARGE_CAPTION_MIN_PX = 280;
    const ENLARGE_CAPTION_PASSES = 3;
    const ENLARGE_PLACEHOLDER_PX = 32;
    const ENLARGE_STILL_FADE_MS = 160;
    const ENLARGE_FADE_SLACK_MS = 60;
    const ENLARGE_DRAG_START_PX = 10;
    const ENLARGE_DRAG_FLOOR_PX = 160;
    const ENLARGE_DRAG_FADE_SHARE = 0.5;
    const ENLARGE_DRAG_SHRINK = 0.2;
    const ENLARGE_CLOSE_SHARE = 0.4;
    const ENLARGE_FLICK_PX_PER_MS = 0.55;
    const ENLARGE_VELOCITY_WINDOW_MS = 90;
    const ENLARGE_COAST_MS = 120;
    const ENLARGE_SETTLE_RATIO = 1.4;
    const ENLARGE_GREY = 'grayscale(1)';
    const ENLARGE_RING_HOLD_MS = 1500;
    const DROPDOWN_CLOSE_DELAY_MS = 140;
    const DROPDOWN_SWITCH_DELAY_MS = 90;
    const DROPDOWN_AIM_WINDOW_MS = 120;
    const DROPDOWN_AIM_STEP_MS = 60;
    const DROPDOWN_AIM_MS = 450;
    const DROPDOWN_PIN_MS = 300;
    const DROPDOWN_EDGE_PX = 8;
    const DROPDOWN_ROWS = 3;
    const SIDEBAR_WIDE_PX = 768;
    const NAV_WIDE_PX = 960;
    const NAV_WRAPPED = 'km-document--nav-wrapped';
    const SCROLLTOP_AFTER_PX = 200;
    const HEADER_LINE_REACH_PX = 72;
    const TOOLTIP_ROOM_PX = 32;

