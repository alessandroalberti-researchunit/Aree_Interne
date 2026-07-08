import React from "react";

/**
 * IZILab Card — base surface container. Optional accent rail, hover lift.
 */
export function Card({
  accent = false,
  interactive = false,
  padding = 24,
  children,
  style = {},
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  return (
    <div
      onMouseEnter={() => interactive && setHover(true)}
      onMouseLeave={() => interactive && setHover(false)}
      style={{
        position: "relative",
        background: "var(--surface-card)",
        border: "1px solid var(--border-default)",
        borderRadius: "var(--radius-lg)",
        padding,
        overflow: "hidden",
        boxShadow: hover ? "var(--glow-violet)" : "none",
        transform: hover ? "translateY(-2px)" : "none",
        transition: "box-shadow var(--dur-base) var(--ease-standard), transform var(--dur-base) var(--ease-standard)",
        cursor: interactive ? "pointer" : "default",
        ...style,
      }}
      {...rest}
    >
      {accent && (
        <span
          aria-hidden="true"
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            height: "100%",
            width: 4,
            background: "var(--gradient-brand)",
          }}
        />
      )}
      {children}
    </div>
  );
}
