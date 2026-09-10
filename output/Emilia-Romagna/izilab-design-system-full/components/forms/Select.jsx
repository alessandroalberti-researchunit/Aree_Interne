import React, { useState } from "react";

/**
 * IZILab Select — native dropdown styled to the system.
 */
export function Select({ label = "", options = [], value, onChange, disabled = false, style = {}, id, ...rest }) {
  const [focus, setFocus] = useState(false);
  const fieldId = id || (label ? "sel-" + label.replace(/\s+/g, "-").toLowerCase() : undefined);
  const opts = options.map((o) => (typeof o === "string" ? { value: o, label: o } : o));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, fontFamily: "var(--font-body)", ...style }}>
      {label && (
        <label htmlFor={fieldId} style={{ fontSize: 13, fontWeight: 600, color: "var(--text-body)" }}>
          {label}
        </label>
      )}
      <div
        style={{
          position: "relative",
          height: 44,
          background: "var(--surface-sunken)",
          borderRadius: "var(--radius-sm)",
          border: `1px solid ${focus ? "var(--focus-ring)" : "var(--border-default)"}`,
          boxShadow: focus ? "0 0 0 3px rgba(73,225,192,0.18)" : "none",
          transition: "border-color var(--dur-fast) var(--ease-standard)",
          opacity: disabled ? 0.5 : 1,
        }}
      >
        <select
          id={fieldId}
          value={value}
          onChange={onChange}
          disabled={disabled}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            all: "unset",
            width: "100%",
            height: "100%",
            boxSizing: "border-box",
            padding: "0 38px 0 14px",
            fontFamily: "var(--font-body)",
            fontSize: 15,
            color: "var(--text-body)",
            cursor: disabled ? "not-allowed" : "pointer",
          }}
          {...rest}
        >
          {opts.map((o) => (
            <option key={o.value} value={o.value} style={{ color: "#111" }}>
              {o.label}
            </option>
          ))}
        </select>
        <span
          aria-hidden="true"
          style={{
            position: "absolute",
            right: 14,
            top: "50%",
            transform: "translateY(-50%)",
            pointerEvents: "none",
            color: "var(--text-muted)",
            fontSize: 12,
          }}
        >
          ▾
        </span>
      </div>
    </div>
  );
}
