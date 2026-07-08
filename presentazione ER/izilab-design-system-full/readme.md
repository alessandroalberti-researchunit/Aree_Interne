# IZILab — Sistema visivo (Design System)

> **IZILab** — laboratorio di ricerca e foresight che guida aziende e istituzioni
> attraverso l'incertezza del futuro con un approccio solido e basato sui dati.
> Sistema visivo *digital-first* con doppia modalità **Light / Dark**.
>
> **Payoff:** *"Il futuro non si aspetta, si anticipa."*

This project is the machine-readable source of truth for the IZILab brand: tokens,
fonts, reusable components, foundation specimens, sample slides and a UI kit. A
consuming project links a single file — `styles.css` — and gets the whole token +
font layer. Components are bundled automatically and read from
`window.IZILabDesignSystem_03588f`.

---

## Sources

Everything here was reconstructed from the materials supplied with the brief —
keep them in case the reader has access:

- **`tokens/` codebase** (mounted, read-only) — `colors.css` + `colors.json`,
  the authoritative Figma-variable export (Palette.pdf / Theme.pdf, *Marzo 2025*).
  This is the source of truth for color. **Note:** the printed palette sheet shows
  a *refuso* (`#6E54E8`) for Violet/500 — the correct primary is **`#6422E8`**.
- **Uploaded reference sheets** (`uploads/`, pages from the "IZI Lab · Sistema
  visivo" deck): `palette-scale`, `palette-dark`, `palette-light`,
  `type-cirka` (display), `type-instrument-sans` (body), `type-chivo-mono` (data),
  `backgrounds-dark`, `backgrounds-light`, `lines-pattern`, `icons-set`,
  `icons-generator`, `social-carousel`, `social-quotes`, `logo-izilab`.
- The "Icon Generator" referenced in the deck is an external app that produces
  the abstract geometric icon set; only static exports were available.

No Figma/GitHub URLs were provided — these were not linked, so cross-reference is
limited to the exported sheets above.

---

## Brand at a glance

| | |
|---|---|
| **Primary** | Violet/500 `#6422E8` |
| **Accent** | Aqua/500 `#49E1C0` |
| **Neutral** | Blanche/500 `#ECEBFE` |
| **Brand gradient** | `linear-gradient(135deg, #6422E8 0%, #49E1C0 100%)` |
| **Display type** | Cirka → **Domine** (fallback) |
| **Body type** | Instrument Sans |
| **Data type** | Chivo Mono |
| **Default mode** | Dark (digital-first); Light for documents / readability |

---

## CONTENT FUNDAMENTALS — how IZILab writes

**Language.** Primary language is **Italian**. Copy is precise, forward-looking and
confident — the voice of a foresight lab, not a hype startup. Technical but
elegant ("tecnico ed elegante" is the phrase used for the visual system, and it
applies to the words too).

**Tone.** Anticipatory and assured. The payoff sets the register: *"Il futuro non
si aspetta, si anticipa."* Statements are declarative and grounded in data
("approccio solido e basato sui dati"). Avoid breathless futurism; favour clarity
and authority.

**Person.** Mixed and contextual. Brand statements speak in an institutional
"noi" implicitly. Social/community copy addresses the reader directly with the
informal **"tu"** — e.g. *"Tutto ciò che ti serve per guardare al futuro"*,
*"stimolare le tue riflessioni"*. Keep the **tu** warm but not casual.

**Casing.** **Sentence case everywhere** for titles and display — never all-caps
headlines. The one exception is the **kicker**: a short contextual label set in
Instrument Sans, UPPERCASE, letter-spaced, often numbered
(e.g. `1. COSA TROVERAI`, `5. COSA TROVERAI`). Kickers introduce a block; titles
follow in Cirka; body follows in Instrument Sans.

**Structure of a unit of content** (carousel slide model): `kicker → title →
short aqua rule → body → forward arrow (→)`. The arrow signals "continua".

**Numbers & data.** Always in **Chivo Mono** — percentages, figures, dates,
tables, stat callouts. This is non-negotiable and is the single strongest
typographic signal of the brand.

**Examples of real copy** (from the system): section names like
*"Racconto futuristico"*, *"Risorse per approfondire"*, *"Innovazioni del mese"*,
*"Community"*; descriptive blurbs such as *"una sezione dedicata alle ultime
tecnologie e alle nuove applicazioni più rilevanti nel mondo dell'intelligenza
artificiale, delle smart cities, della data science, dei big data, di GenAI…"*.

**Emoji.** Not used in brand/editorial copy. (The internal Icon Generator UI uses
a few playful emoji on its own buttons, but that is tooling chrome, not brand
voice.) Do **not** add emoji to slides, UI or marketing copy.

**Don'ts.** No exclamation-heavy hype, no all-caps shouting, no low-contrast or
bright body text on dark backgrounds (a stated rule), no decorative numerals in a
non-mono face.

---

## VISUAL FOUNDATIONS

**Colour.** A three-family system — **Violet** (primary, the brand's identity
colour), **Aqua** (accent / energy / "connettività"), **Blanche** (a violet-tinted
near-neutral, never pure grey). Each family runs a 100→900 scale. Semantic tokens
have **distinct values per mode**. Dark mode lives on deep violet (`#0F0830`
page / `#1B054B` surfaces); light mode lives on near-white violet-tinted Blanche.
High contrast is mandatory. Bright accent colour is for highlights, CTAs, rules
and data — **not** for running body text on dark.

**Gradients.** The signature is the **violet↔aqua** brand gradient
(`135deg, #6422E8 → #49E1C0`) used for "profondità e connettività". Beyond the
linear brand gradient there are *mono* (violet→violet), *duo* (violet↔aqua),
*radial* (aqua→violet→deep-violet) and *chart* gradients for data viz. Gradient
text is used sparingly on hero words.

**Backgrounds.** Two registers. (1) **Aurora / bloom** — soft, blurred, grainy
gradient fields (violet and aqua light leaking through near-black, or pale washes
on white). Immersive, atmospheric; used full-bleed behind hero slides and covers.
(2) **Linee** — fine *technical* line work: perspective grids, topographic mesh,
wireframe contours, plotted dot fields. Subtle, monochrome, low-opacity; layered
over solid or gradient fills to add "profondità e dinamicità… stile tecnico ed
elegante". Both are provided as static PNGs in `assets/backgrounds/` and
recreated as CSS helpers (`.izi-bg-aurora`, `.izi-bg-grid`). Imagery vibe is
**cool** (blue-violet / teal), often dark and atmospheric, with visible grain.

**Type.** High-contrast condensed serif (**Cirka**, fallback **Domine**) for
display/titles, set in sentence case with tight tracking. A clean grotesque
(**Instrument Sans**) for body, kickers and CTAs. A monospace (**Chivo Mono**)
exclusively for numbers and data. The serif/sans/mono triad is the typographic
fingerprint.

**Spacing & layout.** 8px grid. Editorial, generous, document-like layouts: a
strong left title column, a content column, and a meta/notes column (the deck
itself uses a 2–3 column grid with thin rules and page numbers). Thin hairline
rules (`1px`, low-opacity) separate regions.

**Borders & corners.** Geometry is **crisp and restrained**, not pillowy. Cards
and surfaces use small-to-medium radii (8–24px); buttons commonly pill or
medium-radius. Hairline borders (`--border-subtle/default/strong`) carry most of
the structure in dark mode; the short **aqua rule** (40×3px pill) is a recurring
accent under kickers and titles.

**Elevation.** Mode-dependent. **Dark mode** uses **glows** (soft violet/aqua
halos, `--glow-violet`, `--glow-aqua`) rather than drop shadows — light appears to
emit from elements. **Light mode** uses **soft neutral drop shadows**
(`--shadow-sm/md/lg`). Blur/transparency is used for layered surfaces and
glassy overlays sparingly.

**Iconography.** See the dedicated section below — abstract geometry, never
classic UI glyphs.

**Motion.** Restrained and elegant: gentle ease-out fades and short upward
reveals (`izi-fade-up`, `--ease-emphasis`, ~420ms). No bounces, no infinite
decorative loops on content. Hover states lighten/raise (and on dark, intensify
the glow); press states deepen the colour and nudge scale down slightly. All
motion respects `prefers-reduced-motion`.

**Hover / press conventions.**
- *Primary button*: hover → `--color-primary-hover` (violet-600); press →
  `--color-primary-press` (violet-700) + subtle scale 0.98.
- *Accent button*: hover → `--color-accent-hover`; dark mode adds aqua glow.
- *Links*: aqua on dark, violet-600 on light; underline on hover.
- *Cards*: hover lifts elevation (glow on dark / shadow on light).

---

## ICONOGRAPHY

IZILab deliberately **rejects classic line-icon sets**. Its iconography is a system
of **abstract geometric illustrations** — outlined forms (dark navy/violet stroke)
filled with **violet↔aqua gradient** passages: seeds/leaves, lenses, stacked
diamonds, concentric ellipses, overlapping circles, sunbursts, hexagons,
window/aperture forms. They are conceptual, not literal — meant to *evoke*
foresight, connection, depth and emergence rather than label a function.

- **Format:** vector illustrations exported as PNG. The brand maintains an internal
  **"Icon Generator"** app ("Set Generativo", *50+ varianti geometriche diverse*)
  that produces new variants on demand in **Viola** or **Teal** palettes — so the
  set is generative, not fixed.
- **Stored here:** representative exports live in `assets/icons/`
  (`icon-seed`, `icon-diamond-square`, `icon-lens-arrow`, `icon-stack-diamond`,
  `icon-concentric`, `icon-overlap-circle`, `icon-sunburst`, `icon-window`).
  These are cropped from the supplied "Icon Light V1" sheet (light background).
- **Usage:** as feature marks, slide accents, card glyphs and section symbols —
  one per concept, given room to breathe. Do **not** hand-draw new ones in a
  different style; use the generator or the stored set.
- **Functional UI glyphs** (arrows, chevrons, close, etc.) are minimal and
  utilitarian. The recurring one is the **forward arrow `→`** ("continua"). For
  small interface affordances we substitute **Lucide** (CDN) at a matching light
  stroke weight — *flagged substitution*, see CAVEATS.
- **Emoji:** not used as iconography in brand contexts. No Unicode-as-icon beyond
  the editorial `→`.

---

## VISUAL FOUNDATIONS recap → tokens map

| Concern | File |
|---|---|
| Colours (primitives + semantics, Light/Dark) | `tokens/colors.css` |
| Fonts (`@import` Google + Cirka slot) | `tokens/fonts.css` |
| Type scale, weights, families | `tokens/typography.css` |
| Spacing, radii, borders, shadows, motion, layout | `tokens/spacing.css` |
| Element defaults + brand helpers | `tokens/base.css` |
| Global entry (import list only) | `styles.css` |

---

## INDEX — what's in this project

**Root**
- `styles.css` — global entry point (link this one file).
- `readme.md` — this guide.
- `SKILL.md` — Agent-Skills-compatible wrapper.

**`tokens/`** — `colors.css`, `fonts.css`, `typography.css`, `spacing.css`,
`base.css` (+ original `colors.json` reference).

**`assets/`**
- `logo/logo-izilab.png` — primary lockup.
- `backgrounds/` — aurora + wisp gradient fields (dark & light).
- `icons/` — abstract geometric icon exports.

**`guidelines/`** — foundation specimen cards (Design System tab): colour scales &
roles, type specimens, spacing, radii, shadows, gradients, logo, backgrounds,
iconography.

**`components/`** — reusable React primitives (read from
`window.IZILabDesignSystem_03588f`):
- `core/` — `Button`, `IconButton`, `Badge`, `Tag`
- `forms/` — `Input`, `Select`, `Switch`
- `surfaces/` — `Card`, `StatCard`, `Kicker`
- `feedback/` — `ProgressBar`

**`ui_kits/foreseen-carousel/`** — interactive recreation of the IZILab
"Foreseen" social-carousel system (the documented product surface): a
click-through 4:5 carousel viewer with dark + light slides.

**`slides/`** — sample 16:9 slides (Title, Section, Stat, Quote, Content) built on
the foundations.

---

*IZILab · Sistema visivo · Marzo 2025 — "Il futuro non si aspetta, si anticipa."*
