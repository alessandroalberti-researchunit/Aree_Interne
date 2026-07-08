import React from "react";

/**
 * IZILab ProgressBar — determinate progress / meter with brand gradient fill.
 */
export function ProgressBar({ value = 0, max = 100, label = "", showValue = true, gradient = true, style = {}, ...rest }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  return (
    <div style={{ fontFamily: "var(--font-body)", ...style }} {...rest}>
      {(label || showValue) && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 8 }}>
          {label && <span style={{ fontSize: 13, color: "var(--text-body)" }}>{label}</span>}
          {showValue && (
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--text-heading)" }}>
              {Math.round(pct)}%
            </span>
          )}
        </div>
      )}
      <div
        style={{
          height: 8,
          borderRadius: "var(--radius-pill)",
          background: "var(--surface-raised)",
          border: "1px solid var(--border-subtle)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: pct + "%",
            height: "100%",
            borderRadius: "var(--radius-pill)",
            background: gradient ? "var(--gradient-brand)" : "var(--color-accent)",
            transition: "width var(--dur-slow) var(--ease-emphasis)",
          }}
        />
      </div>
    </div>
  );
}
