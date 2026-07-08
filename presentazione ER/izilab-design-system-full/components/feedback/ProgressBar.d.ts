import * as React from "react";

/** Determinate progress bar / meter with the brand gradient fill. */
export interface ProgressBarProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Current value. */
  value?: number;
  /** Maximum value. @default 100 */
  max?: number;
  /** Label shown on the left. */
  label?: string;
  /** Show the % readout (mono) on the right. @default true */
  showValue?: boolean;
  /** Use the violet→aqua gradient fill (vs solid aqua). @default true */
  gradient?: boolean;
}
export declare function ProgressBar(props: ProgressBarProps): JSX.Element;
