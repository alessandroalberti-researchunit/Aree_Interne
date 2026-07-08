import React from "react";
import { Card } from "./Card.jsx";

/**
 * IZILab StatCard — headline metric in Chivo Mono with label and optional
 * trend delta. Numbers are always mono per the brand rule.
 */
export function StatCard({ value, unit = "", label = "", delta = null, accent = false, style = {}, ...rest }) {
  const up = typeof delta === "string" ? delta.trim().startsWith("+") : delta > 0;
  return (
    <Card accent={accent} padding={22} style={{ minWidth: 180, ...style }} {...rest}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 40,
            fontWeight: 500,
            lineHeight: 1,
            letterSpacing: "-0.01em",
            color: "var(--text-heading)",
          }}
        >
          {value}
        </span>
        {unit && (
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 22, color: "var(--color-accent)" }}>{unit}</span>
        )}
      </div>
      {label && (
        <div style={{ fontFamily: "var(--font-body)", fontSize: 13, color: "var(--text-muted)", marginTop: 8 }}>
          {label}
        </div>
      )}
      {delta != null && (
        <div
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 12,
            marginTop: 10,
            color: up ? "var(--color-accent)" : "var(--color-danger)",
          }}
        >
          {up ? "▲" : "▼"} {delta}
        </div>
      )}
    </Card>
  );
}
