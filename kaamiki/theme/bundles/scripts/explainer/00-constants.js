/*
Explainer Script
================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 17 October 2026
Last updated on: 08 November 2026
*/

(() => {
    'use strict';

    const {
        TIMING,
        announce,
        clamp,
        copyText,
        headerHeight,
        onScroll,
        prefersReducedMotion,
        prefersStill,
        rafThrottle,
        say,
        stopGlide,
        codeExplains,
    } = window.Kaamiki;
    const root = document.documentElement;

    const STAGE_MIN_LINES = 6;
    const RESIZE_JITTER_PX = 120;
    const RESIZE_SETTLE_MS = 120;
    const STAGE_MIN_WIDTH_PX = 880;
    const STAGE_PADDING_PX = 16;
    const STAGE_SPACE_SHARE = 0.6;
    const STAGE_MARGIN_PX = 24;
    const REARM_DISTANCE_PX = 120;
    const LOCK_GRACE_MS = 350;
    const HAND_WINDOW_MS = 500;
    const TOUCH_GLIDE_MS = 1500;
    const FOCUS_SCROLL_WINDOW_MS = 300;
    const TRACK_STIFFNESS = 16;
    const STACK_MAX_LINES = 12;
    const DIFF_VISIBLE_SWAPS = 3;
    const ANIMATE_WITHIN_STEPS = 2;
    let held = null;
    let handUntil = 0;
    let wired = false;

