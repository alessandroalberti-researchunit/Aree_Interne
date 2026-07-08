import * as React from "react";

/**
 * Base surface container for grouped content.
 * @startingPoint section="Surfaces" subtitle="Card surface with optional brand rail" viewport="700x260"
 */
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Show the violet→aqua accent rail on the left edge. */
  accent?: boolean;
  /** Enable hover lift + glow (for clickable cards). */
  interactive?: boolean;
  /** Inner padding in px. @default 24 */
  padding?: number;
  children?: React.ReactNode;
}
export declare function Card(props: CardProps): JSX.Element;
