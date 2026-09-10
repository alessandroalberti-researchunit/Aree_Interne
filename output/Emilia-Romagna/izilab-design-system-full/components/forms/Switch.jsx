import React from "react";

/**
 * IZILab Switch — on/off toggle. Controlled via `checked` + `onChange`.
 */
export function Switch({ checked = false, onChange = () => {}, label = "", disabled = false, style = {}, ...rest }) {
  return (
    <label
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 10,
        fontFamily: "var(--font-body)",
        fontSize: 14,
        color: "var(--text-body)",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.5 : 1,
        ...style,
      }}
      {...rest}
    >
      <span
        onClick={() => !disabled && onChange(!checked)}
        role="switch"
        aria-checked={checked}
        style={{
          width: 44,
          height: 26,
          borderRadius: "var(--radius-pill)",
          background: checked ? "var(--color-accent)" : "var(--surface-raised)",
          border: `1px solid ${checked ? "transparent" : "var(--border-strong)"}`,
          position: "relative",
          transition: "background var(--dur-base) var(--ease-standard)",
          flex: "none",
        }}
      >
        <span
          style={{
            position: "absolute",
            top: 2,
            left: checked ? 20 : 2,
            width: 20,
            height: 20,
            borderRadius: "var(--radius-pill)",
            background: checked ? "var(--text-on-accent)" : "var(--blanche-100)",
            transition: "left var(--dur-base) var(--ease-emphasis)",
            boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
          }}
        />
      </span>
      {label && <span>{label}</span>}
    </label>
  );
}
