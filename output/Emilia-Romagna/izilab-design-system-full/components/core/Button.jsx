import React from "react";

/**
 * IZILab Button — primary action control.
 * Variants: primary (violet), accent (aqua), secondary (outline), ghost.
 */
export function Button({
  variant = "primary",
  size = "md",
  iconLeft = null,
  iconRight = null,
  disabled = false,
  full = false,
  children,
  style = {},
  ...rest
}) {
  const sizes = {
    sm: { padding: "8px 16px", fontSize: 13, height: 36, gap: 8 },
    md: { padding: "11px 22px", fontSize: 15, height: 44, gap: 9 },
    lg: { padding: "15px 30px", fontSize: 16, height: 54, gap: 10 },
  };
  const s = sizes[size] || sizes.md;

  const variants = {
    primary: {
      background: "var(--color-primary)",
      color: "var(--text-on-primary)",
      border: "1px solid transparent",
    },
    accent: {
      background: "var(--color-accent)",
      color: "var(--text-on-accent)",
      border: "1px solid transparent",
    },
    secondary: {
      background: "transparent",
      color: "var(--text-heading)",
      border: "1px solid var(--border-strong)",
    },
    ghost: {
      background: "transparent",
      color: "var(--text-link)",
      border: "1px solid transparent",
    },
  };
  const v = variants[variant] || variants.primary;

  const base = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: s.gap,
    height: s.height,
    padding: s.padding,
    fontSize: s.fontSize,
    width: full ? "100%" : "auto",
    fontFamily: "var(--font-body)",
    fontWeight: 600,
    lineHeight: 1,
    letterSpacing: "0.01em",
    borderRadius: "var(--radius-pill)",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.45 : 1,
    transition:
      "background var(--dur-fast) var(--ease-standard), transform var(--dur-fast) var(--ease-standard), box-shadow var(--dur-base) var(--ease-standard), border-color var(--dur-fast) var(--ease-standard)",
    ...v,
    ...style,
  };

  const hoverBg = {
    primary: "var(--color-primary-hover)",
    accent: "var(--color-accent-hover)",
    secondary: "var(--surface-raised)",
    ghost: "var(--surface-raised)",
  }[variant];

  const onEnter = (e) => {
    if (disabled) return;
    e.currentTarget.style.background = hoverBg;
    if (variant === "secondary") e.currentTarget.style.borderColor = "var(--color-accent)";
    if (variant === "accent") e.currentTarget.style.boxShadow = "var(--glow-aqua)";
    if (variant === "primary") e.currentTarget.style.boxShadow = "var(--glow-violet)";
  };
  const onLeave = (e) => {
    if (disabled) return;
    e.currentTarget.style.background = v.background;
    e.currentTarget.style.borderColor = v.border.includes("strong") ? "var(--border-strong)" : "transparent";
    e.currentTarget.style.boxShadow = "none";
    e.currentTarget.style.transform = "none";
  };
  const onDown = (e) => { if (!disabled) e.currentTarget.style.transform = "scale(0.97)"; };
  const onUp = (e) => { if (!disabled) e.currentTarget.style.transform = "none"; };

  return (
    <button
      type="button"
      disabled={disabled}
      style={base}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onMouseDown={onDown}
      onMouseUp={onUp}
      {...rest}
    >
      {iconLeft}
      {children}
      {iconRight}
    </button>
  );
}
