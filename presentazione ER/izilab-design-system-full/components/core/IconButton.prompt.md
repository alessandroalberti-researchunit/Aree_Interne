Icon-only control for compact affordances — the forward arrow, close, menu.

```jsx
<IconButton variant="accent" label="Continua"><span>&rarr;</span></IconButton>
<IconButton variant="outline" shape="square" label="Menu">≡</IconButton>
```

`variant`: solid | accent | ghost (default) | outline. `shape`: round | square.
Keep `size` ≥ 44 for touch targets.
