/* global Search */
(() => {
    'use strict';

    const SKIP = '.km-byline, [data-km-search-skip]';
    const BLOCKS = 'p, li, h1, h2, h3, h4, h5, h6, label, div, figcaption, '
        + 'dt, dd';
    const original = Search.htmlToText;

    Search.htmlToText = (htmlString, anchor) => {
        const page = new DOMParser().parseFromString(htmlString, 'text/html');
        if (!page.querySelector('[role="main"]')) {
            return original(htmlString, anchor);
        }
        page.querySelectorAll(SKIP).forEach((element) => element.remove());
        page.querySelectorAll(BLOCKS).forEach((element) => element.append(' '));
        return original(page.documentElement.outerHTML, anchor);
    };
})();
