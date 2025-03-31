import { createTheme, Theme, ThemeOptions } from '@mui/material';
import { performanceMonitor } from './performance';
import { cacheService } from './cache.service';

interface CustomizationPreferences {
  theme: 'light' | 'dark' | 'system';
  primaryColor: string;
  secondaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
  density: 'compact' | 'comfortable' | 'spacious';
  borderRadius: number;
  animations: boolean;
  customCss?: string;
}

interface CustomThemeOptions extends ThemeOptions {
  density: 'compact' | 'comfortable' | 'spacious';
}

const defaultPreferences: CustomizationPreferences = {
  theme: 'system',
  primaryColor: '#1976d2',
  secondaryColor: '#dc004e',
  fontSize: 'medium',
  density: 'comfortable',
  borderRadius: 4,
  animations: true,
};

export class CustomizationService {
  private preferences: CustomizationPreferences;
  private currentTheme: Theme;
  private listeners: Set<() => void> = new Set();

  constructor() {
    this.preferences = this.loadPreferences();
    this.currentTheme = this.createTheme(this.preferences);
  }

  /**
   * Get current preferences
   */
  getPreferences(): CustomizationPreferences {
    return { ...this.preferences };
  }

  /**
   * Update preferences
   */
  updatePreferences(updates: Partial<CustomizationPreferences>): void {
    const startTime = performance.now();
    try {
      this.preferences = {
        ...this.preferences,
        ...updates,
      };

      this.currentTheme = this.createTheme(this.preferences);
      this.savePreferences();
      this.notifyListeners();

      performanceMonitor.recordMetric(
        'customization-update',
        performance.now() - startTime
      );
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error updating preferences:', error);
    }
  }

  /**
   * Get current theme
   */
  getTheme(): Theme {
    return this.currentTheme;
  }

  /**
   * Subscribe to preference changes
   */
  subscribe(callback: () => void): () => void {
    this.listeners.add(callback);
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * Reset preferences to defaults
   */
  resetPreferences(): void {
    const startTime = performance.now();
    try {
      this.preferences = { ...defaultPreferences };
      this.currentTheme = this.createTheme(this.preferences);
      this.savePreferences();
      this.notifyListeners();

      performanceMonitor.recordMetric(
        'customization-reset',
        performance.now() - startTime
      );
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error resetting preferences:', error);
    }
  }

  /**
   * Export preferences
   */
  exportPreferences(): string {
    const startTime = performance.now();
    try {
      const exported = JSON.stringify(this.preferences, null, 2);
      performanceMonitor.recordMetric(
        'customization-export',
        performance.now() - startTime
      );
      return exported;
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error exporting preferences:', error);
      return '';
    }
  }

  /**
   * Import preferences
   */
  importPreferences(data: string): void {
    const startTime = performance.now();
    try {
      const imported = JSON.parse(data) as CustomizationPreferences;
      this.updatePreferences(imported);
      performanceMonitor.recordMetric(
        'customization-import',
        performance.now() - startTime
      );
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error importing preferences:', error);
    }
  }

  /**
   * Apply custom CSS
   */
  applyCustomCss(css: string): void {
    const startTime = performance.now();
    try {
      const styleId = 'custom-theme-css';
      let styleElement = document.getElementById(styleId);

      if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = styleId;
        document.head.appendChild(styleElement);
      }

      styleElement.textContent = css;
      this.preferences.customCss = css;
      this.savePreferences();

      performanceMonitor.recordMetric(
        'customization-css-apply',
        performance.now() - startTime
      );
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error applying custom CSS:', error);
    }
  }

  private createTheme(preferences: CustomizationPreferences): Theme {
    const startTime = performance.now();
    try {
      const spacing = (() => {
        switch (preferences.density) {
          case 'compact':
            return 4;
          case 'spacious':
            return 8;
          default:
            return 6;
        }
      })();

      const fontSize = (() => {
        switch (preferences.fontSize) {
          case 'small':
            return 14;
          case 'large':
            return 18;
          default:
            return 16;
        }
      })();

      const themeOptions: CustomThemeOptions = {
        palette: {
          mode: preferences.theme === 'system'
            ? window.matchMedia('(prefers-color-scheme: dark)').matches
              ? 'dark'
              : 'light'
            : preferences.theme,
          primary: {
            main: preferences.primaryColor,
          },
          secondary: {
            main: preferences.secondaryColor,
          },
        },
        shape: {
          borderRadius: preferences.borderRadius,
        },
        spacing,
        typography: {
          fontSize,
        },
        components: {
          MuiButtonBase: {
            defaultProps: {
              disableRipple: !preferences.animations,
            },
          },
        },
        density: preferences.density,
      };

      const theme = createTheme(themeOptions);
      performanceMonitor.recordMetric(
        'customization-theme-create',
        performance.now() - startTime
      );
      return theme;
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error creating theme:', error);
      return createTheme();
    }
  }

  private loadPreferences(): CustomizationPreferences {
    const startTime = performance.now();
    try {
      const cached = cacheService.get<CustomizationPreferences>('user-preferences');
      if (cached) {
        performanceMonitor.recordMetric(
          'customization-load-cache',
          performance.now() - startTime
        );
        return cached;
      }

      const stored = localStorage.getItem('user-preferences');
      if (stored) {
        const preferences = JSON.parse(stored);
        cacheService.set('user-preferences', preferences);
        performanceMonitor.recordMetric(
          'customization-load-storage',
          performance.now() - startTime
        );
        return preferences;
      }

      return { ...defaultPreferences };
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error loading preferences:', error);
      return { ...defaultPreferences };
    }
  }

  private savePreferences(): void {
    const startTime = performance.now();
    try {
      localStorage.setItem('user-preferences', JSON.stringify(this.preferences));
      cacheService.set('user-preferences', this.preferences);
      performanceMonitor.recordMetric(
        'customization-save',
        performance.now() - startTime
      );
    } catch (error) {
      performanceMonitor.recordMetric('customization-error', 1);
      console.error('Error saving preferences:', error);
    }
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener();
      } catch (error) {
        console.error('Error in customization listener:', error);
      }
    });
  }
}

// Create a singleton instance
export const customizationService = new CustomizationService(); 