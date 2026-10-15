(() => {
    'use strict';

    const ORIGIN = 'https://app.cal.com';

    window.Cal = window.Cal || function Cal(action, namespace, config) {
        const cal = window.Cal;
        if (!cal.loaded) {
            cal.loaded = true;
            cal.ns = {};
            cal.q = [];
            document.head.appendChild(document.createElement('script')).src = `${ORIGIN}/embed/embed.js`;
        }
        const api = function api(...args) { api.q.push(args); };
        api.q = [];
        cal.ns[namespace] = cal.ns[namespace] || api;
        cal.ns[namespace].q.push([action, namespace, config]);
        cal.q.push(['initNamespace', namespace]);
    };

    document.addEventListener('click', (event) => {
        const link = event.target.closest?.('a[href="#"]');
        if (link?.hasAttribute('data-cal-link') || link?.querySelector('[data-cal-link]')) event.preventDefault();
    });

    const seen = new Set();
    document.querySelectorAll('[data-cal-namespace]').forEach((el) => {
        const ns = el.getAttribute('data-cal-namespace');
        if (!ns || seen.has(ns)) return;
        seen.add(ns);
        Cal('init', ns, { origin: ORIGIN });
        Cal.ns[ns]('ui', { hideEventTypeDetails: false, layout: 'month_view' });
    });
})();
