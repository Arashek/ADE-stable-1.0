import { DesignTool, DesignToolProperty } from '../../../frontend/src/services/InteractiveDesignService';

export class DesignToolService {
  private tools: Map<string, DesignTool> = new Map();

  constructor() {
    this.initializeDefaultTools();
  }

  private initializeDefaultTools() {
    // Shape tools
    this.addTool({
      id: 'rectangle',
      name: 'Rectangle',
      type: 'shape',
      icon: 'rectangle',
      description: 'Draw a rectangle shape',
      properties: [
        {
          id: 'fill',
          name: 'fill',
          type: 'color',
          label: 'Fill Color',
          defaultValue: '#ffffff',
        },
        {
          id: 'stroke',
          name: 'stroke',
          type: 'color',
          label: 'Stroke Color',
          defaultValue: '#000000',
        },
        {
          id: 'strokeWidth',
          name: 'strokeWidth',
          type: 'number',
          label: 'Stroke Width',
          defaultValue: 2,
          min: 0,
          max: 20,
          step: 1,
        },
        {
          id: 'cornerRadius',
          name: 'cornerRadius',
          type: 'number',
          label: 'Corner Radius',
          defaultValue: 0,
          min: 0,
          max: 50,
          step: 1,
        },
      ],
    });

    this.addTool({
      id: 'circle',
      name: 'Circle',
      type: 'shape',
      icon: 'circle',
      description: 'Draw a circle shape',
      properties: [
        {
          id: 'fill',
          name: 'fill',
          type: 'color',
          label: 'Fill Color',
          defaultValue: '#ffffff',
        },
        {
          id: 'stroke',
          name: 'stroke',
          type: 'color',
          label: 'Stroke Color',
          defaultValue: '#000000',
        },
        {
          id: 'strokeWidth',
          name: 'strokeWidth',
          type: 'number',
          label: 'Stroke Width',
          defaultValue: 2,
          min: 0,
          max: 20,
          step: 1,
        },
      ],
    });

    // Text tool
    this.addTool({
      id: 'text',
      name: 'Text',
      type: 'text',
      icon: 'text',
      description: 'Add text to the canvas',
      properties: [
        {
          id: 'fontFamily',
          name: 'fontFamily',
          type: 'select',
          label: 'Font Family',
          defaultValue: 'Arial',
          options: [
            { label: 'Arial', value: 'Arial' },
            { label: 'Times New Roman', value: 'Times New Roman' },
            { label: 'Helvetica', value: 'Helvetica' },
          ],
        },
        {
          id: 'fontSize',
          name: 'fontSize',
          type: 'number',
          label: 'Font Size',
          defaultValue: 16,
          min: 8,
          max: 72,
          step: 1,
        },
        {
          id: 'fontWeight',
          name: 'fontWeight',
          type: 'select',
          label: 'Font Weight',
          defaultValue: 'normal',
          options: [
            { label: 'Normal', value: 'normal' },
            { label: 'Bold', value: 'bold' },
            { label: 'Light', value: 'light' },
          ],
        },
        {
          id: 'color',
          name: 'color',
          type: 'color',
          label: 'Text Color',
          defaultValue: '#000000',
        },
      ],
    });

    // Connection tool
    this.addTool({
      id: 'connection',
      name: 'Connection',
      type: 'connection',
      icon: 'connection',
      description: 'Create connections between elements',
      properties: [
        {
          id: 'stroke',
          name: 'stroke',
          type: 'color',
          label: 'Line Color',
          defaultValue: '#000000',
        },
        {
          id: 'strokeWidth',
          name: 'strokeWidth',
          type: 'number',
          label: 'Line Width',
          defaultValue: 2,
          min: 1,
          max: 10,
          step: 1,
        },
        {
          id: 'lineStyle',
          name: 'lineStyle',
          type: 'select',
          label: 'Line Style',
          defaultValue: 'solid',
          options: [
            { label: 'Solid', value: 'solid' },
            { label: 'Dashed', value: 'dashed' },
            { label: 'Dotted', value: 'dotted' },
          ],
        },
      ],
    });

    // Style tool
    this.addTool({
      id: 'style',
      name: 'Style',
      type: 'style',
      icon: 'style',
      description: 'Apply styles to selected elements',
      properties: [
        {
          id: 'shadow',
          name: 'shadow',
          type: 'boolean',
          label: 'Enable Shadow',
          defaultValue: false,
        },
        {
          id: 'shadowColor',
          name: 'shadowColor',
          type: 'color',
          label: 'Shadow Color',
          defaultValue: '#000000',
        },
        {
          id: 'shadowBlur',
          name: 'shadowBlur',
          type: 'number',
          label: 'Shadow Blur',
          defaultValue: 10,
          min: 0,
          max: 50,
          step: 1,
        },
        {
          id: 'opacity',
          name: 'opacity',
          type: 'slider',
          label: 'Opacity',
          defaultValue: 1,
          min: 0,
          max: 1,
          step: 0.1,
        },
      ],
    });

    // Image tool
    this.addTool({
      id: 'image',
      name: 'Image',
      type: 'media',
      icon: 'image',
      description: 'Add and edit images',
      properties: [
        {
          id: 'opacity',
          name: 'opacity',
          type: 'slider',
          label: 'Opacity',
          defaultValue: 1,
          min: 0,
          max: 1,
          step: 0.1,
        },
        {
          id: 'filter',
          name: 'filter',
          type: 'select',
          label: 'Filter',
          defaultValue: 'none',
          options: [
            { label: 'None', value: 'none' },
            { label: 'Grayscale', value: 'grayscale' },
            { label: 'Sepia', value: 'sepia' },
            { label: 'Blur', value: 'blur' },
            { label: 'Brightness', value: 'brightness' },
          ],
        },
        {
          id: 'filterIntensity',
          name: 'filterIntensity',
          type: 'slider',
          label: 'Filter Intensity',
          defaultValue: 0,
          min: 0,
          max: 1,
          step: 0.1,
        },
      ],
    });

    // Video tool
    this.addTool({
      id: 'video',
      name: 'Video',
      type: 'media',
      icon: 'video',
      description: 'Add and edit videos',
      properties: [
        {
          id: 'autoplay',
          name: 'autoplay',
          type: 'boolean',
          label: 'Autoplay',
          defaultValue: false,
        },
        {
          id: 'loop',
          name: 'loop',
          type: 'boolean',
          label: 'Loop',
          defaultValue: false,
        },
        {
          id: 'muted',
          name: 'muted',
          type: 'boolean',
          label: 'Muted',
          defaultValue: true,
        },
        {
          id: 'controls',
          name: 'controls',
          type: 'boolean',
          label: 'Show Controls',
          defaultValue: true,
        },
      ],
    });

    // Chart tool
    this.addTool({
      id: 'chart',
      name: 'Chart',
      type: 'data',
      icon: 'chart',
      description: 'Create data visualizations',
      properties: [
        {
          id: 'type',
          name: 'type',
          type: 'select',
          label: 'Chart Type',
          defaultValue: 'bar',
          options: [
            { label: 'Bar', value: 'bar' },
            { label: 'Line', value: 'line' },
            { label: 'Pie', value: 'pie' },
            { label: 'Scatter', value: 'scatter' },
          ],
        },
        {
          id: 'theme',
          name: 'theme',
          type: 'select',
          label: 'Theme',
          defaultValue: 'light',
          options: [
            { label: 'Light', value: 'light' },
            { label: 'Dark', value: 'dark' },
            { label: 'Custom', value: 'custom' },
          ],
        },
        {
          id: 'animation',
          name: 'animation',
          type: 'boolean',
          label: 'Enable Animation',
          defaultValue: true,
        },
        {
          id: 'interactive',
          name: 'interactive',
          type: 'boolean',
          label: 'Interactive Mode',
          defaultValue: true,
        },
      ],
    });

    // Table tool
    this.addTool({
      id: 'table',
      name: 'Table',
      type: 'data',
      icon: 'table',
      description: 'Create and edit tables',
      properties: [
        {
          id: 'borders',
          name: 'borders',
          type: 'boolean',
          label: 'Show Borders',
          defaultValue: true,
        },
        {
          id: 'headerStyle',
          name: 'headerStyle',
          type: 'select',
          label: 'Header Style',
          defaultValue: 'bold',
          options: [
            { label: 'Bold', value: 'bold' },
            { label: 'Italic', value: 'italic' },
            { label: 'Underline', value: 'underline' },
          ],
        },
        {
          id: 'stripeRows',
          name: 'stripeRows',
          type: 'boolean',
          label: 'Stripe Rows',
          defaultValue: true,
        },
        {
          id: 'hoverEffect',
          name: 'hoverEffect',
          type: 'boolean',
          label: 'Hover Effect',
          defaultValue: true,
        },
      ],
    });

    // Form tool
    this.addTool({
      id: 'form',
      name: 'Form',
      type: 'interactive',
      icon: 'form',
      description: 'Create interactive forms',
      properties: [
        {
          id: 'layout',
          name: 'layout',
          type: 'select',
          label: 'Layout',
          defaultValue: 'vertical',
          options: [
            { label: 'Vertical', value: 'vertical' },
            { label: 'Horizontal', value: 'horizontal' },
            { label: 'Grid', value: 'grid' },
          ],
        },
        {
          id: 'spacing',
          name: 'spacing',
          type: 'number',
          label: 'Spacing',
          defaultValue: 16,
          min: 8,
          max: 48,
          step: 4,
        },
        {
          id: 'validation',
          name: 'validation',
          type: 'boolean',
          label: 'Enable Validation',
          defaultValue: true,
        },
        {
          id: 'submitButton',
          name: 'submitButton',
          type: 'boolean',
          label: 'Show Submit Button',
          defaultValue: true,
        },
      ],
    });

    // Animation tool
    this.addTool({
      id: 'animation',
      name: 'Animation',
      type: 'interactive',
      icon: 'animation',
      description: 'Add animations to elements',
      properties: [
        {
          id: 'type',
          name: 'type',
          type: 'select',
          label: 'Animation Type',
          defaultValue: 'fade',
          options: [
            { label: 'Fade', value: 'fade' },
            { label: 'Slide', value: 'slide' },
            { label: 'Scale', value: 'scale' },
            { label: 'Rotate', value: 'rotate' },
            { label: 'Bounce', value: 'bounce' },
          ],
        },
        {
          id: 'duration',
          name: 'duration',
          type: 'number',
          label: 'Duration (ms)',
          defaultValue: 500,
          min: 100,
          max: 5000,
          step: 100,
        },
        {
          id: 'delay',
          name: 'delay',
          type: 'number',
          label: 'Delay (ms)',
          defaultValue: 0,
          min: 0,
          max: 5000,
          step: 100,
        },
        {
          id: 'repeat',
          name: 'repeat',
          type: 'select',
          label: 'Repeat',
          defaultValue: 'none',
          options: [
            { label: 'None', value: 'none' },
            { label: 'Once', value: 'once' },
            { label: 'Infinite', value: 'infinite' },
          ],
        },
      ],
    });
  }

  addTool(tool: DesignTool): void {
    this.tools.set(tool.id, tool);
  }

  getTool(id: string): DesignTool | undefined {
    return this.tools.get(id);
  }

  getAllTools(): DesignTool[] {
    return Array.from(this.tools.values());
  }

  getToolsByType(type: DesignTool['type']): DesignTool[] {
    return this.getAllTools().filter(tool => tool.type === type);
  }

  updateTool(id: string, updates: Partial<DesignTool>): void {
    const tool = this.tools.get(id);
    if (tool) {
      this.tools.set(id, { ...tool, ...updates });
    }
  }

  removeTool(id: string): void {
    this.tools.delete(id);
  }

  validateToolProperties(toolId: string, properties: Record<string, any>): boolean {
    const tool = this.tools.get(toolId);
    if (!tool) return false;

    return tool.properties.every(prop => {
      const value = properties[prop.id];
      if (value === undefined) return true; // Optional properties

      switch (prop.type) {
        case 'color':
          return /^#[0-9A-Fa-f]{6}$/.test(value);
        case 'number':
          return typeof value === 'number' &&
            (!prop.min || value >= prop.min) &&
            (!prop.max || value <= prop.max);
        case 'boolean':
          return typeof value === 'boolean';
        case 'select':
          return prop.options?.some(opt => opt.value === value);
        case 'slider':
          return typeof value === 'number' &&
            value >= 0 &&
            value <= 1;
        default:
          return true;
      }
    });
  }

  getDefaultProperties(toolId: string): Record<string, any> {
    const tool = this.tools.get(toolId);
    if (!tool) return {};

    return tool.properties.reduce((acc, prop) => {
      acc[prop.id] = prop.defaultValue;
      return acc;
    }, {} as Record<string, any>);
  }
} 