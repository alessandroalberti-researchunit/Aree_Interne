import * as React from "react";

/** Small status / category pill. */
export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Color role. @default "accent" */
  tone?: "accent" | "primary" | "neutral" | "success" | "warning" | "danger";
  /** Fill style. @default "soft" */
  variant?: "solid" | "soft" | "outline";
  children?: React.ReactNode;
}
export declare function Badge(props: BadgeProps): JSX.Element;
