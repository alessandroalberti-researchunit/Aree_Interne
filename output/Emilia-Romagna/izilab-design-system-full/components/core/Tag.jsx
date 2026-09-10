import React from "react";

/**
 * IZILab Tag — removable/selectable keyword chip (Instrument Sans).
 * Used for topics: AI, smart cities, data science, foresight…
 */
export function Tag({ children, active = false, onRemove = null, style = {}, ...rest }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        height: 30,
        padding: "0 12px",
        fontFamily: "var(--font-body)",
        fontSize: 13,
        fontWeight: 500,
        borderRadius: "var(--radius-sm)",
        cursor: "default",
        background: active ? "var(--color-primary)" : "var(--surface-raised)",
        color: active ? "var(--text-on-primary)" : "var(--text-body)",
        border: `1px solid ${active ? "transparent" : "var(--border-default)"}`,
        transition: "background var(--dur-fast) var(--ease-standard)",
        ...style,
      }}
      {...rest}
    >
      {children}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label="Remove"
          style={{
            all: "unset",
            cursor: "pointer",
            lineHeight: 1,
            fontSize: 14,
            opacity: 0.7,
            display: "inline-flex",
          }}
        >
          ×
        </button>
      )}
    </span>
  );
}
