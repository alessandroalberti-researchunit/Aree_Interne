---
name: izilab-design
description: Use this skill to generate well-branded interfaces and assets for IZILab, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

# IZILab — Sistema visivo

IZILab is a research & foresight lab. Visual system is **digital-first** with
**Light / Dark** modes. Payoff: *"Il futuro non si aspetta, si anticipa."*

Read **`readme.md`** for the full guide (content fundamentals, visual
foundations, iconography, index), then explore the other files.

## Quick reference
- **Primary** Violet/500 `#6422E8` · **Accent** Aqua/500 `#49E1C0` · **Neutral**
  Blanche/500 `#ECEBFE`. (Do **not** use `#6E54E8` — it's a refuso.)
- **Brand gradient** `linear-gradient(135deg, #6422E8 0%, #49E1C0 100%)`.
- **Type** — Display/titoli: Cirka → **Domine** fallback (serif, sentence case).
  Body/kicker/CTA: **Instrument Sans**. Numbers/data/tables: **Chivo Mono** (always).
- **Default** dark mode; light for documents. Tokens differ per mode.
- **Style** — abstract geometric icons (not classic glyphs); violet↔aqua gradients;
  high contrast; aurora/grain backgrounds + fine technical line overlays; crisp
  geometry; glows on dark, soft shadows on light; restrained ease-out motion.

## How to use
- Link **`styles.css`** to inherit all tokens + fonts.
- Components are bundled at **`_ds_bundle.js`** and read from
  `window.IZILabDesignSystem_03588f` (e.g. `const { Button, Card } = window.IZILabDesignSystem_03588f`).
  Component sources live in `components/<group>/`.
- Assets in `assets/` (logo, abstract icons, aurora backgrounds).
- See `guidelines/` for foundation specimens, `ui_kits/foreseen-carousel/` for the
  product surface recreation, and `slides/` for presentation templates.

If creating visual artifacts (slides, mocks, throwaway prototypes), copy assets
out and produce static HTML files for the user to view. For production code, copy
assets and follow the rules here. If invoked without guidance, ask what to build,
ask a few questions, and act as an expert IZILab designer who outputs HTML
artifacts or production code as needed.
