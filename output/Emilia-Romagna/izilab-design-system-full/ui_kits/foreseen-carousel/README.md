# UI Kit — Foreseen Carousel

An interactive recreation of IZILab's **social carousel** system (the "Foreseen"
editorial format), the most fully-specified product surface in the supplied
materials (`uploads/social-carousel.png`).

It is a click-through **carousel viewer**: a 4:5 social card on a stage with
prev/next controls, page dots, a numbered counter and a thumbnail rail. Use
←/→ keys or the arrows to navigate; click any thumbnail or dot to jump.

## Files
- `index.html` — entry. Loads `styles.css`, React/Babel, the DS bundle, then the
  app scripts. Tagged as a **starting point** (`section="Social"`).
- `data.js` — slide data (real copy from the IZILab system), on `window.IZI_FORESEEN`.
- `CarouselSlide.jsx` — one faithful 4:5 slide (cover + content layouts, dark/light).
- `App.jsx` — the viewer chrome, composing DS components.

## Components used
`IconButton` (nav), `Button` (Modifica / Pubblica), `Badge` ("Carousel").
The slide body is a bespoke brand layout built directly on tokens.

## Fidelity notes
- Slide structure follows the reference exactly: `logo (top-right) → kicker
  (numbered, uppercase) → title (Cirka/Domine) → short aqua rule → body
  (Instrument Sans) → forward arrow`.
- Per-mode color from the spec: dark slides use violet-300 kicker / aqua-200
  title / blanche-400 body on deep violet or aurora bg; light slides use
  blanche-800 kicker / violet-600 title / blanche-900 body on near-white.
- The logo sits in a protective white chip on image/dark backgrounds.

No dashboard or other product screens were provided, so only the documented
carousel surface is recreated here (rather than inventing new screens).
