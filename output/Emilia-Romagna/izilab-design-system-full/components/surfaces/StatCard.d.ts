import * as React from "react";

/** Headline metric in Chivo Mono with label and optional trend delta. */
export interface StatCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** The number (string or number) — rendered in mono. */
  value: React.ReactNode;
  /** Unit suffix, shown in aqua (e.g. "%"). */
  unit?: string;
  /** Caption under the value. */
  label?: string;
  /** Trend delta, e.g. "+12%" (green) or "-4%" (red). */
  delta?: string | number | null;
  /** Show the brand accent rail. */
  accent?: boolean;
}
export declare function StatCard(props: StatCardProps): JSX.Element;
