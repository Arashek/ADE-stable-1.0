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
    styles: string[];
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
  components: DesignComponent[];
  styles: DesignStyle[];
  pages: DesignPage[];
  implementation: DesignImplementation;
  metadata: DesignMetadata;
  currentPage?: string;
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