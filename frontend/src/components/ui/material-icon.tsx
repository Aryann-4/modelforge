"use client";

interface MaterialIconProps {
  name: string;
  className?: string;
  filled?: boolean;
}

export function MaterialIcon({ name, className = "", filled = false }: MaterialIconProps) {
  return (
    <span
      className={`material-symbols-outlined ${filled ? "[font-variation-settings:'FILL'_1]" : ""} ${className}`}
    >
      {name}
    </span>
  );
}
