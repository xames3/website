/*
Animations Script
=================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 17 October 2026
Last updated on: 11 November 2026
*/

(() => {
    'use strict';

    const {
        REVEAL_SHOWN,
        REVEAL_WAITING,
        TIMING,
        attempt,
        clamp,
        decodeId,
        fetchJson,
        getCssVar,
        glideTo,
        headerHeight,
        holdPlace,
        isModifiedClick,
        motion: engine,
        onScroll,
        onVisible,
        prefersReducedMotion,
        prefersStill,
        rafThrottle,
        say,
        settleHash,
        springProgress,
    } = window.Kaamiki;
    const root = document.documentElement;

    const CLAMP_SLACK_PX = 48;
    const CLAMP_SETTLE_MS = 60;
    const CLAMP_MIN_PX = 320;
    const CLAMP_MIN_SCREEN_PX = 480;
    const HIGHLIGHT_WAIT_MS = 2000;
    const HIDDEN_PARTS = '.km-tabs__panel:not(.km-tabs__panel--current), '
        + 'details.km-accordion:not([open])';
    const CLAMP_ACCORDION_MIN_PX = 80;
    const ACCORDION_PX_FACTOR = 0.9;
    const BYLINE_BG_INTERVAL_MS = 7000;
    const BYLINE_BG_HIDDEN = '0.001';
    const BYLINE_BG_GROW_REM = 3;
    const TICKER_CELLS = 11;
    const TICKER_BLUR_PX = 2;
    const SWEEP_OUT_END = 0.7;
    const SWEEP_IN_START = 0.4;
    const SWEEP_RESIZE_LAG_SHARE = 0.25;
    const SWEEP_RESIZE_SHARE = 0.5;
    // https://developer.mozilla.org/en-US/docs/Web/CSS/hanging-punctuation#browser_compatibility
    const SAFARI = CSS.supports('hanging-punctuation', 'first');
    const TEXT_BLUR = SAFARI ? 'none' : 'blur(4px)';
    const ROLL_SPREAD_SHARE = 1;
    const ROLL_GLIDE_SHARE = 0.75;
    const ROLL_CLEAR_SHARE = 0.7;
    const ROLL_APPEAR_SHARE = 0.25;
    const ROLL_QUICK_SHARE = 0.3;
    const ROLL_OVERLAP_EM = 0.12;
    const ROLL_FRAME_MS = 1000 / 60;
    const ROLL_GLIDE_END_PX = 1.5;
    const ROLL_GLIDE_MIN_X = 2.5;
    const ROLL_WHOLE = new RegExp(
        '[\\p{Script=Arabic}\\p{Script=Syriac}\\p{Script=Mongolian}'
        + '\\p{Script=Nko}\\p{Script=Devanagari}\\p{Script=Bengali}'
        + '\\p{Script=Gurmukhi}\\p{Script=Gujarati}\\p{Script=Oriya}'
        + '\\p{Script=Tamil}\\p{Script=Telugu}\\p{Script=Kannada}'
        + '\\p{Script=Malayalam}\\p{Script=Sinhala}\\p{Script=Thai}'
        + '\\p{Script=Lao}\\p{Script=Khmer}\\p{Script=Myanmar}'
        + '\\p{Script=Tibetan}]',
        'u',
    );
    const ROLL_PARTS = typeof Intl.Segmenter === 'function'
        ? new Intl.Segmenter(undefined, { granularity: 'grapheme' })
        : null;
    const REVEAL_BUDGET_MS = 1600;
    const REVEAL_MIN_STEP_MS = 30;
    const TITLE_ITEM = 'km-title-item';
    const TITLE_STEPS = 4;
    const SPEECH_WORD_MS = 170;
    const SPEECH_CHAR_MS = 14;
    const SPEECH_COMMA_MS = 260;
    const SPEECH_STOP_MS = 480;
    const SPEECH_MAX_MS = 9000;
    const SPEECH_GAP_WORDS = 5;
    const SPEECH_FIX_WORDS = 3;
    const SOUND_ALIKES = new Map(Object.entries({
        'your': "you're", "you're": 'your', 'their': 'there', 'there': 'their',
        "they're": 'there', 'to': 'two', 'too': 'to', 'two': 'to',
        'for': 'four', 'four': 'for', 'no': 'know', 'know': 'no', 'knew': 'new',
        'new': 'knew', 'write': 'right', 'right': 'write', 'one': 'won',
        'won': 'one', 'would': 'wood', 'hear': 'here', 'here': 'hear',
        'by': 'buy', 'buy': 'by', 'be': 'bee', 'see': 'sea', 'sea': 'see',
        'son': 'sun', 'sun': 'son', 'whole': 'hole', 'hole': 'whole',
        'weak': 'week', 'week': 'weak', 'peace': 'piece', 'piece': 'peace',
        'break': 'brake', 'meat': 'meet', 'meet': 'meat', 'which': 'witch',
        'way': 'weigh', 'wait': 'weight', 'where': 'wear', 'wear': 'where',
        'weather': 'whether', 'whether': 'weather', 'hour': 'our',
        'our': 'hour', 'its': "it's", "it's": 'its', 'then': 'than',
        'than': 'then', 'of': 'off', 'off': 'of', 'are': 'our', 'were': 'where',
        "we're": 'were', 'said': 'set', 'man': 'men', 'men': 'man',
        'live': 'leave', 'leave': 'live', 'loved': 'lived', 'lived': 'loved',
        'if': 'is', 'is': 'if', 'me': 'be', 'like': 'light', 'life': 'live',
        'walk': 'work', 'work': 'walk', 'calm': 'come', 'storm': 'store',
        'form': 'from', 'from': 'form', 'through': 'threw', 'threw': 'through',
        'teach': 'each', 'learn': 'earn', 'master': 'muster', 'want': "won't",
        'something': 'some thing', 'someone': 'some one', 'will': 'well',
        'well': 'will', 'mind': 'mine', 'mine': 'mind', 'told': 'toll',
        'feel': 'fill', 'dream': 'cream', 'time': 'thyme',
        'forward': 'foreword', 'moving': 'mooing',
    }));

