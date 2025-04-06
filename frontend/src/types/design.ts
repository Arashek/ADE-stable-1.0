/**
 * Simplified design types for the ADE platform
 * Focused on core functionality needed for the multi-agent architecture
 * and local testing before cloud deployment
 */

export interface DesignComponent {
  id: string;
  name: string;
  type: string;
  properties: Record<string, any>;
  styles: Record<string, string>;
  pageId?: string;
  parentId?: string;
  children?: string[];
}

export interface DesignStyle {
  id: string;
  name: string;
  type: 'FILL' | 'TEXT' | 'EFFECT' | 'GRID';
  value: string;
  scope: 'global' | 'page' | 'component';
  targetId?: string;
}

export interface DesignPage {
  id: string;
  name: string;
  path: string;
  components: string[];
  styles: string[];
  layout: {
    type: string;
    properties: Record<string, any>;
  };
}

export interface DesignTheme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    error: string;
    text: string;
    textSecondary: string;
    [key: string]: string;
  };
  typography: {
    fontFamily: string;
    fontSize: number;
    [key: string]: any;
  };
  spacing: {
    unit: number;
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    [key: string]: number;
  };
}

export interface DesignSystem {
  id: string;
  name: string;
  components: DesignComponent[];
  styles: DesignStyle[];
  pages: DesignPage[];
  theme: DesignTheme;
  version: string;
  currentPage?: string;
}

export interface DesignSuggestion {
  id: string;
  type: 'component' | 'style' | 'layout' | 'theme';
  description: string;
  priority: 'high' | 'medium' | 'low';
  component?: DesignComponent;
  preview?: string;
}

export interface DesignFeedback {
  suggestions: DesignSuggestion[];
  score: number;
  analysis?: {
    accessibility: number;
    consistency: number;
    usability: number;
    responsiveness: number;
  };
}

export interface DesignRequest {
  type: 'component' | 'page' | 'theme' | 'system';
  requirements: string;
  constraints?: string[];
  examples?: string[];
  target?: string;
}

export interface DesignResponse {
  type: 'component' | 'page' | 'theme' | 'system';
  design: Partial<DesignSystem>;
  explanation: string;
  alternatives?: Partial<DesignSystem>[];
}

// Component prop interfaces for type checking
export interface DesignCanvasProps {
  currentDesign: DesignSystem;
  currentPage: string;
  onUpdateComponent: (componentId: string, updates: Partial<DesignComponent>) => void;
  onAddComponent: (component: DesignComponent) => void;
  onSelectComponent: (componentId: string | null) => void;
  onDeleteComponent: (componentId: string) => void;
}

export interface ComponentLibraryProps {
  components: DesignComponent[];
  onAdd: (component: DesignComponent) => void;
  onUpdate: (componentId: string, updates: Partial<DesignComponent>) => void;
  onSelect: (componentId: string | null) => void;
}

export interface StyleGuideProps {
  theme: DesignTheme;
  onUpdate: (theme: DesignTheme) => void;
}

export interface DesignPreviewProps {
  currentDesign: DesignSystem;
  device?: 'desktop' | 'tablet' | 'mobile';
  onClose: () => void;
}

export interface DesignSystemConfigProps {
  currentDesign: DesignSystem;
  onUpdateDesign: (updatedDesign: Partial<DesignSystem>) => void;
}