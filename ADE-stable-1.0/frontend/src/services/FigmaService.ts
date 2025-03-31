import { DesignSystem, DesignComponent } from '../types/design';

interface FigmaConfig {
  enabled: boolean;
  token: string;
}

interface FigmaFile {
  key: string;
  name: string;
  lastModified: string;
}

interface FigmaComponent {
  key: string;
  name: string;
  description: string;
  lastModified: string;
}

export class FigmaService {
  private static instance: FigmaService;
  private config: FigmaConfig = { enabled: false, token: '' };
  private baseUrl = 'https://api.figma.com/v1';

  private constructor() {}

  static getInstance(): FigmaService {
    if (!FigmaService.instance) {
      FigmaService.instance = new FigmaService();
    }
    return FigmaService.instance;
  }

  setConfig(config: FigmaConfig) {
    this.config = config;
  }

  isEnabled(): boolean {
    return this.config.enabled && !!this.config.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    if (!this.isEnabled()) {
      throw new Error('Figma integration is not enabled');
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'X-Figma-Token': this.config.token,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Figma API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getFiles(): Promise<FigmaFile[]> {
    if (!this.isEnabled()) return [];
    
    try {
      const response = await this.request<{ files: FigmaFile[] }>('/me/files');
      return response.files;
    } catch (error) {
      console.error('Error fetching Figma files:', error);
      return [];
    }
  }

  async getComponents(fileKey: string): Promise<FigmaComponent[]> {
    if (!this.isEnabled()) return [];
    
    try {
      const response = await this.request<{ components: FigmaComponent[] }>(
        `/files/${fileKey}/components`
      );
      return response.components;
    } catch (error) {
      console.error('Error fetching Figma components:', error);
      return [];
    }
  }

  async importComponent(fileKey: string, componentKey: string): Promise<DesignComponent | null> {
    if (!this.isEnabled()) return null;
    
    try {
      const response = await this.request<{
        component: {
          key: string;
          name: string;
          description: string;
          styles: Record<string, any>;
          properties: Record<string, any>;
        };
      }>(`/files/${fileKey}/components/${componentKey}`);

      // Convert Figma component to our DesignComponent format
      return {
        id: response.component.key,
        type: 'component',
        name: response.component.name,
        description: response.component.description,
        styles: response.component.styles,
        properties: response.component.properties,
      };
    } catch (error) {
      console.error('Error importing Figma component:', error);
      return null;
    }
  }

  async syncComponent(
    design: DesignSystem,
    component: DesignComponent,
    fileKey: string,
    componentKey: string
  ): Promise<boolean> {
    if (!this.isEnabled()) return false;
    
    try {
      // Get latest version from Figma
      const figmaComponent = await this.importComponent(fileKey, componentKey);
      if (!figmaComponent) return false;

      // Update component in design system
      const updatedComponents = design.components?.map(c =>
        c.id === component.id ? figmaComponent : c
      );

      return true;
    } catch (error) {
      console.error('Error syncing Figma component:', error);
      return false;
    }
  }

  async exportToFigma(design: DesignSystem, fileKey: string): Promise<boolean> {
    if (!this.isEnabled()) return false;
    
    try {
      // Convert design system to Figma format
      const figmaData = this.convertDesignToFigma(design);

      // Create or update Figma file
      await this.request(`/files/${fileKey}`, {
        method: 'PUT',
        body: JSON.stringify(figmaData),
      });

      return true;
    } catch (error) {
      console.error('Error exporting to Figma:', error);
      return false;
    }
  }

  private convertDesignToFigma(design: DesignSystem): any {
    // Convert our design system format to Figma's format
    // This is a simplified example - you would need to implement the full conversion
    return {
      name: design.metadata.name,
      components: design.components?.map(component => ({
        key: component.id,
        name: component.name,
        description: component.description,
        styles: component.styles,
        properties: component.properties,
      })),
    };
  }
} 