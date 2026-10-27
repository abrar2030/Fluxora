import theme, {
  colors,
  fontSize,
  lightTheme,
  shadows,
  spacing,
} from "../../src/styles/theme";

describe("theme tokens", () => {
  it("maps the primary color into the paper theme", () => {
    expect(lightTheme.colors.primary).toBe(colors.primary);
    expect(lightTheme.dark).toBe(false);
  });

  it("exposes ascending spacing and font scales", () => {
    const spacingValues = Object.values(spacing);
    const fontValues = Object.values(fontSize);
    expect([...spacingValues].sort((a, b) => a - b)).toEqual(spacingValues);
    expect([...fontValues].sort((a, b) => a - b)).toEqual(fontValues);
  });

  it("provides three increasing shadow presets", () => {
    expect(shadows.small.elevation).toBeLessThan(shadows.medium.elevation);
    expect(shadows.medium.elevation).toBeLessThan(shadows.large.elevation);
  });

  it("re-exports every token from the default export", () => {
    expect(theme.colors).toBe(colors);
    expect(theme.spacing).toBe(spacing);
  });
});
