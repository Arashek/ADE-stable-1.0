import { DesignTemplateService } from '../DesignTemplateService';
import { DatabaseService } from '../../../DatabaseService';
import { FileService } from '../../../FileService';
import { DesignTemplate, DesignPreset } from '../DesignTemplateService';
import {
  DesignCanvas,
  DesignElement,
  DesignStyle,
} from '../../../../frontend/src/services/InteractiveDesignService';

jest.mock('../../../DatabaseService');
jest.mock('../../../FileService');

describe('DesignTemplateService', () => {
  let service: DesignTemplateService;
  let mockDb: jest.Mocked<DatabaseService>;
  let mockFileService: jest.Mocked<FileService>;

  const mockTemplate: DesignTemplate = {
    id: 'template-1',
    name: 'Test Template',
    description: 'A test template',
    category: 'layout',
    thumbnail: 'thumbnail.png',
    elements: [
      {
        id: 'elem-1',
        type: 'component',
        content: 'Test Component',
        position: { x: 100, y: 100 },
        size: { width: 200, height: 100 },
        style: {
          fill: '#ffffff',
          stroke: '#000000',
          strokeWidth: 2,
        },
        properties: {},
      },
    ],
    style: {
      fill: '#ffffff',
      stroke: '#000000',
      strokeWidth: 1,
    },
    metadata: {
      author: 'system',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      tags: ['test', 'layout'],
      version: '1.0.0',
    },
  };

  const mockPreset: DesignPreset = {
    id: 'preset-1',
    name: 'Test Preset',
    description: 'A test preset',
    category: 'style',
    style: {
      fill: '#f0f0f0',
      stroke: '#333333',
      strokeWidth: 3,
      shadow: {
        color: '#000000',
        blur: 10,
        offsetX: 5,
        offsetY: 5,
      },
    },
    metadata: {
      author: 'system',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      tags: ['test', 'style'],
      version: '1.0.0',
    },
  };

  beforeEach(() => {
    mockDb = {
      getTemplates: jest.fn(),
      saveTemplate: jest.fn(),
      deleteTemplate: jest.fn(),
      getPresets: jest.fn(),
      savePreset: jest.fn(),
      deletePreset: jest.fn(),
    } as any;

    mockFileService = {
      saveFile: jest.fn(),
      readFile: jest.fn(),
    } as any;

    service = new DesignTemplateService(mockDb, mockFileService);
  });

  describe('Template methods', () => {
    it('should get a template by id', async () => {
      mockDb.getTemplates.mockResolvedValue([mockTemplate]);

      const template = await service.getTemplate('template-1');
      expect(template).toBeDefined();
      expect(template?.id).toBe('template-1');
    });

    it('should get all templates', async () => {
      mockDb.getTemplates.mockResolvedValue([mockTemplate]);

      const templates = await service.getAllTemplates();
      expect(templates.length).toBe(1);
      expect(templates[0].id).toBe('template-1');
    });

    it('should get templates by category', async () => {
      mockDb.getTemplates.mockResolvedValue([mockTemplate]);

      const templates = await service.getTemplatesByCategory('layout');
      expect(templates.length).toBe(1);
      expect(templates[0].category).toBe('layout');
    });

    it('should create a new template', async () => {
      const newTemplate = {
        name: 'New Template',
        description: 'A new template',
        category: 'layout',
        thumbnail: 'new-thumbnail.png',
        elements: [],
        style: {},
      };

      mockDb.saveTemplate.mockResolvedValue(undefined);

      const created = await service.createTemplate(newTemplate);
      expect(created.id).toBeDefined();
      expect(created.metadata.author).toBe('system');
      expect(mockDb.saveTemplate).toHaveBeenCalled();
    });

    it('should update an existing template', async () => {
      mockDb.getTemplates.mockResolvedValue([mockTemplate]);
      mockDb.saveTemplate.mockResolvedValue(undefined);

      const updates = {
        name: 'Updated Template',
        description: 'Updated description',
      };

      await service.updateTemplate('template-1', updates);
      expect(mockDb.saveTemplate).toHaveBeenCalled();
    });

    it('should delete a template', async () => {
      mockDb.deleteTemplate.mockResolvedValue(undefined);

      await service.deleteTemplate('template-1');
      expect(mockDb.deleteTemplate).toHaveBeenCalledWith('template-1');
    });

    it('should apply a template to a canvas', async () => {
      mockDb.getTemplates.mockResolvedValue([mockTemplate]);

      const canvas: DesignCanvas = {
        id: 'canvas-1',
        name: 'Test Canvas',
        elements: [],
        style: {},
        grid: { enabled: true, size: 20, color: '#e0e0e0' },
        snap: { enabled: true, threshold: 10 },
        zoom: 1,
        pan: { x: 0, y: 0 },
      };

      const updatedCanvas = await service.applyTemplate(canvas, 'template-1');
      expect(updatedCanvas.elements.length).toBe(1);
      expect(updatedCanvas.elements[0].id).not.toBe('elem-1'); // New ID should be generated
    });
  });

  describe('Preset methods', () => {
    it('should get a preset by id', async () => {
      mockDb.getPresets.mockResolvedValue([mockPreset]);

      const preset = await service.getPreset('preset-1');
      expect(preset).toBeDefined();
      expect(preset?.id).toBe('preset-1');
    });

    it('should get all presets', async () => {
      mockDb.getPresets.mockResolvedValue([mockPreset]);

      const presets = await service.getAllPresets();
      expect(presets.length).toBe(1);
      expect(presets[0].id).toBe('preset-1');
    });

    it('should get presets by category', async () => {
      mockDb.getPresets.mockResolvedValue([mockPreset]);

      const presets = await service.getPresetsByCategory('style');
      expect(presets.length).toBe(1);
      expect(presets[0].category).toBe('style');
    });

    it('should create a new preset', async () => {
      const newPreset = {
        name: 'New Preset',
        description: 'A new preset',
        category: 'style',
        style: {},
      };

      mockDb.savePreset.mockResolvedValue(undefined);

      const created = await service.createPreset(newPreset);
      expect(created.id).toBeDefined();
      expect(created.metadata.author).toBe('system');
      expect(mockDb.savePreset).toHaveBeenCalled();
    });

    it('should update an existing preset', async () => {
      mockDb.getPresets.mockResolvedValue([mockPreset]);
      mockDb.savePreset.mockResolvedValue(undefined);

      const updates = {
        name: 'Updated Preset',
        description: 'Updated description',
      };

      await service.updatePreset('preset-1', updates);
      expect(mockDb.savePreset).toHaveBeenCalled();
    });

    it('should delete a preset', async () => {
      mockDb.deletePreset.mockResolvedValue(undefined);

      await service.deletePreset('preset-1');
      expect(mockDb.deletePreset).toHaveBeenCalledWith('preset-1');
    });

    it('should apply a preset to an element', async () => {
      mockDb.getPresets.mockResolvedValue([mockPreset]);

      const element: DesignElement = {
        id: 'elem-1',
        type: 'component',
        content: 'Test Component',
        position: { x: 100, y: 100 },
        size: { width: 200, height: 100 },
        style: {},
        properties: {},
      };

      const updatedElement = await service.applyPreset(element, 'preset-1');
      expect(updatedElement.style).toEqual(mockPreset.style);
    });
  });
}); 