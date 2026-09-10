import * as React from "react";

export type SelectOption = string | { value: string; label: string };

/** Native select styled to the IZILab system. */
export interface SelectProps {
  label?: string;
  options: SelectOption[];
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  disabled?: boolean;
  id?: string;
  style?: React.CSSProperties;
}
export declare function Select(props: SelectProps): JSX.Element;
