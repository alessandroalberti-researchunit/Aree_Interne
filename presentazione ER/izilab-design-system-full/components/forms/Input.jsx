import React, { useState } from "react";

/**
 * IZILab Input — text field with optional label, hint and error.
 */
export function Input({
  label = "",
  hint = "",
  error = "",
  type = "text",
  prefix = null,
  disabled = false,
  style = {},
  id,
  ...rest
}) {
  const [focus, setFocus] = useState(false);
  const fieldId = id || (label ? "in-" + label.replace(/\s+/g, "-").toLowerCase() : undefined);
  const borderColor = error
    ? "var(--color-danger)"
    : focus
    ? "var(--focus-ring)"
    : "var(--border-default)";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, fontFamily: "var(--font-body)", ...style }}>
      {label && (
        <label htmlFor={fieldId} style={{ fontSize: 13, fontWeight: 600, color: "var(--text-body)" }}>
          {label}
        </label>
      )}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          height: 44,
          padding: "0 14px",
          background: "var(--surface-sunken)",
          borderRadius: "var(--radius-sm)",
          border: `1px solid ${borderColor}`,
          boxShadow: focus && !error ? "0 0 0 3px rgba(73,225,192,0.18)" : "none",
          transition: "border-color var(--dur-fast) var(--ease-standard), box-shadow var(--dur-fast) var(--ease-standard)",
          opacity: disabled ? 0.5 : 1,
        }}
      >
        {prefix && <span style={{ color: "var(--text-muted)", display: "inline-flex" }}>{prefix}</span>}
        <input
          id={fieldId}
          type={type}
          disabled={disabled}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            all: "unset",
            flex: 1,
            fontFamily: "var(--font-body)",
            fontSize: 15,
            color: "var(--text-body)",
            width: "100%",
          }}
          {...rest}
        />
      </div>
      {(hint || error) && (
        <span style={{ fontSize: 12, color: error ? "var(--color-danger)" : "var(--text-muted)" }}>
          {error || hint}
        </span>
      )}
    </div>
  );
}
