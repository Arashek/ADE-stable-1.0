import '@mui/material/styles';

declare module '@mui/material/styles' {
  interface Palette {
    // Add custom palette colors
    purple: Palette['primary'];
    blue: Palette['primary'];
    green: Palette['primary'];
    red: Palette['primary'];
    orange: Palette['primary'];
    blueGrey: Palette['primary'];
  }

  interface PaletteOptions {
    // Add custom palette color options
    purple?: PaletteOptions['primary'];
    blue?: PaletteOptions['primary'];
    green?: PaletteOptions['primary'];
    red?: PaletteOptions['primary'];
    orange?: PaletteOptions['primary'];
    blueGrey?: PaletteOptions['primary'];
  }
}

// Extend the theme to include custom properties
declare module '@mui/material/styles' {
  interface Theme {
    // Add any additional custom properties here
  }
  interface ThemeOptions {
    // Add any additional custom properties here
  }
}
