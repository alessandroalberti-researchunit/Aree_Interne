import * as React from "react";

/** Uppercase contextual label + signature aqua rule. */
export interface KickerProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Optional leading number (rendered in mono): "1. COSA TROVERAI". */
  number?: number | string | null;
  /** Show the short aqua rule beneath. @default true */
  rule?: boolean;
  children?: React.ReactNode;
}
export declare function Kicker(props: KickerProps): JSX.Element;
