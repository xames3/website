"""\
Font Awesome Icons
==================

Author: Akshay Mestry <xa@mes3.dev>
Created on: 27 October 2026
Last updated on: 07 November 2026

Every icon Kaamiki draws, as a Pro icon and the Free one that stands in
for it.

A site with a Font Awesome kit gets the Pro icons, in its
`kaamiki.conf.icons.style`. A site without one gets the Free icons,
which are fewer and come in three styles, `solid`, `regular` and
`brands`. Every icon Kaamiki writes into a page comes from `Icons`,
which knows which of the two the site has.

The names Font Awesome Free 7.3.1 draws, the version Kaamiki loads, are
listed at the end of the file.
"""

from __future__ import annotations

import dataclasses
import difflib
import os
import typing as t
from types import MappingProxyType

from kaamiki.extensions.utils import checks

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from sphinx.config import Config

DEFAULT_STYLE: t.Final[str] = "regular"
KIT_VARIABLE: t.Final[str] = "KAAMIKI_FA_KIT"
STYLE_ALIASES: t.Final[dict[str, str]] = {
    "fab": "brands",
    "fal": "light",
    "far": "regular",
    "fas": "solid",
    "fat": "thin",
}
REGULAR_FIRST: t.Final[frozenset[str]] = frozenset({"light", "regular", "thin"})


class IconPair(t.NamedTuple):
    """An icon as a Pro kit draws it and as Font Awesome Free does.

    `pro` is a name like `house`, which takes the site's
    `kaamiki.conf.icons.style`, or the classes in full,
    `fa-brands fa-python`. `free` is always the classes in full and
    always an icon Font Awesome Free has.
    """

    pro: str
    free: str


def brand_pair(name: str) -> IconPair:
    """Pair a brand with itself, as Free has every brand Pro does.

    :param name: The brand's name, as `python`.
    :return: The brand's pair.
    """
    classes = f"fa-brands fa-{name}"
    return IconPair(classes, classes)


def solid(name: str) -> IconPair:
    """Pair an icon that is always drawn solid, with a kit or without.

    :param name: The icon's name, as `chevron-down`.
    :return: The pair.
    """
    return IconPair(f"fa-solid fa-{name}", f"fa-solid fa-{name}")


FILE_ICON: t.Final[IconPair] = IconPair(
    "file-lines", "fa-regular fa-file-lines"
)
ROLE_ICONS: t.Final[Mapping[str, IconPair]] = MappingProxyType(
    {
        "breadcrumb_separator_child": IconPair(
            "angle-right", "fa-solid fa-angle-right"
        ),
        "breadcrumb_separator_parent": IconPair(
            "angles-right", "fa-solid fa-angles-right"
        ),
        "copy_url": IconPair("link", "fa-solid fa-link"),
        "external_link": IconPair(
            "arrow-up-right-from-square",
            "fa-solid fa-arrow-up-right-from-square",
        ),
        "feedback": IconPair("paper-plane", "fa-regular fa-paper-plane"),
        "language": IconPair("language", "fa-solid fa-language"),
        "menu": IconPair("bars", "fa-solid fa-bars"),
        "page_source": FILE_ICON,
        "play": IconPair("play", "fa-solid fa-play"),
        "reading_time": IconPair("clock", "fa-regular fa-clock"),
        "release_date": IconPair("calendar", "fa-regular fa-calendar"),
        "release_notes": IconPair("tag", "fa-solid fa-tag"),
        "scrolltop": IconPair("arrow-up", "fa-solid fa-arrow-up"),
        "search": IconPair("magnifying-glass", "fa-solid fa-magnifying-glass"),
        "show_more": IconPair("chevron-down", "fa-solid fa-chevron-down"),
        "nav_arrow": solid("chevron-down"),
        "list_tick": IconPair("check", "fa-solid fa-check"),
        "copy": IconPair("clipboard", "fa-solid fa-clipboard"),
        "copied": IconPair("check", "fa-solid fa-check"),
        "admonition_note": IconPair("circle-info", "fa-solid fa-circle-info"),
        "admonition_seealso": IconPair("globe", "fa-solid fa-globe"),
        "admonition_tip": IconPair("compass", "fa-solid fa-compass"),
        "admonition_hint": IconPair("lightbulb", "fa-solid fa-lightbulb"),
        "admonition_important": IconPair("star", "fa-solid fa-star"),
        "admonition_danger": IconPair(
            "skull-crossbones", "fa-solid fa-skull-crossbones"
        ),
        "admonition_error": IconPair("bug", "fa-solid fa-bug"),
        "admonition_warning": IconPair(
            "triangle-exclamation", "fa-solid fa-triangle-exclamation"
        ),
        "repository_mark": brand_pair("github"),
        "repository_stars": solid("star"),
        "repository_forks": solid("code-fork"),
        "release_added": IconPair(
            "code-pull-request", "fa-solid fa-code-pull-request"
        ),
        "release_changed": IconPair("code-branch", "fa-solid fa-code-branch"),
        "release_fixed": IconPair("code-merge", "fa-solid fa-code-merge"),
        "release_removed": IconPair("ban", "fa-solid fa-ban"),
        "release_other": IconPair("circle", "fa-solid fa-circle"),
    }
)
BLANK_ROLES: t.Final[tuple[str, ...]] = ("release_notes",)
ACCORDION_MARKERS: t.Final[Mapping[str, IconPair]] = MappingProxyType(
    {
        "plus": IconPair("plus", "fa-solid fa-plus"),
        "down": IconPair("chevron-down", "fa-solid fa-chevron-down"),
        "right": IconPair("chevron-right", "fa-solid fa-chevron-right"),
    }
)
KEY_ICONS: t.Final[Mapping[str, IconPair]] = MappingProxyType(
    {
        "caret-up": IconPair("caret-up", "fa-solid fa-caret-up"),
        "caret-down": IconPair("caret-down", "fa-solid fa-caret-down"),
        "caret-left": IconPair("caret-left", "fa-solid fa-caret-left"),
        "caret-right": IconPair("caret-right", "fa-solid fa-caret-right"),
        "chevron-up": IconPair("chevron-up", "fa-solid fa-chevron-up"),
        "chevron-down": IconPair("chevron-down", "fa-solid fa-chevron-down"),
        "chevron-left": IconPair("chevron-left", "fa-solid fa-chevron-left"),
        "chevron-right": IconPair("chevron-right", "fa-solid fa-chevron-right"),
        "globe": IconPair("fa-light fa-globe", "fa-solid fa-globe"),
        "microsoft": brand_pair("microsoft"),
        "ubuntu": brand_pair("ubuntu"),
    }
)
LANGUAGE_ICONS: t.Final[tuple[tuple[IconPair, frozenset[str]], ...]] = (
    (
        brand_pair("python"),
        frozenset({"py", "py3", "pycon", "python", "python3"}),
    ),
    (
        brand_pair("js"),
        frozenset({"javascript", "js", "jsx", "node", "nodejs"}),
    ),
    (brand_pair("typescript"), frozenset({"ts", "tsx", "typescript"})),
    (brand_pair("rust"), frozenset({"rs", "rust"})),
    (brand_pair("golang"), frozenset({"go", "golang"})),
    (brand_pair("java"), frozenset({"java"})),
    (brand_pair("swift"), frozenset({"swift"})),
    (brand_pair("r-project"), frozenset({"r", "rscript"})),
    (brand_pair("php"), frozenset({"php", "php3", "php4", "php5"})),
    (brand_pair("erlang"), frozenset({"erl", "erlang"})),
    (brand_pair("html5"), frozenset({"html", "xhtml"})),
    (brand_pair("css3-alt"), frozenset({"css"})),
    (brand_pair("sass"), frozenset({"sass", "scss"})),
    (brand_pair("less"), frozenset({"less"})),
    (brand_pair("markdown"), frozenset({"markdown", "md"})),
    (brand_pair("docker"), frozenset({"docker", "dockerfile"})),
    (brand_pair("vuejs"), frozenset({"vue"})),
    (brand_pair("android"), frozenset({"kotlin"})),
    (IconPair("gem", "fa-regular fa-gem"), frozenset({"rb", "ruby"})),
    (
        IconPair("database", "fa-solid fa-database"),
        frozenset(
            {"mysql", "plpgsql", "postgres", "postgresql", "sql", "sqlite3"}
        ),
    ),
    (
        IconPair("terminal", "fa-solid fa-terminal"),
        frozenset(
            {
                "bash",
                "bat",
                "batch",
                "console",
                "doscon",
                "fish",
                "powershell",
                "pwsh",
                "sh",
                "shell",
                "shell-session",
                "zsh",
            }
        ),
    ),
    (
        IconPair("brackets-curly", "fa-solid fa-code"),
        frozenset(
            {
                "c",
                "c++",
                "cpp",
                "cuda",
                "h",
                "hpp",
                "json",
                "json-object",
                "objc",
                "objective-c",
            }
        ),
    ),
    (
        IconPair("file-lines", "fa-regular fa-file-lines"),
        frozenset({"rest", "restructuredtext", "rst", "text", "txt"}),
    ),
    (
        IconPair("file-xml", "fa-regular fa-file-code"),
        frozenset({"xml"}),
    ),
    (
        IconPair("list", "fa-solid fa-list"),
        frozenset({"cfg", "dosini", "ini", "toml", "yaml", "yml"}),
    ),
)
STAND_INS: t.Final[Mapping[str, str]] = MappingProxyType(
    {
        "badge-check": "fa-regular fa-circle-check",
        "brackets-curly": "fa-solid fa-code",
        "file-xml": "fa-regular fa-file-code",
        "link-simple": "fa-solid fa-link",
        "sparkles": "fa-solid fa-wand-magic-sparkles",
        "table-columns-merge-previous": "fa-solid fa-table-columns",
    }
)


def read_kit(configured: str | None) -> str | None:
    """Find the Font Awesome kit a site gives in its conf or its shell.

    :param configured: The `kaamiki.conf.icons.kit` setting.
    :return: The setting, or what `KAAMIKI_FA_KIT` holds when the
        setting is empty, or `None` for no kit.
    """
    return configured or os.environ.get(KIT_VARIABLE) or None


def split(spec: str) -> tuple[list[str], str | None, str, list[str]]:
    """Take an icon apart.

    :param spec: The icon as `checks.icon` reads it: `plus`, `fa-plus`,
        `far fa-plus` or `fa-sharp fa-solid fa-plus fa-spin`.
    :return: The families (`fa-sharp`), the style by its plain name
        (`solid`), the icon's name without `fa-` and Font Awesome's own
        sizes and animations.
    """
    parts = spec.split()
    families: list[str] = []
    style: str | None = None
    while len(parts) > 1 and parts[0] in checks.FAMILIES:
        families.append(parts.pop(0))
    if len(parts) > 1 and parts[0] in checks.STYLES:
        token = parts.pop(0)
        style = STYLE_ALIASES.get(token) or token.removeprefix("fa-")
    name, *extras = parts
    return families, style, name.removeprefix("fa-"), extras


def free_classes(style: str, name: str) -> str | None:
    """Find the Font Awesome Free icon that draws a name.

    :param style: The style it was asked for, by its plain name.
    :param name: The icon's name without `fa-`.
    :return: The Free icon's classes, in the asked style when Free has
        it and in the nearest it does have when it hasn't, or its
        stand-in, or `None` when Free draws nothing like it.
    """
    if style == "brands":
        return f"fa-brands fa-{name}" if name in FREE_BRANDS else None
    order = ("solid", "regular")
    if style in REGULAR_FIRST:
        order = ("regular", "solid")
    for each in order:
        if name in FREE_STYLES[each]:
            return f"fa-{each} fa-{name}"
    return STAND_INS.get(name)


@dataclasses.dataclass(frozen=True, slots=True)
class Icons:
    """The icons a site draws, with a Font Awesome kit or without one.

    :param kit: The kit's address, or `None` for Font Awesome Free.
    :param style: The site's `kaamiki.conf.icons.style`. A kit draws
        icons in it when they name no style of their own. Without a
        kit it chooses between Free's `solid` and `regular` icons,
        where Free has both.
    """

    kit: str | None = None
    style: str = DEFAULT_STYLE

    @classmethod
    def of(cls, config: Config) -> Icons:
        """Read the icons a site has from its settings and its shell.

        :param config: The Sphinx configuration.
        :return: The site's icons.
        """
        from kaamiki.extensions.utils.settings import setting

        return cls(
            kit=read_kit(setting(config, "fa_kit")),
            style=setting(config, "fa_style"),
        )

    @property
    def font_style(self) -> str:
        """The style the stylesheet draws its icons in.

        A kit has every style. Free's `solid` is the one that has every
        icon the stylesheet draws.
        """
        return self.style if self.kit else "solid"

    def classes(self, spec: str) -> str:
        """Spell out an icon in full, the way the site can draw it.

        An icon that names no style takes the site's. One that names a
        family and no style, `fa-sharp fa-house` say, keeps Font
        Awesome's own default, `solid`, with a kit.

        :param spec: The icon as `checks.icon` reads it.
        :return: With a kit, the icon in the style it names or the
            site's. Without one, the Free icon that draws it, in the
            site's style where Free has both and in the one it has
            where it has only one.
        :raises ValueError: When there is no kit and Free has no icon
            of that name nor a stand-in for it.
        """
        families, style, name, extras = split(spec)
        if self.kit:
            if style is None and not families:
                style = "brands" if self.only_brand(name) else self.style
            head = [*families, *([f"fa-{style}"] if style else [])]
            return " ".join([*head, f"fa-{name}", *extras])
        if style is None:
            style = "brands" if self.only_brand(name) else self.style
        if families:
            style = "solid"
        found = free_classes(style, name)
        if found is None:
            raise ValueError(self.refusal(name))
        return " ".join([found, *extras])

    @staticmethod
    def only_brand(name: str) -> bool:
        """Say whether a name is a brand and nothing else.

        :param name: The icon's name without `fa-`.
        :return: Whether it's a brand with no solid or regular icon of
            its own, so a name with no style can only mean the brand.
        """
        return (
            name in FREE_BRANDS
            and name not in FREE_SOLID
            and name not in FREE_REGULAR
        )

    @staticmethod
    def refusal(name: str) -> str:
        """Say why a site with no kit can't draw an icon.

        :param name: The icon's name without `fa-`.
        :return: The sentence, with the nearest Free name when there is
            one.
        """
        near = difflib.get_close_matches(
            name,
            sorted(FREE_SOLID | FREE_REGULAR | FREE_BRANDS),
            1,
        )
        hint = f" Did you mean fa-{near[0]}?" if near else ""
        return (
            f"fa-{name} isn't a Font Awesome Free icon and Kaamiki has no"
            f" Free stand-in for it, so a site with no kit can't draw it."
            f" Set kaamiki.conf.icons.kit or {KIT_VARIABLE} for Pro icons or"
            f" pick a Free one.{hint}"
        )

    def pair(self, pair: IconPair) -> str:
        """Spell out a pair's icon, as the site can draw it.

        :param pair: The icon's Pro and Free versions.
        :return: The Pro one with a kit and the Free one without, a
            regular Free icon swapped for its solid twin when the
            site's style is `solid`.
        """
        if not pair.pro:
            return ""
        if self.kit:
            return self.classes(pair.pro)
        style, name = pair.free.split()
        if style == "fa-regular" and self.style == "solid":
            name = name.removeprefix("fa-")
            if name in FREE_SOLID:
                return f"fa-solid fa-{name}"
        return pair.free

    def custom(self, value: str | Mapping[str, str] | None) -> str:
        """Spell out an icon a site chose for itself.

        :param value: An icon like `checks.icon` reads it, or a table
            with a `pro` icon, a `free` one or both, to give the two
            plans an icon each. An empty string is no icon.
        :return: The icon's classes. A table is read for the plan the
            site has and falls back on the other's icon.
        :raises ValueError: When the site can't draw it.
        """
        if not value:
            return ""
        if isinstance(value, str):
            return self.classes(value)
        mine, other = ("pro", "free") if self.kit else ("free", "pro")
        return self.classes(value.get(mine) or value[other])

    def roles(
        self, chosen: Mapping[str, str | Mapping[str, str]]
    ) -> dict[str, str]:
        """Spell out every icon Kaamiki's own parts wear.

        :param chosen: The icons the site set in
            `kaamiki.conf.icons.names`.
        :return: Every icon by its name in `ROLE_ICONS`, the site's own
            where it set one.
        """
        return {
            key: self.custom(chosen[key]) if key in chosen else self.role(key)
            for key in ROLE_ICONS
        }

    def role(self, key: str) -> str:
        """Spell out one of the icons Kaamiki's own parts wear.

        :param key: The icon's name in `ROLE_ICONS`.
        :return: The icon's classes or an empty string for none.
        """
        return self.pair(ROLE_ICONS[key])

    def language(self, language: str | None) -> str:
        """Spell out the icon a language is known by.

        :param language: The language a code block is written in.
        :return: The icon's classes or an empty string for a language
            with none.
        """
        name = (language or "").strip().lower()
        for pair, names in LANGUAGE_ICONS:
            if name in names:
                return self.pair(pair)
        return ""


def _names(listed: str) -> frozenset[str]:
    """Read the names a block of text lists, one space between each."""
    return frozenset(listed.split())


# HACK(xames3): This is possibly a shittiest approach to handle things,
# but for now, I think this'll work without installing and bloating
# the environment and slowing the build times.
FREE_BRANDS: t.Final[frozenset[str]] = _names(
    """
    11ty 42-group 500px a11y-project accessible-icon accusoft adn adversal
    affiliatetheme airbnb algolia alipay amazon amazon-pay amilia android
    angellist angrycreative angular app-store app-store-ios apper apple
    apple-pay arch-linux artstation asymmetrik atlassian audible autoprefixer
    avianex aviato aws bandcamp battle-net behance behance-square bgg bilibili
    bimobject bitbucket bitcoin bity black-tie blackberry blogger blogger-b
    bluesky bluetooth bluetooth-b board-game-geek bootstrap bots brave
    brave-reverse btc buffer build-awesome buromobelexperte buy-n-large
    buysellads canadian-maple-leaf cash-app cc-amazon-pay cc-amex cc-apple-pay
    cc-diners-club cc-discover cc-jcb cc-mastercard cc-paypal cc-stripe
    cc-visa centercode centos chrome chromecast circle-zulip claude cloudflare
    cloudscale cloudsmith cloudversify cmplid codeberg codepen codiepie
    confluence connectdevelop contao copilot cotton-bureau cpanel
    creative-commons creative-commons-by creative-commons-nc
    creative-commons-nc-eu creative-commons-nc-jp creative-commons-nd
    creative-commons-pd creative-commons-pd-alt creative-commons-remix
    creative-commons-sa creative-commons-sampling
    creative-commons-sampling-plus creative-commons-share
    creative-commons-zero critical-role css css3 css3-alt cuttlefish d-and-d
    d-and-d-beyond dailymotion dart-lang dashcube debian deezer delicious
    deploydog deskpro dev deviantart devpost dhl diaspora digg digital-ocean
    discord discourse disqus dochub docker dolibarr draft2digital dribbble
    dribbble-square dropbox drupal duolingo dyalog earlybirds ebay edge
    edge-legacy elementor eleventy ello ember empire envira erlang ethereum
    etsy evernote expeditedssl facebook facebook-f facebook-messenger
    facebook-square fantasy-flight-games fedex fediverse fedora figma
    files-pinwheel firefox firefox-browser first-order first-order-alt
    firstdraft flickr flipboard flutter fly font-awesome font-awesome-alt
    font-awesome-flag font-awesome-logo-full fonticons fonticons-fi forgejo
    fort-awesome fort-awesome-alt forumbee foursquare free-code-camp freebsd
    fulcrum galactic-republic galactic-senate get-pocket gg gg-circle git
    git-alt git-square gitee github github-alt github-square gitkraken gitlab
    gitlab-square gitter glide glide-g globaleaks gofore golang goodreads
    goodreads-g google google-drive google-pay google-play google-plus
    google-plus-g google-plus-square google-scholar google-wallet gratipay
    grav gripfire grunt guilded gulp hacker-news hacker-news-square hackerrank
    hashnode hips hire-a-helper hive hooli hornbill hotjar houzz html5 hubspot
    hugging-face ideal imdb innosoft instagram instagram-square instalod
    intercom internet-archive internet-explorer invision ioxhost itch-io
    itunes itunes-note java jedi-order jenkins jira joget joomla js js-square
    jsfiddle julia jxl kaggle kakao-talk keybase keycdn kickstarter
    kickstarter-k ko-fi korvue kubernetes laravel lastfm lastfm-square leanpub
    leetcode less lets-encrypt letterboxd line linkedin linkedin-in linktree
    linode linux lumon lumon-drop lyft magento mailchimp mandalorian markdown
    mastodon matrix mattermost maxcdn mdb medapps medium medium-m medrt meetup
    megaport mendeley meta microblog microsoft mintbit mix mixcloud mixer
    mizuni modx monero napster neos nextcloud nfc-directional nfc-symbol
    nimblr node node-js notion npm ns8 nutritionix obs-studio obsidian
    octopus-deploy odnoklassniki odnoklassniki-square odysee old-republic
    openai opencart openid openstreetmap opensuse opera optin-monster orcid
    osi padlet page4 pagelines palfed pandora patreon paypal perbyte periscope
    phabricator phoenix-framework phoenix-squadron php pied-piper
    pied-piper-alt pied-piper-hat pied-piper-pp pied-piper-square pinterest
    pinterest-p pinterest-square pix pixelfed pixiv playstation postgresql
    product-hunt pushed python qq quinscape quora r-project raspberry-pi
    ravelry react reacteurope readme rebel red-river reddit reddit-alien
    reddit-square redhat rendact renren replyd researchgate resolving rev
    roblox-creator-studio rocketchat rockrms ror rust safari salesforce sass
    scaleway schlix screenpal scribd searchengin sellcast sellsy servicestack
    shirtsinbulk shoelace shopify shopware signal-messenger simplybuilt
    sistrix sith sitrox sketch skyatlas skype slack slack-hash slideshare
    snapchat snapchat-ghost snapchat-square solana soundcloud sourcetree
    space-awesome speakap speaker-deck spotify square-behance square-bluesky
    square-build-awesome-stroke square-deskpro square-dribbble square-facebook
    square-figma square-font-awesome square-font-awesome-stroke square-git
    square-github square-gitlab square-google-plus square-hacker-news
    square-instagram square-js square-kickstarter square-lastfm
    square-letterboxd square-linkedin square-odnoklassniki square-pied-piper
    square-pinterest square-reddit square-snapchat square-steam square-threads
    square-tumblr square-twitter square-upwork square-viadeo square-vimeo
    square-web-awesome square-web-awesome-stroke square-whatsapp
    square-x-twitter square-xing square-youtube squarespace stack-exchange
    stack-overflow stackpath staylinked steam steam-square steam-symbol
    sticker-mule storybook strava stripe stripe-s stubber studiovinari
    stumbleupon stumbleupon-circle substack superpowers supple supportnow suse
    svelte swift symfony symfonycasts tailwind-css teamspeak telegram
    telegram-plane tencent-weibo tesla tex the-red-yeti themeco themeisle
    think-peaks threads threema tidal tiktok tor-browser trade-federation
    trello tumblr tumblr-square twitch twitter twitter-square typescript typo3
    uber ubuntu uikit ultralytics ultralytics-hub ultralytics-yolo umbraco
    uncharted uniregistry unison unity unreal-engine unsplash untappd ups
    upwork usb usps ussunnah vaadin venmo venmo-v viacoin viadeo viadeo-square
    viber vim vimeo vimeo-square vimeo-v vine visual-studio vk vnv vsco vuejs
    w3c watchman-monitoring waze web-awesome webflow weebly weibo weixin
    whatsapp whatsapp-square whmcs wikipedia-w windows wirsindhandwerk wix
    wizards-of-the-coast wodu wolf-pack-battalion wordpress wordpress-simple
    wpbeginner wpexplorer wpforms wpressr wsh x-twitter xbox xing xing-square
    xmpp xrp xrpl y-combinator yahoo yammer yandex yandex-international yarn
    yelp yoast youtube youtube-shorts youtube-square zhihu zoom zulip
    """
)
FREE_REGULAR: t.Final[frozenset[str]] = _names(
    """
    address-book address-card alarm-clock angry arrow-alt-circle-down
    arrow-alt-circle-left arrow-alt-circle-right arrow-alt-circle-up bar-chart
    bell bell-slash bookmark building calendar calendar-alt calendar-check
    calendar-days calendar-minus calendar-plus calendar-times calendar-xmark
    camera camera-alt caret-square-down caret-square-left caret-square-right
    caret-square-up chart-bar check-circle check-square chess-bishop
    chess-king chess-knight chess-pawn chess-queen chess-rook circle
    circle-check circle-dot circle-down circle-left circle-pause circle-play
    circle-question circle-right circle-stop circle-up circle-user
    circle-xmark clipboard clock clock-four clone closed-captioning cloud
    comment comment-alt comment-dots commenting comments compass contact-book
    contact-card copy copyright credit-card credit-card-alt dizzy dot-circle
    drivers-license edit envelope envelope-open eye eye-slash face-angry
    face-dizzy face-flushed face-frown face-frown-open face-grimace face-grin
    face-grin-beam face-grin-beam-sweat face-grin-hearts face-grin-squint
    face-grin-squint-tears face-grin-stars face-grin-tears face-grin-tongue
    face-grin-tongue-squint face-grin-tongue-wink face-grin-wide
    face-grin-wink face-kiss face-kiss-beam face-kiss-wink-heart face-laugh
    face-laugh-beam face-laugh-squint face-laugh-wink face-meh face-meh-blank
    face-rolling-eyes face-sad-cry face-sad-tear face-smile face-smile-beam
    face-smile-wink face-surprise face-tired file file-alt file-archive
    file-audio file-clipboard file-code file-excel file-image file-lines
    file-pdf file-powerpoint file-text file-video file-word file-zipper flag
    floppy-disk flushed folder folder-blank folder-closed folder-open
    font-awesome font-awesome-flag font-awesome-logo-full frown frown-open
    futbol futbol-ball gem grimace grin grin-alt grin-beam grin-beam-sweat
    grin-hearts grin-squint grin-squint-tears grin-stars grin-tears
    grin-tongue grin-tongue-squint grin-tongue-wink grin-wink hand
    hand-back-fist hand-lizard hand-paper hand-peace hand-point-down
    hand-point-left hand-point-right hand-point-up hand-pointer hand-rock
    hand-scissors hand-spock handshake handshake-alt handshake-simple
    hard-drive hdd headphones headphones-alt headphones-simple heart home
    home-alt home-lg-alt hospital hospital-alt hospital-wide hourglass
    hourglass-2 hourglass-empty hourglass-half house id-badge id-card image
    images keyboard kiss kiss-beam kiss-wink-heart laugh laugh-beam
    laugh-squint laugh-wink lemon life-ring lightbulb list-alt map meh
    meh-blank meh-rolling-eyes message minus-square money-bill-1
    money-bill-alt moon newspaper note-sticky object-group object-ungroup
    paper-plane paste pause-circle pen-to-square play-circle plus-square
    question-circle rectangle-list rectangle-times rectangle-xmark registered
    sad-cry sad-tear save share-from-square share-square smile smile-beam
    smile-wink snowflake soccer-ball square square-caret-down
    square-caret-left square-caret-right square-caret-up square-check
    square-full square-minus square-plus star star-half star-half-alt
    star-half-stroke sticky-note stop-circle sun surprise thumbs-down
    thumbs-up times-circle times-rectangle tired trash-alt trash-can truck
    user user-alt user-circle user-large vcard window-close window-maximize
    window-minimize window-restore xmark-circle
    """
)
FREE_SOLID: t.Final[frozenset[str]] = _names(
    """
    0 1 2 3 4 5 6 7 8 9
    a ad add address-book address-card adjust air-freshener alarm-clock
    align-center align-justify align-left align-right allergies ambulance
    american-sign-language-interpreting anchor anchor-circle-check
    anchor-circle-exclamation anchor-circle-xmark anchor-lock
    angle-double-down angle-double-left angle-double-right angle-double-up
    angle-down angle-left angle-right angle-up angles-down angles-left
    angles-right angles-up angry ankh apple-alt apple-whole aquarius archive
    archway area-chart aries arrow-alt-circle-down arrow-alt-circle-left
    arrow-alt-circle-right arrow-alt-circle-up arrow-circle-down
    arrow-circle-left arrow-circle-right arrow-circle-up arrow-down
    arrow-down-1-9 arrow-down-9-1 arrow-down-a-z arrow-down-long
    arrow-down-short-wide arrow-down-up-across-line arrow-down-up-lock
    arrow-down-wide-short arrow-down-z-a arrow-left arrow-left-long
    arrow-left-rotate arrow-pointer arrow-right arrow-right-arrow-left
    arrow-right-from-bracket arrow-right-from-file arrow-right-long
    arrow-right-rotate arrow-right-to-bracket arrow-right-to-city
    arrow-right-to-file arrow-rotate-back arrow-rotate-backward
    arrow-rotate-forward arrow-rotate-left arrow-rotate-right arrow-trend-down
    arrow-trend-up arrow-turn-down arrow-turn-up arrow-up arrow-up-1-9
    arrow-up-9-1 arrow-up-a-z arrow-up-from-bracket arrow-up-from-ground-water
    arrow-up-from-water-pump arrow-up-long arrow-up-right-dots
    arrow-up-right-from-square arrow-up-short-wide arrow-up-wide-short
    arrow-up-z-a arrows arrows-alt arrows-alt-h arrows-alt-v
    arrows-down-to-line arrows-down-to-people arrows-h arrows-left-right
    arrows-left-right-to-line arrows-rotate arrows-spin
    arrows-split-up-and-left arrows-to-circle arrows-to-dot arrows-to-eye
    arrows-turn-right arrows-turn-to-dots arrows-up-down
    arrows-up-down-left-right arrows-up-to-line arrows-v asl-interpreting
    assistive-listening-systems asterisk at atlas atom audio-description
    austral-sign automobile award b baby baby-carriage backspace backward
    backward-fast backward-step bacon bacteria bacterium bag-shopping bahai
    baht-sign balance-scale balance-scale-left balance-scale-right ban
    ban-smoking band-aid bandage bangladeshi-taka-sign bank bar-chart barcode
    bars bars-progress bars-staggered baseball baseball-ball baseball-bat-ball
    basket-shopping basketball basketball-ball bath bathtub battery battery-0
    battery-2 battery-3 battery-4 battery-5 battery-car battery-empty
    battery-full battery-half battery-quarter battery-three-quarters bed
    bed-pulse beer beer-mug-empty bell bell-concierge bell-slash bezier-curve
    bible bicycle biking binoculars biohazard birthday-cake bitcoin-sign
    blackboard blender blender-phone blind blog bold bolt bolt-lightning bomb
    bone bong book book-atlas book-bible book-bookmark book-dead
    book-journal-whills book-medical book-open book-open-reader book-quran
    book-reader book-skull book-tanakh bookmark border-all border-none
    border-style border-top-left bore-hole bottle-droplet bottle-water
    bowl-food bowl-rice bowling-ball box box-archive box-open box-tissue boxes
    boxes-alt boxes-packing boxes-stacked braille brain brazilian-real-sign
    bread-slice bridge bridge-circle-check bridge-circle-exclamation
    bridge-circle-xmark bridge-lock bridge-water briefcase briefcase-clock
    briefcase-medical broadcast-tower broom broom-ball brush bucket bug
    bug-slash bugs building building-circle-arrow-right building-circle-check
    building-circle-exclamation building-circle-xmark building-columns
    building-flag building-lock building-ngo building-shield building-un
    building-user building-wheat bullhorn bullseye burger burn burst bus
    bus-alt bus-side bus-simple business-time c cab cable-car cake
    cake-candles calculator calendar calendar-alt calendar-check calendar-day
    calendar-days calendar-minus calendar-plus calendar-times calendar-week
    calendar-xmark camera camera-alt camera-retro camera-rotate campground
    cancel cancer candy-cane cannabis capricorn capsules car car-alt
    car-battery car-burst car-crash car-on car-rear car-side car-tunnel
    caravan caret-down caret-left caret-right caret-square-down
    caret-square-left caret-square-right caret-square-up caret-up
    carriage-baby carrot cart-arrow-down cart-flatbed cart-flatbed-suitcase
    cart-plus cart-shopping cash-register cat cedi-sign cent-sign certificate
    chain chain-broken chain-slash chair chalkboard chalkboard-teacher
    chalkboard-user champagne-glasses charging-station chart-area chart-bar
    chart-column chart-diagram chart-gantt chart-line chart-pie chart-simple
    check check-circle check-double check-square check-to-slot cheese chess
    chess-bishop chess-board chess-king chess-knight chess-pawn chess-queen
    chess-rook chevron-circle-down chevron-circle-left chevron-circle-right
    chevron-circle-up chevron-down chevron-left chevron-right chevron-up child
    child-combatant child-dress child-reaching child-rifle children church
    circle circle-arrow-down circle-arrow-left circle-arrow-right
    circle-arrow-up circle-check circle-chevron-down circle-chevron-left
    circle-chevron-right circle-chevron-up circle-dollar-to-slot circle-dot
    circle-down circle-exclamation circle-h circle-half-stroke circle-info
    circle-left circle-minus circle-nodes circle-notch circle-pause
    circle-play circle-plus circle-question circle-radiation circle-right
    circle-stop circle-up circle-user circle-xmark city clapperboard
    clinic-medical clipboard clipboard-check clipboard-list clipboard-question
    clipboard-user clock clock-four clock-rotate-left clone close
    closed-captioning closed-captioning-slash cloud cloud-arrow-down
    cloud-arrow-up cloud-bolt cloud-download cloud-download-alt cloud-meatball
    cloud-moon cloud-moon-rain cloud-rain cloud-showers-heavy
    cloud-showers-water cloud-sun cloud-sun-rain cloud-upload cloud-upload-alt
    clover cny cocktail code code-branch code-commit code-compare code-fork
    code-merge code-pull-request coffee cog cogs coins colon-sign columns
    comment comment-alt comment-dollar comment-dots comment-medical
    comment-nodes comment-slash comment-sms commenting comments
    comments-dollar compact-disc compass compass-drafting compress
    compress-alt compress-arrows-alt computer computer-mouse concierge-bell
    contact-book contact-card cookie cookie-bite copy copyright couch cow
    credit-card credit-card-alt crop crop-alt crop-simple cross crosshairs
    crow crown crutch cruzeiro-sign cube cubes cubes-stacked cut cutlery d
    dashboard database deaf deafness dedent delete-left democrat desktop
    desktop-alt dharmachakra diagnoses diagram-next diagram-predecessor
    diagram-project diagram-successor diamond diamond-turn-right dice dice-d20
    dice-d6 dice-five dice-four dice-one dice-six dice-three dice-two digging
    digital-tachograph directions disease display divide dizzy dna dog dollar
    dollar-sign dolly dolly-box dolly-flatbed donate dong-sign door-closed
    door-open dot-circle dove down-left-and-up-right-to-center down-long
    download drafting-compass dragon draw-polygon drivers-license droplet
    droplet-slash drum drum-steelpan drumstick-bite dumbbell dumpster
    dumpster-fire dungeon e ear-deaf ear-listen earth earth-africa
    earth-america earth-americas earth-asia earth-europe earth-oceania edit
    egg eject elevator ellipsis ellipsis-h ellipsis-v ellipsis-vertical
    envelope envelope-circle-check envelope-open envelope-open-text
    envelope-square envelopes-bulk equals eraser ethernet eur euro euro-sign
    exchange exchange-alt exclamation exclamation-circle exclamation-triangle
    expand expand-alt expand-arrows-alt explosion external-link
    external-link-alt external-link-square external-link-square-alt eye
    eye-dropper eye-dropper-empty eye-low-vision eye-slash eyedropper f
    face-angry face-dizzy face-flushed face-frown face-frown-open face-grimace
    face-grin face-grin-beam face-grin-beam-sweat face-grin-hearts
    face-grin-squint face-grin-squint-tears face-grin-stars face-grin-tears
    face-grin-tongue face-grin-tongue-squint face-grin-tongue-wink
    face-grin-wide face-grin-wink face-kiss face-kiss-beam
    face-kiss-wink-heart face-laugh face-laugh-beam face-laugh-squint
    face-laugh-wink face-meh face-meh-blank face-rolling-eyes face-sad-cry
    face-sad-tear face-smile face-smile-beam face-smile-wink face-surprise
    face-tired fan fast-backward fast-forward faucet faucet-drip fax feather
    feather-alt feather-pointed feed female ferry fighter-jet file file-alt
    file-archive file-arrow-down file-arrow-up file-audio file-circle-check
    file-circle-exclamation file-circle-minus file-circle-plus
    file-circle-question file-circle-xmark file-clipboard file-code
    file-contract file-csv file-download file-edit file-excel file-export
    file-fragment file-half-dashed file-image file-import file-invoice
    file-invoice-dollar file-lines file-medical file-medical-alt file-pdf
    file-pen file-powerpoint file-prescription file-shield file-signature
    file-text file-upload file-video file-waveform file-word file-zipper fill
    fill-drip film film-alt film-simple filter filter-circle-dollar
    filter-circle-xmark fingerprint fire fire-alt fire-burner
    fire-extinguisher fire-flame-curved fire-flame-simple first-aid fish
    fish-fins fist-raised flag flag-checkered flag-usa flask flask-vial
    floppy-disk florin-sign flushed folder folder-blank folder-closed
    folder-minus folder-open folder-plus folder-tree font font-awesome
    font-awesome-flag font-awesome-logo-full football football-ball forward
    forward-fast forward-step franc-sign frog frown frown-open funnel-dollar
    futbol futbol-ball g gamepad gas-pump gauge gauge-high gauge-med
    gauge-simple gauge-simple-high gauge-simple-med gavel gbp gear gears gem
    gemini genderless ghost gift gifts glass-cheers glass-martini
    glass-martini-alt glass-water glass-water-droplet glass-whiskey glasses
    globe globe-africa globe-americas globe-asia globe-europe globe-oceania
    golf-ball golf-ball-tee gopuram graduation-cap greater-than
    greater-than-equal grid-horizontal grid-vertical grimace grin grin-alt
    grin-beam grin-beam-sweat grin-hearts grin-squint grin-squint-tears
    grin-stars grin-tears grin-tongue grin-tongue-squint grin-tongue-wink
    grin-wink grip grip-horizontal grip-lines grip-lines-vertical
    grip-vertical group-arrows-rotate guarani-sign guitar gun h h-square
    hamburger hammer hamsa hand hand-back-fist hand-dots hand-fist
    hand-holding hand-holding-dollar hand-holding-droplet hand-holding-hand
    hand-holding-heart hand-holding-medical hand-holding-usd
    hand-holding-water hand-lizard hand-middle-finger hand-paper hand-peace
    hand-point-down hand-point-left hand-point-right hand-point-up
    hand-pointer hand-rock hand-scissors hand-sparkles hand-spock handcuffs
    hands hands-american-sign-language-interpreting hands-asl-interpreting
    hands-bound hands-bubbles hands-clapping hands-helping hands-holding
    hands-holding-child hands-holding-circle hands-praying hands-wash
    handshake handshake-alt handshake-alt-slash handshake-angle
    handshake-simple handshake-simple-slash handshake-slash hanukiah
    hard-drive hard-hat hard-of-hearing hashtag hat-cowboy hat-cowboy-side
    hat-hard hat-wizard haykal hdd head-side-cough head-side-cough-slash
    head-side-mask head-side-virus header heading headphones headphones-alt
    headphones-simple headset heart heart-broken heart-circle-bolt
    heart-circle-check heart-circle-exclamation heart-circle-minus
    heart-circle-plus heart-circle-xmark heart-crack heart-music-camera-bolt
    heart-pulse heartbeat helicopter helicopter-symbol helmet-safety helmet-un
    heptagon hexagon hexagon-nodes hexagon-nodes-bolt highlighter hiking
    hill-avalanche hill-rockslide hippo history hockey-puck holly-berry home
    home-alt home-lg home-lg-alt home-user horse horse-head hospital
    hospital-alt hospital-symbol hospital-user hospital-wide hot-tub
    hot-tub-person hotdog hotel hourglass hourglass-1 hourglass-2 hourglass-3
    hourglass-empty hourglass-end hourglass-half hourglass-start house
    house-chimney house-chimney-crack house-chimney-medical house-chimney-user
    house-chimney-window house-circle-check house-circle-exclamation
    house-circle-xmark house-crack house-damage house-fire house-flag
    house-flood-water house-flood-water-circle-arrow-right house-laptop
    house-lock house-medical house-medical-circle-check
    house-medical-circle-exclamation house-medical-circle-xmark
    house-medical-flag house-signal house-tsunami house-user hryvnia
    hryvnia-sign hurricane i i-cursor ice-cream icicles icons id-badge id-card
    id-card-alt id-card-clip igloo ils image image-portrait images inbox
    indent indian-rupee indian-rupee-sign industry infinity info info-circle
    inr institution italic j jar jar-wheat jedi jet-fighter jet-fighter-up
    joint journal-whills jpy jug-detergent k kaaba key keyboard khanda
    kip-sign kiss kiss-beam kiss-wink-heart kit-medical kitchen-set kiwi-bird
    krw l ladder-water land-mine-on landmark landmark-alt landmark-dome
    landmark-flag language laptop laptop-code laptop-file laptop-house
    laptop-medical lari-sign laugh laugh-beam laugh-squint laugh-wink
    layer-group leaf left-long left-right legal lemon leo less-than
    less-than-equal level-down level-down-alt level-up level-up-alt libra
    life-ring lightbulb line-chart lines-leaning link link-slash lira-sign
    list list-1-2 list-alt list-check list-dots list-numeric list-ol
    list-squares list-ul litecoin-sign location location-arrow
    location-crosshairs location-dot location-pin location-pin-lock lock
    lock-open locust long-arrow-alt-down long-arrow-alt-left
    long-arrow-alt-right long-arrow-alt-up long-arrow-down long-arrow-left
    long-arrow-right long-arrow-up lotus low-vision luggage-cart lungs
    lungs-virus m magic magic-wand-sparkles magnet magnifying-glass
    magnifying-glass-arrow-right magnifying-glass-chart
    magnifying-glass-dollar magnifying-glass-location magnifying-glass-minus
    magnifying-glass-plus mail-bulk mail-forward mail-reply mail-reply-all
    male manat-sign map map-location map-location-dot map-marked
    map-marked-alt map-marker map-marker-alt map-pin map-signs marker mars
    mars-and-venus mars-and-venus-burst mars-double mars-stroke mars-stroke-h
    mars-stroke-right mars-stroke-up mars-stroke-v martini-glass
    martini-glass-citrus martini-glass-empty mask mask-face mask-ventilator
    masks-theater mattress-pillow maximize medal medkit meh meh-blank
    meh-rolling-eyes memory menorah mercury message meteor microchip
    microphone microphone-alt microphone-alt-slash microphone-lines
    microphone-lines-slash microphone-slash microscope mill-sign minimize
    minus minus-circle minus-square mitten mobile mobile-alt mobile-android
    mobile-android-alt mobile-button mobile-phone mobile-retro mobile-screen
    mobile-screen-button mobile-vibrate money-bill money-bill-1
    money-bill-1-wave money-bill-alt money-bill-transfer money-bill-trend-up
    money-bill-wave money-bill-wave-alt money-bill-wheat money-bills
    money-check money-check-alt money-check-dollar monument moon mortar-board
    mortar-pestle mosque mosquito mosquito-net motorcycle mound mountain
    mountain-city mountain-sun mouse mouse-pointer mug-hot mug-saucer multiply
    museum music n naira-sign navicon network-wired neuter newspaper
    non-binary not-equal notdef note-sticky notes-medical o object-group
    object-ungroup octagon oil-can oil-well om otter outdent p pager
    paint-brush paint-roller paintbrush palette pallet panorama paper-plane
    paperclip parachute-box paragraph parking passport pastafarianism paste
    pause pause-circle paw peace pen pen-alt pen-clip pen-fancy pen-nib
    pen-ruler pen-square pen-to-square pencil pencil-alt pencil-ruler
    pencil-square pentagon people-arrows people-arrows-left-right people-carry
    people-carry-box people-group people-line people-pulling people-robbery
    people-roof pepper-hot percent percentage person person-arrow-down-to-line
    person-arrow-up-from-line person-biking person-booth person-breastfeeding
    person-burst person-cane person-chalkboard person-circle-check
    person-circle-exclamation person-circle-minus person-circle-plus
    person-circle-question person-circle-xmark person-digging
    person-dots-from-line person-dress person-dress-burst person-drowning
    person-falling person-falling-burst person-half-dress person-harassing
    person-hiking person-military-pointing person-military-rifle
    person-military-to-person person-praying person-pregnant person-rays
    person-rifle person-running person-shelter person-skating person-skiing
    person-skiing-nordic person-snowboarding person-swimming
    person-through-window person-walking person-walking-arrow-loop-left
    person-walking-arrow-right person-walking-dashed-line-arrow-right
    person-walking-luggage person-walking-with-cane peseta-sign peso-sign
    phone phone-alt phone-flip phone-slash phone-square phone-square-alt
    phone-volume photo-film photo-video picture-in-picture pie-chart
    piggy-bank pills ping-pong-paddle-ball pisces pizza-slice place-of-worship
    plane plane-arrival plane-circle-check plane-circle-exclamation
    plane-circle-xmark plane-departure plane-lock plane-slash plane-up
    plant-wilt plate-wheat play play-circle plug plug-circle-bolt
    plug-circle-check plug-circle-exclamation plug-circle-minus
    plug-circle-plus plug-circle-xmark plus plus-circle plus-minus plus-square
    podcast poll poll-h poo poo-bolt poo-storm poop portrait pound-sign
    power-off pray praying-hands prescription prescription-bottle
    prescription-bottle-alt prescription-bottle-medical print procedures
    project-diagram pump-medical pump-soap puzzle-piece q qrcode question
    question-circle quidditch quidditch-broom-ball quote-left quote-left-alt
    quote-right quote-right-alt quran r radiation radiation-alt radio rainbow
    random ranking-star receipt record-vinyl rectangle-ad rectangle-list
    rectangle-times rectangle-xmark recycle redo redo-alt refresh registered
    remove remove-format reorder repeat reply reply-all republican restroom
    retweet ribbon right-from-bracket right-left right-long right-to-bracket
    ring rmb road road-barrier road-bridge road-circle-check
    road-circle-exclamation road-circle-xmark road-lock road-spikes robot
    rocket rod-asclepius rod-snake rotate rotate-back rotate-backward
    rotate-forward rotate-left rotate-right rouble route rss rss-square rub
    ruble ruble-sign rug ruler ruler-combined ruler-horizontal ruler-vertical
    running rupee rupee-sign rupiah-sign s sack-dollar sack-xmark sad-cry
    sad-tear sagittarius sailboat satellite satellite-dish save scale-balanced
    scale-unbalanced scale-unbalanced-flip school school-circle-check
    school-circle-exclamation school-circle-xmark school-flag school-lock
    scissors scorpio screwdriver screwdriver-wrench scroll scroll-torah
    sd-card search search-dollar search-location search-minus search-plus
    section seedling septagon server shapes share share-alt share-alt-square
    share-from-square share-nodes share-square sheet-plastic shekel
    shekel-sign sheqel sheqel-sign shield shield-alt shield-blank shield-cat
    shield-dog shield-halved shield-heart shield-virus ship shipping-fast
    shirt shoe-prints shop shop-lock shop-slash shopping-bag shopping-basket
    shopping-cart shower shrimp shuffle shuttle-space shuttle-van sign
    sign-hanging sign-in sign-in-alt sign-language sign-out sign-out-alt
    signal signal-5 signal-perfect signature signing signs-post sim-card
    single-quote-left single-quote-right sink sitemap skating skiing
    skiing-nordic skull skull-crossbones slash sleigh sliders sliders-h smile
    smile-beam smile-wink smog smoking smoking-ban sms snowboarding snowflake
    snowman snowplow soap soccer-ball socks solar-panel sort sort-alpha-asc
    sort-alpha-desc sort-alpha-down sort-alpha-down-alt sort-alpha-up
    sort-alpha-up-alt sort-amount-asc sort-amount-desc sort-amount-down
    sort-amount-down-alt sort-amount-up sort-amount-up-alt sort-asc sort-desc
    sort-down sort-numeric-asc sort-numeric-desc sort-numeric-down
    sort-numeric-down-alt sort-numeric-up sort-numeric-up-alt sort-up spa
    space-shuttle spaghetti-monster-flying spell-check spider spinner spiral
    splotch spoon spray-can spray-can-sparkles sprout square
    square-arrow-up-right square-binary square-caret-down square-caret-left
    square-caret-right square-caret-up square-check square-envelope
    square-full square-h square-minus square-nfi square-parking square-pen
    square-person-confined square-phone square-phone-flip square-plus
    square-poll-horizontal square-poll-vertical square-root-alt
    square-root-variable square-rss square-share-nodes square-up-right
    square-virus square-xmark staff-aesculapius staff-snake stairs stamp
    stapler star star-and-crescent star-half star-half-alt star-half-stroke
    star-of-david star-of-life step-backward step-forward sterling-sign
    stethoscope sticky-note stop stop-circle stopwatch stopwatch-20 store
    store-alt store-alt-slash store-slash stream street-view strikethrough
    stroopwafel subscript subtract subway suitcase suitcase-medical
    suitcase-rolling sun sun-plant-wilt superscript surprise swatchbook
    swimmer swimming-pool synagogue sync sync-alt syringe t t-shirt table
    table-cells table-cells-column-lock table-cells-large table-cells-row-lock
    table-cells-row-unlock table-columns table-list table-tennis
    table-tennis-paddle-ball tablet tablet-alt tablet-android tablet-button
    tablet-screen-button tablets tachograph-digital tachometer tachometer-alt
    tachometer-alt-average tachometer-alt-fast tachometer-average
    tachometer-fast tag tags tanakh tape tarp tarp-droplet tasks tasks-alt
    taurus taxi teeth teeth-open teletype television temperature-0
    temperature-1 temperature-2 temperature-3 temperature-4
    temperature-arrow-down temperature-arrow-up temperature-down
    temperature-empty temperature-full temperature-half temperature-high
    temperature-low temperature-quarter temperature-three-quarters
    temperature-up tenge tenge-sign tent tent-arrow-down-to-line
    tent-arrow-left-right tent-arrow-turn-left tent-arrows-down tents terminal
    text-height text-slash text-width th th-large th-list theater-masks
    thermometer thermometer-0 thermometer-1 thermometer-2 thermometer-3
    thermometer-4 thermometer-empty thermometer-full thermometer-half
    thermometer-quarter thermometer-three-quarters thumb-tack thumb-tack-slash
    thumbs-down thumbs-up thumbtack thumbtack-slash thunderstorm ticket
    ticket-alt ticket-simple timeline times times-circle times-rectangle
    times-square tint tint-slash tired toggle-off toggle-on toilet
    toilet-paper toilet-paper-alt toilet-paper-blank toilet-paper-slash
    toilet-portable toilets-portable toolbox tools tooth torah torii-gate
    tornado tower-broadcast tower-cell tower-observation tractor trademark
    traffic-light trailer train train-subway train-tram tram transgender
    transgender-alt trash trash-alt trash-arrow-up trash-can
    trash-can-arrow-up trash-restore trash-restore-alt tree tree-city
    triangle-circle-square triangle-exclamation trophy trowel trowel-bricks
    truck truck-arrow-right truck-droplet truck-fast truck-field
    truck-field-un truck-front truck-loading truck-medical truck-monster
    truck-moving truck-pickup truck-plane truck-ramp-box try tshirt tty
    turkish-lira turkish-lira-sign turn-down turn-up tv tv-alt u umbrella
    umbrella-beach underline undo undo-alt universal-access university unlink
    unlock unlock-alt unlock-keyhole unsorted up-down up-down-left-right
    up-long up-right-and-down-left-from-center up-right-from-square upload usd
    user user-alt user-alt-slash user-astronaut user-check user-circle
    user-clock user-cog user-doctor user-edit user-friends user-gear
    user-graduate user-group user-injured user-large user-large-slash
    user-lock user-md user-minus user-ninja user-nurse user-pen user-plus
    user-secret user-shield user-slash user-tag user-tie user-times user-xmark
    users users-between-lines users-cog users-gear users-line users-rays
    users-rectangle users-slash users-viewfinder utensil-spoon utensils v
    van-shuttle vault vcard vector-polygon venus venus-double venus-mars vest
    vest-patches vial vial-circle-check vial-virus vials video video-camera
    video-slash vihara virgo virus virus-covid virus-covid-slash virus-slash
    viruses voicemail volcano volleyball volleyball-ball volume
    volume-control-phone volume-down volume-high volume-low volume-medium
    volume-mute volume-off volume-times volume-up volume-xmark vote-yea
    vr-cardboard w walkie-talkie walking wallet wand-magic wand-magic-sparkles
    wand-sparkles warehouse warning water water-ladder wave-square web-awesome
    weight weight-hanging weight-scale wheat-alt wheat-awn
    wheat-awn-circle-exclamation wheelchair wheelchair-alt wheelchair-move
    whiskey-glass wifi wifi-3 wifi-strong wind window-close window-maximize
    window-minimize window-restore wine-bottle wine-glass wine-glass-alt
    wine-glass-empty won won-sign worm wrench x x-ray xmark xmark-circle
    xmark-square xmarks-lines y yen yen-sign yin-yang z zap
    """
)
FREE_STYLES: t.Final[Mapping[str, frozenset[str]]] = MappingProxyType(
    {"regular": FREE_REGULAR, "solid": FREE_SOLID}
)
