# CCreations

The website of CCreations (Joris Schets): custom systems for SMEs, and the brand board that documents the identity.

It is a static site with no build step and no runtime dependencies: semantic HTML, one stylesheet, two small JavaScript modules.

## Run it

Any static file server works. The pages load an SVG sprite and ES modules, which browsers refuse over `file://`, so opening `index.html` directly from disk will not work.

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

## Structure

```
index.html              Home page
merk.html               Brand board: logos, colours, type, components, social templates
css/site.css            All styles; design tokens live in :root
js/site.js              Language switch, mobile menu, contact form, wave graphic
js/translations.js      French, Spanish and English strings
assets/sprite.svg       Logo and icons, referenced with <use>
assets/fonts/           Self-hosted fonts (Latin subset)
assets/brand/           Generated logo files and social templates
assets/screens/         Rendered images of the rebuilt app screens
tools/build_brand.py    Generates everything in assets/brand/
tools/screens/          HTML sources of the rebuilt app screens
tools/render_screens.py Renders those sources to assets/screens/
```

## How things work

**Design tokens.** Colours, fonts, borders, radius and spacing are custom properties in the `:root` block at the top of `css/site.css`. The brand board reads the same tokens, so it cannot drift from the site.

**Languages.** Dutch is written in the HTML and is the source of truth. Elements carry a `data-i18n="key"` attribute; `js/site.js` reads the Dutch text from the page once and swaps in the French, Spanish or English string from `js/translations.js`. Attributes are translated with `data-i18n-placeholder`, `data-i18n-alt`, `data-i18n-aria-label` and `data-i18n-content`. On a first visit the site follows the browser's language; visitors whose language is not offered get English, and a choice made with the language switch is remembered. To add a string: write it in Dutch in the HTML with a new key, then add that key to every language in `js/translations.js`.

**Contact form.** The form sends nothing itself. It opens a draft in the visitor's own email app. The receiving address is `CONTACT_EMAIL` at the top of `js/site.js`. The intake button next to it links to a Google Calendar booking page; nothing loads from Google unless a visitor clicks it.

**Brand files.** The logos and social templates are generated, with all text converted to outlines. After changing a colour, a font or the monogram, regenerate them:

```sh
pip install fonttools brotli uharfbuzz
python3 tools/build_brand.py
```

The same script writes `assets/favicon.svg`. The PNG files (`favicon-32.png`, `apple-touch-icon.png` and `brand/social-avatar.png`) were rasterised from the generated SVGs once and need redoing by hand if the monogram changes.

**Project screens.** Each screen in the Projects section is an HTML page in `tools/screens/`, rendered to an image. After editing one:

```sh
pip install playwright pillow
python3 tools/render_screens.py
```

## Checks

The only Node dependencies are linters.

```sh
npm install
npm run lint
```

## Privacy

- No analytics, no cookies, no third-party requests. Fonts are served from this repository.
- The language choice is kept in the browser's `localStorage` and nowhere else.
- The project screens are not screenshots. They are rebuilt by hand from the real applications, in their real layout, with fictional data, and the site says so under each one. Real screenshots with client data must never be committed.

## Known limitation

Translations are applied in the browser, so search engines index the Dutch text only. Separate pages per language would need a build step, which this site deliberately avoids.

## Licence

The code (HTML, CSS, JavaScript, Python) is released under the MIT licence, see `LICENSE`.

Not covered by that licence, all rights reserved: the CCreations name and logo, everything in `assets/brand/`, the texts, the illustrations and the screenshots.

The fonts in `assets/fonts/` are Bai Jamjuree, Roboto and Roboto Condensed, each under the SIL Open Font License 1.1.
