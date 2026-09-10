import React from "react";

/**
 * IZILab IconButton — square/round control for a single glyph (e.g. → close, menu).
 * variant: solid | ghost | outline ; shape: round | square
 */
export function IconButton({
  variant = "ghost",
  shape = "round",
  size = 44,
  label = "",
  children,
  disabled = false,
  style = {},
  ...rest
}) {
  const variants = {
    solid:   { background: "var(--color-primary)", color: "var(--text-on-primary)", border: "1px solid transparent" },
    accent:  { background: "var(--color-accent)",  color: "var(--text-on-accent)",  border: "1px solid transparent" },
    ghost:   { background: "transparent",          color: "var(--text-body)",       border: "1px solid transparent" },
    outline: { background: "transparent",          color: "var(--text-body)",       border: "1px solid var(--border-strong)" },
  };
  const v = variants[variant] || variants.ghost;

  return (
    <button
      type="button"
      aria-label={label}
      disabled={disabled}
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: size,
        height: size,
        borderRadius: shape === "round" ? "var(--radius-pill)" : "var(--radius-md)",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.45 : 1,
        transition: "background var(--dur-fast) var(--ease-standard), border-color var(--dur-fast) var(--ease-standard)",
        ...v,
        ...style,
      }}
      onMouseEnter={(e) => { if (!disabled && variant === "ghost") e.currentTarget.style.background = "var(--surface-raised)"; if (!disabled && variant === "outline") e.currentTarget.style.borderColor = "var(--color-accent)"; }}
      onMouseLeave={(e) => { if (!disabled) { e.currentTarget.style.background = v.background; e.currentTarget.style.borderColor = variant === "outline" ? "var(--border-strong)" : "transparent"; } }}
      {...rest}
    >
      {children}
    </button>
  );
}
