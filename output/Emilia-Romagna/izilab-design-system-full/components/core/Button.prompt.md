Pill-shaped primary action control — use for the main CTA in any IZILab surface.

```jsx
<Button variant="primary" iconRight={<span>&rarr;</span>}>Esplora il futuro</Button>
<Button variant="accent" size="lg">Inizia ora</Button>
<Button variant="secondary">Scopri di più</Button>
<Button variant="ghost" size="sm">Annulla</Button>
```

Variants: `primary` (violet, default), `accent` (aqua), `secondary` (outline),
`ghost`. Sizes `sm | md | lg`. On dark, primary/accent gain a glow on hover;
press nudges scale to 0.97. Put the `→` arrow in `iconRight` for "continua" CTAs.
