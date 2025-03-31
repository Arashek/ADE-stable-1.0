import { useState, useEffect, useCallback } from 'react';
import { performanceMonitor } from '../services/performance';

interface AccessibilityOptions {
  highContrast?: boolean;
  largeText?: boolean;
  reducedMotion?: boolean;
  screenReader?: boolean;
  keyboardOnly?: boolean;
}

interface AccessibilityState extends AccessibilityOptions {
  announcements: string[];
}

export const useAccessibility = (initialOptions: AccessibilityOptions = {}) => {
  const [state, setState] = useState<AccessibilityState>({
    highContrast: initialOptions.highContrast || false,
    largeText: initialOptions.largeText || false,
    reducedMotion: initialOptions.reducedMotion || false,
    screenReader: initialOptions.screenReader || false,
    keyboardOnly: initialOptions.keyboardOnly || false,
    announcements: [],
  });

  // Load preferences from localStorage on mount
  useEffect(() => {
    const startTime = performance.now();
    try {
      const stored = localStorage.getItem('accessibility-preferences');
      if (stored) {
        const preferences = JSON.parse(stored);
        setState(prev => ({
          ...prev,
          ...preferences,
        }));
      }
      performanceMonitor.recordMetric('accessibility-load', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('accessibility-load-error', 1);
    }
  }, []);

  // Save preferences to localStorage when they change
  useEffect(() => {
    const startTime = performance.now();
    try {
      const preferences = {
        highContrast: state.highContrast,
        largeText: state.largeText,
        reducedMotion: state.reducedMotion,
        screenReader: state.screenReader,
        keyboardOnly: state.keyboardOnly,
      };
      localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
      performanceMonitor.recordMetric('accessibility-save', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('accessibility-save-error', 1);
    }
  }, [state.highContrast, state.largeText, state.reducedMotion, state.screenReader, state.keyboardOnly]);

  // Apply CSS classes based on preferences
  useEffect(() => {
    const startTime = performance.now();
    try {
      const root = document.documentElement;
      root.classList.toggle('high-contrast', state.highContrast);
      root.classList.toggle('large-text', state.largeText);
      root.classList.toggle('reduced-motion', state.reducedMotion);
      root.classList.toggle('screen-reader', state.screenReader);
      root.classList.toggle('keyboard-only', state.keyboardOnly);
      performanceMonitor.recordMetric('accessibility-apply', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('accessibility-apply-error', 1);
    }
  }, [state.highContrast, state.largeText, state.reducedMotion, state.screenReader, state.keyboardOnly]);

  // Toggle individual preferences
  const toggleHighContrast = useCallback(() => {
    setState(prev => ({ ...prev, highContrast: !prev.highContrast }));
    performanceMonitor.recordMetric('accessibility-toggle', 1);
  }, []);

  const toggleLargeText = useCallback(() => {
    setState(prev => ({ ...prev, largeText: !prev.largeText }));
    performanceMonitor.recordMetric('accessibility-toggle', 1);
  }, []);

  const toggleReducedMotion = useCallback(() => {
    setState(prev => ({ ...prev, reducedMotion: !prev.reducedMotion }));
    performanceMonitor.recordMetric('accessibility-toggle', 1);
  }, []);

  const toggleScreenReader = useCallback(() => {
    setState(prev => ({ ...prev, screenReader: !prev.screenReader }));
    performanceMonitor.recordMetric('accessibility-toggle', 1);
  }, []);

  const toggleKeyboardOnly = useCallback(() => {
    setState(prev => ({ ...prev, keyboardOnly: !prev.keyboardOnly }));
    performanceMonitor.recordMetric('accessibility-toggle', 1);
  }, []);

  // Announce messages for screen readers
  const announce = useCallback((message: string) => {
    const startTime = performance.now();
    try {
      setState(prev => ({
        ...prev,
        announcements: [...prev.announcements, message],
      }));
      performanceMonitor.recordMetric('accessibility-announce', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('accessibility-announce-error', 1);
    }
  }, []);

  // Clear announcements after they've been read
  const clearAnnouncements = useCallback(() => {
    setState(prev => ({
      ...prev,
      announcements: [],
    }));
  }, []);

  // Handle keyboard navigation
  useEffect(() => {
    if (state.keyboardOnly) {
      const handleMouseDown = (e: MouseEvent) => {
        if (!e.target || !(e.target as HTMLElement).hasAttribute('data-keyboard-allowed')) {
          e.preventDefault();
          performanceMonitor.recordMetric('accessibility-keyboard-only-block', 1);
        }
      };

      document.addEventListener('mousedown', handleMouseDown);
      return () => {
        document.removeEventListener('mousedown', handleMouseDown);
      };
    }
  }, [state.keyboardOnly]);

  return {
    ...state,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    toggleScreenReader,
    toggleKeyboardOnly,
    announce,
    clearAnnouncements,
  };
}; 