// Theme colours and typography tokens. The palette is deliberately muted and
// paper-like — imagery is distinguished by a restrained accent per theme.
import type { Theme } from "../types";

export const THEME_COLORS: Record<Theme, string> = {
  nature: "#5f6b4b", // moss
  light: "#b98a2f", // amber
  home: "#8a5a38", // earth
  body: "#9c4a45", // cinnabar
  death: "#4b4b55", // slate
  myth: "#6a5a8c", // muted violet
  place: "#3f6a6a", // teal
};

export const THEME_LABELS: Record<Theme, string> = {
  nature: "自然",
  light: "光明",
  home: "家园",
  body: "身体",
  death: "死亡",
  myth: "神话",
  place: "地理",
};

export function themeColor(theme: Theme): string {
  return THEME_COLORS[theme] ?? THEME_COLORS.nature;
}

// Map a raw frequency onto a node radius (px). Scale grows sub-linearly so
// the largest words do not dominate the field.
export function radiusFor(frequency: number, maxFrequency: number): number {
  const t = frequency / maxFrequency;
  return 7 + Math.pow(t, 0.55) * 20;
}
