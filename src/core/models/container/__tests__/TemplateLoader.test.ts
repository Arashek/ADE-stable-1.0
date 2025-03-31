import { TemplateLoader } from '../TemplateLoader';
import { ContainerTemplate, ProjectType } from '../types';
import * as fs from 'fs';
import * as path from 'path';

jest.mock('fs');
jest.mock('path');

describe('TemplateLoader', () => {
  let templateLoader: TemplateLoader;
  const mockTemplateDir = '/mock/templates';
  const mockTemplate: ContainerTemplate = {
    id: 'test-template',
    name: 'Test Template',
    projectType: ProjectType.WEB,
    baseImage: 'node:18-alpine',
    defaultResources: {
      cpu: { limit: 2, reservation: 1 },
      memory: { limit: '4g', reservation: '2g' },
      disk: { limit: '20g', reservation: '10g' }
    },
    description: 'Test template for unit testing',
    tags: ['test', 'web']
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (path.join as jest.Mock).mockImplementation((...args) => args.join('/'));
    templateLoader = new TemplateLoader(mockTemplateDir);
  });

  describe('loadTemplates', () => {
    it('should load templates from the template directory', async () => {
      const mockFiles = ['template1.yaml', 'template2.yaml'];
      const mockFileContent = JSON.stringify(mockTemplate);

      (fs.promises.readdir as jest.Mock).mockResolvedValue(mockFiles);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(mockFileContent);

      const templates = await templateLoader.loadTemplates();

      expect(fs.promises.readdir).toHaveBeenCalledWith(mockTemplateDir);
      expect(templates).toHaveLength(2);
      expect(templates[0]).toEqual(mockTemplate);
    });

    it('should handle errors when loading templates', async () => {
      const error = new Error('Failed to read directory');
      (fs.promises.readdir as jest.Mock).mockRejectedValue(error);

      await expect(templateLoader.loadTemplates()).rejects.toThrow(error);
    });
  });

  describe('saveTemplate', () => {
    it('should save a template to a file', async () => {
      await templateLoader.saveTemplate(mockTemplate);

      expect(fs.promises.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('test-template.yaml'),
        expect.any(String)
      );
    });

    it('should handle errors when saving templates', async () => {
      const error = new Error('Failed to write file');
      (fs.promises.writeFile as jest.Mock).mockRejectedValue(error);

      await expect(templateLoader.saveTemplate(mockTemplate)).rejects.toThrow(error);
    });
  });

  describe('deleteTemplate', () => {
    it('should delete a template file', async () => {
      // First load the template
      (fs.promises.readdir as jest.Mock).mockResolvedValue(['test-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockTemplate));
      await templateLoader.loadTemplates();

      // Then delete it
      await templateLoader.deleteTemplate(ProjectType.WEB);

      expect(fs.promises.unlink).toHaveBeenCalledWith(
        expect.stringContaining('test-template.yaml')
      );
    });

    it('should handle errors when deleting templates', async () => {
      const error = new Error('Failed to delete file');
      (fs.promises.unlink as jest.Mock).mockRejectedValue(error);

      // First load the template
      (fs.promises.readdir as jest.Mock).mockResolvedValue(['test-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockTemplate));
      await templateLoader.loadTemplates();

      // Then try to delete it
      await expect(templateLoader.deleteTemplate(ProjectType.WEB)).rejects.toThrow(error);
    });
  });

  describe('getTemplate', () => {
    it('should return a template by project type', async () => {
      // First load the template
      (fs.promises.readdir as jest.Mock).mockResolvedValue(['test-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockTemplate));
      await templateLoader.loadTemplates();

      const template = templateLoader.getTemplate(ProjectType.WEB);
      expect(template).toEqual(mockTemplate);
    });

    it('should return undefined for non-existent project type', async () => {
      const template = templateLoader.getTemplate(ProjectType.WEB);
      expect(template).toBeUndefined();
    });
  });

  describe('getAllTemplates', () => {
    it('should return all loaded templates', async () => {
      // First load the template
      (fs.promises.readdir as jest.Mock).mockResolvedValue(['test-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(mockTemplate));
      await templateLoader.loadTemplates();

      const templates = templateLoader.getAllTemplates();
      expect(templates).toHaveLength(1);
      expect(templates[0]).toEqual(mockTemplate);
    });

    it('should return empty array when no templates are loaded', () => {
      const templates = templateLoader.getAllTemplates();
      expect(templates).toHaveLength(0);
    });
  });

  describe('template validation', () => {
    it('should validate required fields', async () => {
      const invalidTemplate = { ...mockTemplate };
      delete invalidTemplate.id;

      (fs.promises.readdir as jest.Mock).mockResolvedValue(['invalid-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(invalidTemplate));

      await expect(templateLoader.loadTemplates()).rejects.toThrow('Template is missing required field: id');
    });

    it('should validate resource limits', async () => {
      const invalidTemplate = {
        ...mockTemplate,
        defaultResources: {
          ...mockTemplate.defaultResources,
          cpu: { limit: -1, reservation: 1 }
        }
      };

      (fs.promises.readdir as jest.Mock).mockResolvedValue(['invalid-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(invalidTemplate));

      await expect(templateLoader.loadTemplates()).rejects.toThrow('CPU limits and reservations must be positive numbers');
    });

    it('should validate memory format', async () => {
      const invalidTemplate = {
        ...mockTemplate,
        defaultResources: {
          ...mockTemplate.defaultResources,
          memory: { limit: 'invalid', reservation: '2g' }
        }
      };

      (fs.promises.readdir as jest.Mock).mockResolvedValue(['invalid-template.yaml']);
      (fs.promises.readFile as jest.Mock).mockResolvedValue(JSON.stringify(invalidTemplate));

      await expect(templateLoader.loadTemplates()).rejects.toThrow('Invalid memory format');
    });
  });
}); 