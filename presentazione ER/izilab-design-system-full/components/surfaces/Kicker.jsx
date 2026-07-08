import React from "react";

/**
 * IZILab Kicker — small uppercase contextual label, optionally numbered,
 * with the signature short aqua rule beneath it.
 */
export function Kicker({ children, number = null, rule = true, style = {}, ...rest }) {
  return (
    <div style={{ ...style }} {...rest}>
      <div
        style={{
          fontFamily: "var(--font-body)",
          fontSize: "var(--text-xs)",
          fontWeight: 600,
          letterSpacing: "var(--ls-kicker)",
          textTransform: "uppercase",
          color: "var(--text-kicker)",
        }}
      >
        {number != null && <span style={{ fontFamily: "var(--font-mono)" }}>{number}. </span>}
        {children}
      </div>
      {rule && (
        <span
          aria-hidden="true"
          style={{
            display: "block",
            width: 40,
            height: 3,
            borderRadius: "var(--radius-pill)",
            background: "var(--color-accent)",
            marginTop: 12,
          }}
        />
      )}
    </div>
  );
}
