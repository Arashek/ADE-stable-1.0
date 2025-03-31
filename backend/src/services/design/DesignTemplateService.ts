import { DatabaseService } from '../../DatabaseService';
import { FileService } from '../../FileService';
import {
  DesignCanvas,
  DesignElement,
  DesignStyle,
} from '../../../frontend/src/services/InteractiveDesignService';

export interface DesignTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail: string;
  elements: DesignElement[];
  style: DesignStyle;
  metadata: {
    author: string;
    createdAt: string;
    updatedAt: string;
    tags: string[];
    version: string;
  };
}

export interface DesignPreset {
  id: string;
  name: string;
  description: string;
  category: string;
  style: DesignStyle;
  metadata: {
    author: string;
    createdAt: string;
    updatedAt: string;
    tags: string[];
    version: string;
  };
}

export class DesignTemplateService {
  private templates: Map<string, DesignTemplate> = new Map();
  private presets: Map<string, DesignPreset> = new Map();

  constructor(
    private db: DatabaseService,
    private fileService: FileService
  ) {
    this.initializeDefaultTemplates();
    this.initializeDefaultPresets();
  }

  private async initializeDefaultTemplates() {
    // Load default templates from database
    const defaultTemplates = await this.db.getTemplates();
    defaultTemplates.forEach(template => {
      this.templates.set(template.id, template);
    });
  }

  private async initializeDefaultPresets() {
    // Load default presets from database
    const defaultPresets = await this.db.getPresets();
    defaultPresets.forEach(preset => {
      this.presets.set(preset.id, preset);
    });
  }

  // Template methods
  async getTemplate(id: string): Promise<DesignTemplate | undefined> {
    return this.templates.get(id);
  }

  async getAllTemplates(): Promise<DesignTemplate[]> {
    return Array.from(this.templates.values());
  }

  async getTemplatesByCategory(category: string): Promise<DesignTemplate[]> {
    return this.getAllTemplates().filter(template => template.category === category);
  }

  async createTemplate(template: Omit<DesignTemplate, 'id' | 'metadata'>): Promise<DesignTemplate> {
    const newTemplate: DesignTemplate = {
      ...template,
      id: this.generateId(),
      metadata: {
        author: 'system',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: [],
        version: '1.0.0',
      },
    };

    this.templates.set(newTemplate.id, newTemplate);
    await this.db.saveTemplate(newTemplate);
    return newTemplate;
  }

  async updateTemplate(id: string, updates: Partial<DesignTemplate>): Promise<void> {
    const template = this.templates.get(id);
    if (template) {
      const updatedTemplate: DesignTemplate = {
        ...template,
        ...updates,
        metadata: {
          ...template.metadata,
          updatedAt: new Date().toISOString(),
        },
      };

      this.templates.set(id, updatedTemplate);
      await this.db.saveTemplate(updatedTemplate);
    }
  }

  async deleteTemplate(id: string): Promise<void> {
    this.templates.delete(id);
    await this.db.deleteTemplate(id);
  }

  async applyTemplate(canvas: DesignCanvas, templateId: string): Promise<DesignCanvas> {
    const template = await this.getTemplate(templateId);
    if (!template) {
      throw new Error('Template not found');
    }

    const newElements = template.elements.map(element => ({
      ...element,
      id: this.generateId(),
    }));

    return {
      ...canvas,
      elements: [...canvas.elements, ...newElements],
      style: {
        ...canvas.style,
        ...template.style,
      },
    };
  }

  // Preset methods
  async getPreset(id: string): Promise<DesignPreset | undefined> {
    return this.presets.get(id);
  }

  async getAllPresets(): Promise<DesignPreset[]> {
    return Array.from(this.presets.values());
  }

  async getPresetsByCategory(category: string): Promise<DesignPreset[]> {
    return this.getAllPresets().filter(preset => preset.category === category);
  }

  async createPreset(preset: Omit<DesignPreset, 'id' | 'metadata'>): Promise<DesignPreset> {
    const newPreset: DesignPreset = {
      ...preset,
      id: this.generateId(),
      metadata: {
        author: 'system',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        tags: [],
        version: '1.0.0',
      },
    };

    this.presets.set(newPreset.id, newPreset);
    await this.db.savePreset(newPreset);
    return newPreset;
  }

  async updatePreset(id: string, updates: Partial<DesignPreset>): Promise<void> {
    const preset = this.presets.get(id);
    if (preset) {
      const updatedPreset: DesignPreset = {
        ...preset,
        ...updates,
        metadata: {
          ...preset.metadata,
          updatedAt: new Date().toISOString(),
        },
      };

      this.presets.set(id, updatedPreset);
      await this.db.savePreset(updatedPreset);
    }
  }

  async deletePreset(id: string): Promise<void> {
    this.presets.delete(id);
    await this.db.deletePreset(id);
  }

  async applyPreset(element: DesignElement, presetId: string): Promise<DesignElement> {
    const preset = await this.getPreset(presetId);
    if (!preset) {
      throw new Error('Preset not found');
    }

    return {
      ...element,
      style: {
        ...element.style,
        ...preset.style,
      },
    };
  }

  // Utility methods
  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
} 