import * as React from "react";

/** Icon-only control (arrow, close, menu…). */
export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. @default "ghost" */
  variant?: "solid" | "accent" | "ghost" | "outline";
  /** Corner shape. @default "round" */
  shape?: "round" | "square";
  /** Pixel size of the square hit area. @default 44 */
  size?: number;
  /** Accessible label (aria-label). */
  label?: string;
  children?: React.ReactNode;
}
export declare function IconButton(props: IconButtonProps): JSX.Element;
