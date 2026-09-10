import * as React from "react";

/** Selectable / removable keyword chip. */
export interface TagProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Highlighted (selected) state. */
  active?: boolean;
  /** When provided, renders a × that calls this handler. */
  onRemove?: () => void;
  children?: React.ReactNode;
}
export declare function Tag(props: TagProps): JSX.Element;
