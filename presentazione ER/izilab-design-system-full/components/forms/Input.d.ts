import * as React from "react";

/** Single-line text field with label, hint and error states. */
export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "prefix"> {
  /** Field label. */
  label?: string;
  /** Helper text shown below. */
  hint?: string;
  /** Error message (turns the field red). */
  error?: string;
  /** Leading adornment (icon or text). */
  prefix?: React.ReactNode;
}
export declare function Input(props: InputProps): JSX.Element;
