import React from "react";

/**
 * IZILab Badge — small status/category pill.
 * tone: accent | primary | neutral | success | warning | danger
 * variant: solid | soft | outline
 */
export function Badge({ tone = "accent", variant = "soft", children, style = {}, ...rest }) {
  const palette = {
    accent:  { solid: "var(--color-accent)",  fg: "var(--text-on-accent)",  soft: "rgba(73,225,192,0.16)",  softFg: "var(--aqua-300)",   line: "var(--aqua-500)" },
    primary: { solid: "var(--color-primary)", fg: "var(--text-on-primary)", soft: "rgba(142,125,246,0.20)", softFg: "var(--violet-300)", line: "var(--violet-400)" },
    neutral: { solid: "var(--blanche-700)",   fg: "var(--blanche-100)",     soft: "rgba(150,149,167,0.18)", softFg: "var(--text-muted)", line: "var(--border-strong)" },
    success: { solid: "var(--color-success)", fg: "var(--text-on-accent)",  soft: "rgba(73,225,192,0.16)",  softFg: "var(--aqua-300)",   line: "var(--aqua-500)" },
    warning: { solid: "var(--color-warning)", fg: "#2a1c00",                soft: "rgba(245,196,81,0.18)",  softFg: "#F5C451",           line: "#F5C451" },
    danger:  { solid: "var(--color-danger)",  fg: "#2a0008",                soft: "rgba(242,101,125,0.18)", softFg: "#F2657D",           line: "#F2657D" },
  }[tone] || {};

  const v =
    variant === "solid"
      ? { background: palette.solid, color: palette.fg, border: "1px solid transparent" }
      : variant === "outline"
      ? { background: "transparent", color: palette.softFg, border: `1px solid ${palette.line}` }
      : { background: palette.soft, color: palette.softFg, border: "1px solid transparent" };

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        height: 24,
        padding: "0 10px",
        fontFamily: "var(--font-body)",
        fontSize: 12,
        fontWeight: 600,
        letterSpacing: "0.02em",
        borderRadius: "var(--radius-pill)",
        whiteSpace: "nowrap",
        ...v,
        ...style,
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
