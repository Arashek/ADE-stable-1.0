import { monitoringService } from './monitoring.service';

export interface AccessibilityConfig {
  highContrast: boolean;
  fontSize: number;
  reducedMotion: boolean;
  screenReader: boolean;
}

class AccessibilityService {
  private static instance: AccessibilityService;
  private config: AccessibilityConfig;
  private focusableElements: HTMLElement[] = [];
  private currentFocusIndex: number = -1;

  private constructor() {
    this.config = this.loadConfig();
    this.setupEventListeners();
    this.setupKeyboardNavigation();
  }

  public static getInstance(): AccessibilityService {
    if (!AccessibilityService.instance) {
      AccessibilityService.instance = new AccessibilityService();
    }
    return AccessibilityService.instance;
  }

  private loadConfig(): AccessibilityConfig {
    const savedConfig = localStorage.getItem('accessibility_config');
    if (savedConfig) {
      return JSON.parse(savedConfig);
    }
    return {
      highContrast: false,
      fontSize: 16,
      reducedMotion: false,
      screenReader: false,
    };
  }

  private setupEventListeners() {
    // Listen for system-level accessibility changes
    window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
      this.updateConfig({ reducedMotion: e.matches });
    });

    // Track focus changes for analytics
    document.addEventListener('focusin', (e) => {
      const target = e.target as HTMLElement;
      this.trackFocusChange(target);
    });
  }

  private setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        this.handleTabNavigation(e.shiftKey);
      }
    });
  }

  private handleTabNavigation(shiftKey: boolean) {
    const elements = this.getFocusableElements();
    if (elements.length === 0) return;

    if (shiftKey) {
      this.currentFocusIndex = this.currentFocusIndex <= 0
        ? elements.length - 1
        : this.currentFocusIndex - 1;
    } else {
      this.currentFocusIndex = this.currentFocusIndex >= elements.length - 1
        ? 0
        : this.currentFocusIndex + 1;
    }

    elements[this.currentFocusIndex].focus();
  }

  private getFocusableElements(): HTMLElement[] {
    return Array.from(document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )) as HTMLElement[];
  }

  private trackFocusChange(element: HTMLElement) {
    monitoringService.trackUserEvent({
      type: 'focus_change',
      userId: 'anonymous',
      data: {
        element: element.tagName,
        id: element.id,
        className: element.className,
        ariaLabel: element.getAttribute('aria-label'),
      },
    });
  }

  // Public Methods

  public updateConfig(newConfig: Partial<AccessibilityConfig>) {
    this.config = { ...this.config, ...newConfig };
    localStorage.setItem('accessibility_config', JSON.stringify(this.config));
    this.applyConfig();
  }

  private applyConfig() {
    // Apply high contrast
    document.body.classList.toggle('high-contrast', this.config.highContrast);

    // Apply font size
    document.documentElement.style.fontSize = `${this.config.fontSize}px`;

    // Apply reduced motion
    document.body.classList.toggle('reduced-motion', this.config.reducedMotion);

    // Apply screen reader optimizations
    this.toggleScreenReaderOptimizations(this.config.screenReader);
  }

  private toggleScreenReaderOptimizations(enabled: boolean) {
    const elements = document.querySelectorAll('[aria-hidden]');
    elements.forEach((element) => {
      element.setAttribute('aria-hidden', enabled ? 'false' : 'true');
    });
  }

  public addAriaLabel(element: HTMLElement, label: string) {
    element.setAttribute('aria-label', label);
    monitoringService.trackUserEvent({
      type: 'aria_label_added',
      userId: 'anonymous',
      data: {
        element: element.tagName,
        id: element.id,
        label,
      },
    });
  }

  public addKeyboardShortcut(element: HTMLElement, shortcut: string, action: () => void) {
    const keyHandler = (e: KeyboardEvent) => {
      if (e.key === shortcut) {
        e.preventDefault();
        action();
      }
    };

    element.addEventListener('keydown', keyHandler);
    monitoringService.trackUserEvent({
      type: 'keyboard_shortcut_added',
      userId: 'anonymous',
      data: {
        element: element.tagName,
        id: element.id,
        shortcut,
      },
    });
  }

  public announceToScreenReader(message: string) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('role', 'status');
    announcement.textContent = message;
    document.body.appendChild(announcement);
    setTimeout(() => announcement.remove(), 1000);
  }

  public getConfig(): AccessibilityConfig {
    return { ...this.config };
  }

  public cleanup() {
    // Remove event listeners and clean up any resources
  }
}

export const accessibilityService = AccessibilityService.getInstance(); 