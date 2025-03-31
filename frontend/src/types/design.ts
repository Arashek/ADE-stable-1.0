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

export interface DesignImplementation {
  components: {
    id: string;
    code: string;
    dependencies: string[];
  }[];
  styles: {
    id: string;
    code: string;
    dependencies: string[];
  }[];
  pages: {
    id: string;
    code: string;
    dependencies: string[];
  }[];
  layout: {
    type: string;
    components: string[];
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
    h1: Partial<{
      fontSize: string;
      fontWeight: number;
      lineHeight: number;
      letterSpacing: string;
    }>;
    h2: Partial<{
      fontSize: string;
      fontWeight: number;
      lineHeight: number;
      letterSpacing: string;
    }>;
    h3: Partial<{
      fontSize: string;
      fontWeight: number;
      lineHeight: number;
      letterSpacing: string;
    }>;
    body: Partial<{
      fontSize: string;
      fontWeight: number;
      lineHeight: number;
      letterSpacing: string;
    }>;
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
  borderRadius: {
    sm: number;
    md: number;
    lg: number;
    [key: string]: number;
  };
  breakpoints?: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    [key: string]: number;
  };
  shadows?: string[];
  transitions?: {
    duration: {
      short: number;
      standard: number;
      complex: number;
      [key: string]: number;
    };
    easing: {
      easeIn: string;
      easeOut: string;
      easeInOut: string;
      [key: string]: string;
    };
  };
}

export interface DesignMetadata {
  name: string;
  description?: string;
  version: string;
  lastModified: string;
  createdBy: string;
  zoom?: number;
  showGrid?: boolean;
  snapToGrid?: boolean;
  gridSize?: number;
  snapThreshold?: number;
  exportWithComments?: boolean;
  exportWithStyles?: boolean;
  integrations?: {
    figma?: {
      enabled: boolean;
      token: string;
    };
  };
}

export interface DesignSystem {
  id: string;
  name: string;
  components: DesignComponent[];
  styles: DesignStyle[];
  pages: DesignPage[];
  implementation: DesignImplementation;
  metadata: DesignMetadata;
  currentPage?: string;
  theme: DesignTheme;
  version: string;
}

export interface DesignValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: Array<{
    type: 'component' | 'style' | 'layout' | 'accessibility';
    message: string;
    priority: 'high' | 'medium' | 'low';
  }>;
}

export interface DesignModification {
  type: 'add' | 'update' | 'remove' | 'move';
  target: 'component' | 'style' | 'page' | 'layout';
  id: string;
  changes: Record<string, any>;
  context?: {
    pageId?: string;
    parentId?: string;
    position?: number;
  };
}

export interface DesignSuggestion {
  id: string;
  type: 'component' | 'style' | 'layout' | 'theme';
  description: string;
  priority: 'high' | 'medium' | 'low';
  component?: DesignComponent;
  styles?: Partial<DesignTheme>;
  layout?: any;
  preview?: string;
}

export interface DesignFeedback {
  suggestions: DesignSuggestion[];
  validations: DesignValidationResult;
  score: number;
  analysis: {
    accessibility: number;
    consistency: number;
    usability: number;
    responsiveness: number;
  };
}

export interface DesignNotification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: Date;
  source: 'user' | 'agent' | 'system';
  read: boolean;
  action?: {
    label: string;
    handler: () => void;
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

export interface DesignChatProps {
  designAgent: any;
  currentDesign: DesignSystem;
  onUpdateDesign: (updatedDesign: Partial<DesignSystem>) => void;
  onApplySuggestion: (suggestion: DesignSuggestion) => void;
}

export interface DesignPreviewProps {
  currentDesign: DesignSystem;
  device?: 'desktop' | 'tablet' | 'mobile';
  onClose: () => void;
}

export interface DesignSuggestionsPanelProps {
  suggestions: DesignSuggestion[];
  onApplySuggestion: (suggestion: DesignSuggestion) => void;
  onDismiss: () => void;
}

export interface DesignSystemConfigProps {
  currentDesign: DesignSystem;
  onUpdateDesign: (updatedDesign: Partial<DesignSystem>) => void;
}