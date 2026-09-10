import * as React from "react";

/**
 * Primary action control for IZILab interfaces.
 * @startingPoint section="Core" subtitle="Pill button · primary/accent/secondary/ghost" viewport="700x220"
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. @default "primary" */
  variant?: "primary" | "accent" | "secondary" | "ghost";
  /** Control size. @default "md" */
  size?: "sm" | "md" | "lg";
  /** Element rendered before the label. */
  iconLeft?: React.ReactNode;
  /** Element rendered after the label (often the → arrow). */
  iconRight?: React.ReactNode;
  /** Disable interaction. */
  disabled?: boolean;
  /** Stretch to container width. */
  full?: boolean;
  children?: React.ReactNode;
}

export declare function Button(props: ButtonProps): JSX.Element;
